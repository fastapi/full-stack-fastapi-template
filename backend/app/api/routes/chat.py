from uuid import UUID
import uuid
from datetime import datetime
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, SQLModel

logger = logging.getLogger(__name__)

from app.api.deps import (
    CurrentActiveUser,
    SessionDep,
)
from app.models import (
    AISoulEntity,
    ChatMessage,
    ChatMessageCreate,
    ChatMessagePublic,
    User,
    UserAISoulInteraction,
)
from app.services.ai_soul_service import AISoulService
from app.services.content_filter_service import ContentFilterService
from app.services.risk_assessment_service import RiskAssessmentService
from app.services.counselor_service import CounselorService

router = APIRouter()


class ChatMessagePairResponse(SQLModel):
    """Response model for chat message creation containing both user and AI messages"""
    user_message: ChatMessagePublic
    ai_message: ChatMessagePublic

@router.post("/{ai_soul_id}/messages", response_model=ChatMessagePairResponse)
async def create_chat_message(
    *,
    db: SessionDep,
    current_user: CurrentActiveUser,
    ai_soul_id: UUID,
    message_in: ChatMessageCreate,
) -> ChatMessagePairResponse:
    """
    Create a new chat message and get AI response with counselor override system.
    Any user can chat with any AI soul.
    Returns both user message and AI response to prevent message stacking.
    """
    # Verify AI soul exists
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    # Check if user has any pending messages under review for this AI soul
    from app.models import PendingResponse
    pending_statement = (
        select(PendingResponse)
        .where(
            PendingResponse.user_id == current_user.id,
            PendingResponse.ai_soul_id == ai_soul_id,
            PendingResponse.status == "pending"
        )
    )
    pending_responses = db.exec(pending_statement).all()
    
    if pending_responses:
        raise HTTPException(
            status_code=429, 
            detail="You have messages under review. Please wait for counselor approval before sending new messages."
        )

    # Analyze content for safety and risk assessment
    content_filter = ContentFilterService()
    content_analysis = await content_filter.analyze_content(message_in.content)
    
    # Only block content that is truly inappropriate (not crisis-related)
    # Crisis-related content should go through risk assessment and counselor review
    if (content_analysis.get("flagged") and 
        "sexual" in content_analysis.get("categories", []) and 
        content_analysis.get("severity") in ["high", "critical"]):
        raise HTTPException(
            status_code=400,
            detail="Message content violates content safety guidelines",
        )

    # Save user message
    user_message = ChatMessage(
        content=message_in.content,
        user_id=current_user.id,
        ai_soul_id=ai_soul_id,
        is_from_user=True,
    )
    db.add(user_message)
    
    # Increment global interaction count for this AI soul
    ai_soul.interaction_count += 1
    db.add(ai_soul)
    
    # Update user-specific interaction tracking
    user_interaction = db.exec(
        select(UserAISoulInteraction).where(
            UserAISoulInteraction.user_id == current_user.id,
            UserAISoulInteraction.ai_soul_id == ai_soul_id
        )
    ).first()
    
    if user_interaction:
        user_interaction.interaction_count += 1
        user_interaction.last_interaction = datetime.utcnow()
        user_interaction.updated_at = datetime.utcnow()
    else:
        user_interaction = UserAISoulInteraction(
            user_id=current_user.id,
            ai_soul_id=ai_soul_id,
            interaction_count=1,
            last_interaction=datetime.utcnow()
        )
        db.add(user_interaction)
    
    db.commit()
    db.refresh(user_message)

    # Perform risk assessment on user message
    risk_service = RiskAssessmentService()
    risk_assessment = await risk_service.assess_message_risk(
        session=db,
        user_message=message_in.content,
        user_id=str(current_user.id),
        ai_soul_id=str(ai_soul_id),
        chat_message_id=str(user_message.id),
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        content_analysis=content_analysis
    )
    
    # Debug logging for risk assessment
    logger.info(f"Risk assessment for message '{message_in.content}': {risk_assessment}")

    # Check if counselor review is required - if so, block all responses until approved
    if risk_assessment.get("requires_human_review", False):
        logger.info(f"Message requires human review - creating temporary response")
        
        # Create pending response for counselor review first
        counselor_service = CounselorService(db)
        
        # Generate AI response for counselor review but don't send to user
        ai_service = AISoulService()
        ai_response = await ai_service.generate_ai_response(
            db,
            str(current_user.id),
            str(ai_soul_id),
            message_in.content,
            risk_assessment
        )
        
        # Create pending response for counselor review - no message sent to user yet
        pending_response = await counselor_service.create_pending_response(
            chat_message_id=str(user_message.id),
            risk_assessment_id=risk_assessment["assessment_id"],
            user_id=str(current_user.id),
            ai_soul_id=str(ai_soul_id),
            original_message=message_in.content,
            ai_response=ai_response,  # AI response for counselor to review
            organization_id=str(current_user.organization_id) if current_user.organization_id else None
        )
        
        # Return user message with a temporary AI response indicating review is in progress
        # This message is NOT saved to database - it's just for UI feedback
        review_message = "Your message is being reviewed by a specialist. You will receive a response shortly."
        
        # Add crisis resources if needed
        crisis_resources = risk_assessment.get("crisis_resources", [])
        if crisis_resources:
            review_message += "\n\n⚠️ If you need immediate assistance:\n" + "\n".join(crisis_resources)
        
        return ChatMessagePairResponse(
            user_message=ChatMessagePublic(
                id=user_message.id,
                content=user_message.content,
                user_id=user_message.user_id,
                ai_soul_id=user_message.ai_soul_id,
                is_from_user=user_message.is_from_user,
                timestamp=user_message.timestamp,
                is_temporary=False
            ),
            ai_message=ChatMessagePublic(
                id=uuid.uuid4(),  # Generate temporary UUID - this message is not saved to database
                content=review_message,
                user_id=user_message.user_id,
                ai_soul_id=user_message.ai_soul_id,
                is_from_user=False,
                timestamp=user_message.timestamp,
                is_temporary=True  # Mark as temporary
            )
        )
    
    # If no review required or low risk, generate and send AI response immediately
    ai_service = AISoulService()
    ai_response = await ai_service.generate_ai_response(
        db,
        str(current_user.id),
        str(ai_soul_id),
        message_in.content,
        risk_assessment
    )
    
    ai_message = ChatMessage(
        content=ai_response,
        user_id=current_user.id,
        ai_soul_id=ai_soul_id,
        is_from_user=False,
    )
    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    # Return both messages to prevent stacking
    return ChatMessagePairResponse(
        user_message=ChatMessagePublic(
            id=user_message.id,
            content=user_message.content,
            user_id=user_message.user_id,
            ai_soul_id=user_message.ai_soul_id,
            is_from_user=user_message.is_from_user,
            timestamp=user_message.timestamp,
            is_temporary=False
        ),
        ai_message=ChatMessagePublic(
            id=ai_message.id,
            content=ai_message.content,
            user_id=ai_message.user_id,
            ai_soul_id=ai_message.ai_soul_id,
            is_from_user=ai_message.is_from_user,
            timestamp=ai_message.timestamp,
            is_temporary=False
        )
    )


@router.get("/{ai_soul_id}/messages", response_model=list[ChatMessagePublic])
def get_chat_messages(
    *,
    db: SessionDep,
    current_user: CurrentActiveUser,
    ai_soul_id: UUID,
    skip: int = 0,
    limit: int = 100,
) -> list[ChatMessagePublic]:
    """
    Get chat messages for a specific AI soul.
    Users can only see their own chat messages.
    Messages are returned in ascending order (oldest first).
    """
    # Verify AI soul exists
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    statement = (
        select(ChatMessage)
        .where(
            ChatMessage.user_id == current_user.id,
            ChatMessage.ai_soul_id == ai_soul_id,
        )
        .order_by(ChatMessage.timestamp.asc())
        .offset(skip)
        .limit(limit)
    )
    messages = db.exec(statement).all()
    
    # Convert to ChatMessagePublic with is_temporary=False for all saved messages
    return [
        ChatMessagePublic(
            id=msg.id,
            content=msg.content,
            user_id=msg.user_id,
            ai_soul_id=msg.ai_soul_id,
            is_from_user=msg.is_from_user,
            timestamp=msg.timestamp,
            is_temporary=False  # All saved messages are not temporary
        )
        for msg in messages
    ]


@router.delete("/{ai_soul_id}/messages")
def delete_chat_messages(
    *,
    db: SessionDep,
    current_user: CurrentActiveUser,
    ai_soul_id: UUID,
) -> None:
    """
    Delete all chat messages for a specific AI soul.
    Users can only delete their own chat messages.
    """
    # Verify AI soul exists
    ai_soul = db.get(AISoulEntity, ai_soul_id)
    if not ai_soul:
        raise HTTPException(status_code=404, detail="AI Soul Entity not found")

    statement = (
        select(ChatMessage)
        .where(
            ChatMessage.user_id == current_user.id,
            ChatMessage.ai_soul_id == ai_soul_id,
        )
    )
    messages = db.exec(statement).all()
    for message in messages:
        db.delete(message)
    db.commit()
