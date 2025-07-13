"""
Counselor API Routes for Review Queue and Approval System

These routes handle counselor workflows including:
- Review queue management
- Response approvals, modifications, and rejections
- Case escalation
- Performance analytics
"""

from typing import Any, Dict, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlmodel import Session, select

from app.api.deps import (
    CurrentCounselorOrAdmin,
    SessionDep,
)
from app.models import (
    Counselor,
    CounselorAction,
    Organization,
    PendingResponse,
    RiskAssessment,
    User,
)
from app.services.counselor_service import CounselorService
from app.services.risk_assessment_service import RiskAssessmentService

router = APIRouter()


# Pydantic models for request/response
class ApproveResponseRequest(BaseModel):
    notes: str | None = None


class ModifyResponseRequest(BaseModel):
    modified_response: str
    notes: str | None = None


class RejectResponseRequest(BaseModel):
    replacement_response: str
    reason: str


class EscalateRequestRequest(BaseModel):
    escalation_reason: str
    target_counselor_id: str | None = None


class CounselorQueueResponse(BaseModel):
    queue_items: List[Dict[str, Any]]
    total_count: int
    urgent_count: int
    high_priority_count: int


class PerformanceMetricsResponse(BaseModel):
    counselor_id: str
    period_days: int
    total_cases_reviewed: int
    approvals: int
    modifications: int
    rejections: int
    escalations: int
    approval_rate: float
    average_review_time_seconds: int
    current_queue_size: int
    cases_per_day: float


@router.get("/queue", response_model=CounselorQueueResponse)
async def get_counselor_queue(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    status: str = Query(default="pending", description="Status filter"),
    limit: int = Query(default=50, le=100, description="Maximum number of items")
) -> CounselorQueueResponse:
    """
    Get the review queue for the current counselor.
    """
    # Get counselor record
    counselor = db.exec(
        select(Counselor).where(Counselor.user_id == current_user.id)
    ).first()
    
    counselor_service = CounselorService(db)
    
    # For admin users, get all pending responses in organization-wide view
    # but with the same data structure as counselor queue for frontend consistency
    if not counselor and current_user.is_superuser:
        queue_items = await counselor_service.get_admin_queue(
            organization_id=str(current_user.organization_id) if current_user.organization_id else None,
            status=status,
            limit=limit
        )
    else:
        queue_items = await counselor_service.get_counselor_queue(
            counselor_id=str(counselor.id) if counselor else None,
            status=status,
            limit=limit
        )
    
    # Calculate priority counts
    urgent_count = len([item for item in queue_items if item.get("priority") == "urgent"])
    high_priority_count = len([item for item in queue_items if item.get("priority") == "high"])
    
    return CounselorQueueResponse(
        queue_items=queue_items,
        total_count=len(queue_items),
        urgent_count=urgent_count,
        high_priority_count=high_priority_count
    )


@router.get("/organization-queue")
async def get_organization_queue(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    status: str = Query(default="pending", description="Status filter"),
    priority: str | None = Query(default=None, description="Priority filter"),
    limit: int = Query(default=100, le=200, description="Maximum number of items")
) -> Dict[str, Any]:
    """
    Get the organization-wide review queue (admin/supervisor only).
    """
    counselor_service = CounselorService(db)
    queue_items = await counselor_service.get_organization_queue(
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        status=status,
        priority=priority,
        limit=limit
    )
    
    return {
        "queue_items": queue_items,
        "total_count": len(queue_items),
        "filters": {
            "status": status,
            "priority": priority
        }
    }


@router.post("/{pending_response_id}/approve")
async def approve_response(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    pending_response_id: UUID,
    request: ApproveResponseRequest
) -> Dict[str, Any]:
    """
    Approve an AI response without modifications.
    """
    # Get counselor record (this should exist due to CurrentCounselorOrAdmin dependency)
    counselor = db.exec(
        select(Counselor).where(Counselor.user_id == current_user.id)
    ).first()
    
    # Verify pending response exists
    pending_response = db.get(PendingResponse, pending_response_id)
    if not pending_response:
        raise HTTPException(
            status_code=404, 
            detail=f"Pending response {pending_response_id} not found"
        )
    
    # Check assignment (admins can approve any response)
    if not current_user.is_superuser and counselor:
        if pending_response.assigned_counselor_id != counselor.id:
            raise HTTPException(
                status_code=403,
                detail="This response is assigned to another counselor. You can only approve responses assigned to you."
            )
    
    try:
        counselor_service = CounselorService(db)
        result = await counselor_service.approve_response(
            pending_response_id=str(pending_response_id),
            counselor_id=str(counselor.id) if counselor else None,
            notes=request.notes
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to approve response: {str(e)}"
        )


@router.post("/{pending_response_id}/modify")
async def modify_response(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    pending_response_id: UUID,
    request: ModifyResponseRequest
) -> Dict[str, Any]:
    """
    Modify an AI response before sending to user.
    """
    # Get counselor record (this should exist due to CurrentCounselorOrAdmin dependency)
    counselor = db.exec(
        select(Counselor).where(Counselor.user_id == current_user.id)
    ).first()
    
    # This should not happen due to our improved dependency, but let's be safe
    if not counselor and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Counselor profile not found. Please contact administrator."
        )
    
    # Verify pending response exists
    pending_response = db.get(PendingResponse, pending_response_id)
    if not pending_response:
        raise HTTPException(
            status_code=404, 
            detail=f"Pending response {pending_response_id} not found"
        )
    
    # Check assignment (admins can modify any response)
    if not current_user.is_superuser and counselor:
        if pending_response.assigned_counselor_id != counselor.id:
            raise HTTPException(
                status_code=403,
                detail=f"This response is assigned to another counselor. You can only modify responses assigned to you."
            )
    
    # Validate request
    if not request.modified_response or not request.modified_response.strip():
        raise HTTPException(
            status_code=400,
            detail="Modified response cannot be empty"
        )
    
    try:
        counselor_service = CounselorService(db)
        result = await counselor_service.modify_response(
            pending_response_id=str(pending_response_id),
            counselor_id=str(counselor.id) if counselor else None,
            modified_response=request.modified_response.strip(),
            notes=request.notes
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify response: {str(e)}"
        )


@router.post("/{pending_response_id}/reject")
async def reject_response(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    pending_response_id: UUID,
    request: RejectResponseRequest
) -> Dict[str, Any]:
    """
    Reject an AI response and provide a replacement.
    """
    # Get counselor record (this should exist due to CurrentCounselorOrAdmin dependency)
    counselor = db.exec(
        select(Counselor).where(Counselor.user_id == current_user.id)
    ).first()
    
    # This should not happen due to our improved dependency, but let's be safe
    if not counselor and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Counselor profile not found. Please contact administrator."
        )
    
    # Verify pending response exists
    pending_response = db.get(PendingResponse, pending_response_id)
    if not pending_response:
        raise HTTPException(
            status_code=404, 
            detail=f"Pending response {pending_response_id} not found"
        )
    
    # Check assignment (admins can reject any response)
    if not current_user.is_superuser and counselor:
        if pending_response.assigned_counselor_id != counselor.id:
            raise HTTPException(
                status_code=403,
                detail="This response is assigned to another counselor. You can only reject responses assigned to you."
            )
    
    # Validate request
    if not request.replacement_response or not request.replacement_response.strip():
        raise HTTPException(
            status_code=400,
            detail="Replacement response cannot be empty"
        )
    
    if not request.reason or not request.reason.strip():
        raise HTTPException(
            status_code=400,
            detail="Rejection reason cannot be empty"
        )
    
    try:
        counselor_service = CounselorService(db)
        result = await counselor_service.reject_response(
            pending_response_id=str(pending_response_id),
            counselor_id=str(counselor.id) if counselor else None,
            replacement_response=request.replacement_response.strip(),
            reason=request.reason.strip()
        )
        
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to reject response: {str(e)}"
        )


@router.post("/{pending_response_id}/escalate")
async def escalate_case(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    pending_response_id: UUID,
    request: EscalateRequestRequest
) -> Dict[str, Any]:
    """
    Escalate a case to another counselor or supervisor.
    """
    # Verify counselor permissions
    counselor = db.exec(
        select(Counselor).where(Counselor.user_id == current_user.id)
    ).first()
    
    if not counselor:
        raise HTTPException(
            status_code=403,
            detail="Only counselors can escalate cases"
        )
    
    # Verify pending response
    pending_response = db.get(PendingResponse, pending_response_id)
    if not pending_response:
        raise HTTPException(status_code=404, detail="Pending response not found")
    
    if pending_response.assigned_counselor_id != counselor.id:
        raise HTTPException(
            status_code=403,
            detail="You can only escalate cases assigned to you"
        )
    
    counselor_service = CounselorService(db)
    result = await counselor_service.escalate_case(
        pending_response_id=str(pending_response_id),
        counselor_id=str(counselor.id),
        escalation_reason=request.escalation_reason,
        target_counselor_id=request.target_counselor_id
    )
    
    return result


@router.get("/performance", response_model=PerformanceMetricsResponse)
async def get_counselor_performance(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    days: int = Query(default=30, le=365, description="Number of days to analyze")
) -> PerformanceMetricsResponse:
    """
    Get performance metrics for the current counselor.
    """
    # Get counselor record
    counselor = db.exec(
        select(Counselor).where(Counselor.user_id == current_user.id)
    ).first()
    
    # If no counselor record but user is admin, allow access with organization-wide metrics
    if not counselor and not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="Only counselors and administrators can view performance metrics"
        )
    
    counselor_service = CounselorService(db)
    
    # If admin without counselor record, get organization-wide metrics
    if not counselor and current_user.is_superuser:
        # For admin users, provide organization-wide performance metrics
        metrics = await counselor_service.get_organization_performance(
            organization_id=str(current_user.organization_id) if current_user.organization_id else None,
            days=days
        )
    else:
        metrics = await counselor_service.get_counselor_performance(
            counselor_id=str(counselor.id),
            days=days
        )
    
    return PerformanceMetricsResponse(**metrics)


@router.get("/risk-assessments")
async def get_recent_risk_assessments(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    days: int = Query(default=7, le=30, description="Number of days to look back"),
    limit: int = Query(default=50, le=100, description="Maximum number of assessments")
) -> Dict[str, Any]:
    """
    Get recent risk assessments for monitoring (counselor/admin only).
    """
    # Check permissions
    if not current_user.is_superuser and current_user.role not in ["admin", "counselor"]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view risk assessments"
        )
    
    risk_service = RiskAssessmentService()
    assessments = await risk_service.get_recent_risk_assessments(
        session=db,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        days=days,
        limit=limit
    )
    
    # Convert to serializable format
    assessment_data = []
    for assessment in assessments:
        assessment_data.append({
            "id": str(assessment.id),
            "risk_level": assessment.risk_level,
            "risk_categories": assessment.risk_categories,
            "confidence_score": assessment.confidence_score,
            "reasoning": assessment.reasoning,
            "requires_human_review": assessment.requires_human_review,
            "auto_response_blocked": assessment.auto_response_blocked,
            "assessed_at": assessment.assessed_at,
            "user_id": str(assessment.user_id),
            "ai_soul_id": str(assessment.ai_soul_id)
        })
    
    return {
        "assessments": assessment_data,
        "total_count": len(assessment_data),
        "period_days": days
    }


@router.get("/high-risk-conversations")
async def get_high_risk_conversations(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    hours: int = Query(default=24, le=168, description="Number of hours to look back")
) -> Dict[str, Any]:
    """
    Get conversations with high risk assessments for immediate attention.
    """
    # Check permissions
    if not current_user.is_superuser and current_user.role not in ["admin", "counselor"]:
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions to view high-risk conversations"
        )
    
    risk_service = RiskAssessmentService()
    conversations = await risk_service.get_high_risk_conversations(
        session=db,
        organization_id=str(current_user.organization_id) if current_user.organization_id else None,
        hours=hours
    )
    
    return {
        "conversations": conversations,
        "total_count": len(conversations),
        "period_hours": hours
    }


@router.post("/auto-approve-expired")
async def auto_approve_expired_responses(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin
) -> Dict[str, Any]:
    """
    Manually trigger auto-approval of expired responses (admin only).
    """
    # Check admin permissions
    if not current_user.is_superuser and current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    
    counselor_service = CounselorService(db)
    approved_count = await counselor_service.auto_approve_expired_responses()
    
    return {
        "message": f"Auto-approved {approved_count} expired responses",
        "approved_count": approved_count
    }


@router.get("/counselors")
async def list_counselors(
    *,
    db: SessionDep,
    current_user: CurrentCounselorOrAdmin,
    organization_id: UUID | None = Query(default=None, description="Filter by organization")
) -> Dict[str, Any]:
    """
    List all counselors (admin only).
    """
    # Check admin permissions
    if not current_user.is_superuser and current_user.role not in ["admin"]:
        raise HTTPException(
            status_code=403,
            detail="Admin privileges required"
        )
    
    statement = select(Counselor)
    
    if organization_id:
        statement = statement.where(Counselor.organization_id == organization_id)
    elif current_user.organization_id:
        statement = statement.where(Counselor.organization_id == current_user.organization_id)
    
    counselors = db.exec(statement).all()
    
    counselor_data = []
    for counselor in counselors:
        user = db.get(User, counselor.user_id)
        counselor_data.append({
            "id": str(counselor.id),
            "user_id": str(counselor.user_id),
            "user_name": user.full_name if user else "Unknown",
            "user_email": user.email if user else "Unknown",
            "specializations": counselor.specializations,
            "license_number": counselor.license_number,
            "license_type": counselor.license_type,
            "is_available": counselor.is_available,
            "max_concurrent_cases": counselor.max_concurrent_cases,
            "created_at": counselor.created_at
        })
    
    return {
        "counselors": counselor_data,
        "total_count": len(counselor_data)
    } 