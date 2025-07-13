"""
Counselor Service for Managing Review Queue and Approvals

This service handles the counselor workflow for reviewing AI responses,
managing the queue, and tracking counselor actions.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlmodel import Session, select, and_, or_

from app.models import (
    AISoulEntity,
    ChatMessage,
    Counselor,
    CounselorAction,
    Organization,
    PendingResponse,
    RiskAssessment,
    User,
)

logger = logging.getLogger(__name__)


class CounselorService:
    """Service for managing counselor review queue and approvals."""

    def __init__(self, session: Session):
        self.session = session

    async def create_pending_response(
        self,
        chat_message_id: str,
        risk_assessment_id: str,
        user_id: str,
        ai_soul_id: str,
        original_message: str,
        ai_response: str,
        organization_id: str | None = None,
        priority: str = "normal"
    ) -> PendingResponse:
        """
        Create a new pending response for counselor review.
        """
        try:
            # Determine priority based on risk level
            risk_assessment = self.session.get(RiskAssessment, risk_assessment_id)
            if risk_assessment:
                if risk_assessment.risk_level == "critical":
                    priority = "urgent"
                elif risk_assessment.risk_level == "high":
                    priority = "high"
            
            # Set response time limit based on priority
            response_time_limit = None
            if priority == "urgent":
                response_time_limit = datetime.utcnow() + timedelta(minutes=15)
            elif priority == "high":
                response_time_limit = datetime.utcnow() + timedelta(hours=1)
            elif priority == "normal":
                response_time_limit = datetime.utcnow() + timedelta(hours=4)
            
            # Assign to available counselor
            assigned_counselor = await self._assign_counselor(organization_id, priority)
            
            pending_response = PendingResponse(
                chat_message_id=chat_message_id,
                risk_assessment_id=risk_assessment_id,
                user_id=user_id,
                ai_soul_id=ai_soul_id,
                organization_id=organization_id,
                original_user_message=original_message,
                ai_generated_response=ai_response,
                priority=priority,
                assigned_counselor_id=assigned_counselor.id if assigned_counselor else None,
                response_time_limit=response_time_limit
            )
            
            self.session.add(pending_response)
            self.session.commit()
            self.session.refresh(pending_response)
            
            logger.info(
                f"Created pending response {pending_response.id} for user {user_id} "
                f"with priority {priority}"
            )
            
            # TODO: Send notification to assigned counselor
            if assigned_counselor:
                await self._notify_counselor(assigned_counselor, pending_response)
            
            return pending_response
            
        except Exception as e:
            logger.error(f"Error creating pending response: {str(e)}")
            self.session.rollback()
            raise

    async def get_counselor_queue(
        self,
        counselor_id: str,
        status: str = "pending",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get pending responses assigned to a specific counselor.
        """
        try:
            statement = (
                select(PendingResponse)
                .where(
                    and_(
                        PendingResponse.assigned_counselor_id == counselor_id,
                        PendingResponse.status == status
                    )
                )
                .order_by(
                    PendingResponse.priority.desc(),  # Urgent first
                    PendingResponse.created_at.asc()   # Oldest first within priority
                )
                .limit(limit)
            )
            
            pending_responses = self.session.exec(statement).all()
            
            # Enrich with additional data
            enriched_queue = []
            for response in pending_responses:
                # Get related data
                user = self.session.get(User, response.user_id)
                ai_soul = self.session.get(AISoulEntity, response.ai_soul_id)
                risk_assessment = self.session.get(RiskAssessment, response.risk_assessment_id)
                
                # Calculate time remaining
                time_remaining = None
                if response.response_time_limit:
                    remaining = response.response_time_limit - datetime.utcnow()
                    time_remaining = max(0, int(remaining.total_seconds()))
                
                enriched_item = {
                    "id": str(response.id),
                    "user_name": user.full_name if user else "Unknown",
                    "user_email": user.email if user else "Unknown",
                    "ai_soul_name": ai_soul.name if ai_soul else "Unknown",
                    "original_user_message": response.original_user_message,
                    "ai_generated_response": response.ai_generated_response,
                    "priority": response.priority,
                    "created_at": response.created_at,
                    "time_remaining_seconds": time_remaining,
                    "risk_level": risk_assessment.risk_level if risk_assessment else "unknown",
                    "risk_categories": json.loads(risk_assessment.risk_categories) if risk_assessment else [],
                    "risk_reasoning": risk_assessment.reasoning if risk_assessment else "",
                    "status": response.status
                }
                enriched_queue.append(enriched_item)
            
            return enriched_queue
            
        except Exception as e:
            logger.error(f"Error getting counselor queue: {str(e)}")
            return []

    async def get_admin_queue(
        self,
        organization_id: str | None = None,
        status: str = "pending",
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get all pending responses for admin users with the same data structure as counselor queue.
        This ensures frontend compatibility.
        """
        try:
            statement = select(PendingResponse).where(
                PendingResponse.status == status
            )
            
            if organization_id:
                statement = statement.where(PendingResponse.organization_id == organization_id)
            
            statement = statement.order_by(
                PendingResponse.priority.desc(),  # Urgent first
                PendingResponse.created_at.asc()   # Oldest first within priority
            ).limit(limit)
            
            pending_responses = self.session.exec(statement).all()
            
            # Use the same enriched format as counselor queue for consistency
            enriched_queue = []
            for response in pending_responses:
                # Get related data
                user = self.session.get(User, response.user_id)
                ai_soul = self.session.get(AISoulEntity, response.ai_soul_id)
                risk_assessment = self.session.get(RiskAssessment, response.risk_assessment_id)
                assigned_counselor = self.session.get(Counselor, response.assigned_counselor_id) if response.assigned_counselor_id else None
                
                # Calculate time remaining
                time_remaining = None
                if response.response_time_limit:
                    remaining = response.response_time_limit - datetime.utcnow()
                    time_remaining = max(0, int(remaining.total_seconds()))
                
                enriched_item = {
                    "id": str(response.id),
                    "user_name": user.full_name if user else "Unknown",
                    "user_email": user.email if user else "Unknown",
                    "ai_soul_name": ai_soul.name if ai_soul else "Unknown",
                    "original_user_message": response.original_user_message,
                    "ai_generated_response": response.ai_generated_response,
                    "priority": response.priority,
                    "created_at": response.created_at,
                    "time_remaining_seconds": time_remaining,
                    "risk_level": risk_assessment.risk_level if risk_assessment else "unknown",
                    "risk_categories": json.loads(risk_assessment.risk_categories) if risk_assessment else [],
                    "risk_reasoning": risk_assessment.reasoning if risk_assessment else "",
                    "status": response.status,
                    "assigned_counselor": assigned_counselor.user.full_name if assigned_counselor and assigned_counselor.user else "Unassigned"
                }
                enriched_queue.append(enriched_item)
            
            return enriched_queue
            
        except Exception as e:
            logger.error(f"Error getting admin queue: {str(e)}")
            return []

    async def approve_response(
        self,
        pending_response_id: str,
        counselor_id: str | None,
        notes: str | None = None
    ) -> Dict[str, Any]:
        """
        Approve an AI response without modifications.
        """
        try:
            pending_response = self.session.get(PendingResponse, pending_response_id)
            if not pending_response:
                raise ValueError("Pending response not found")
            
            # Update pending response
            pending_response.status = "approved"
            pending_response.reviewed_at = datetime.utcnow()
            pending_response.counselor_notes = notes
            
            # Log counselor action only if we have a valid counselor_id
            if counselor_id:
                import uuid
                action = CounselorAction(
                    counselor_id=uuid.UUID(counselor_id),
                    pending_response_id=uuid.UUID(pending_response_id),
                    user_id=pending_response.user_id,
                    organization_id=pending_response.organization_id,
                    action_type="approved",
                    original_response=pending_response.ai_generated_response,
                    final_response=pending_response.ai_generated_response,
                    reason=notes,
                    time_taken_seconds=self._calculate_review_time(pending_response)
                )
                
                self.session.add(action)
            
            self.session.commit()
            
            # Send the approved response to the user
            await self._send_response_to_user(
                pending_response, 
                pending_response.ai_generated_response
            )
            
            logger.info(f"Response {pending_response_id} approved by counselor {counselor_id}")
            
            return {
                "status": "approved",
                "response_sent": True,
                "final_response": pending_response.ai_generated_response
            }
            
        except Exception as e:
            logger.error(f"Error approving response: {str(e)}")
            self.session.rollback()
            raise

    async def modify_response(
        self,
        pending_response_id: str,
        counselor_id: str | None,
        modified_response: str,
        notes: str | None = None
    ) -> Dict[str, Any]:
        """
        Modify an AI response before sending to user.
        """
        try:
            pending_response = self.session.get(PendingResponse, pending_response_id)
            if not pending_response:
                raise ValueError("Pending response not found")
            
            # Update pending response
            pending_response.status = "modified"
            pending_response.reviewed_at = datetime.utcnow()
            pending_response.modified_response = modified_response
            pending_response.counselor_notes = notes
            
            # Log counselor action only if we have a valid counselor_id
            if counselor_id:
                import uuid
                action = CounselorAction(
                    counselor_id=uuid.UUID(counselor_id),
                    pending_response_id=uuid.UUID(pending_response_id),
                    user_id=pending_response.user_id,
                    organization_id=pending_response.organization_id,
                    action_type="modified",
                    original_response=pending_response.ai_generated_response,
                    final_response=modified_response,
                    reason=notes,
                    time_taken_seconds=self._calculate_review_time(pending_response)
                )
                
                self.session.add(action)
            
            self.session.commit()
            
            # Send the modified response to the user
            await self._send_response_to_user(pending_response, modified_response)
            
            logger.info(f"Response {pending_response_id} modified by counselor {counselor_id}")
            
            return {
                "status": "modified",
                "response_sent": True,
                "final_response": modified_response
            }
            
        except Exception as e:
            logger.error(f"Error modifying response: {str(e)}")
            self.session.rollback()
            raise

    async def reject_response(
        self,
        pending_response_id: str,
        counselor_id: str | None,
        replacement_response: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Reject an AI response and provide a replacement.
        """
        try:
            pending_response = self.session.get(PendingResponse, pending_response_id)
            if not pending_response:
                raise ValueError("Pending response not found")
            
            # Update pending response
            pending_response.status = "rejected"
            pending_response.reviewed_at = datetime.utcnow()
            pending_response.modified_response = replacement_response
            pending_response.counselor_notes = reason
            
            # Log counselor action only if we have a valid counselor_id
            if counselor_id:
                import uuid
                action = CounselorAction(
                    counselor_id=uuid.UUID(counselor_id),
                    pending_response_id=uuid.UUID(pending_response_id),
                    user_id=pending_response.user_id,
                    organization_id=pending_response.organization_id,
                    action_type="rejected",
                    original_response=pending_response.ai_generated_response,
                    final_response=replacement_response,
                    reason=reason,
                    time_taken_seconds=self._calculate_review_time(pending_response)
                )
                
                self.session.add(action)
            
            self.session.commit()
            
            # Send the replacement response to the user
            await self._send_response_to_user(pending_response, replacement_response)
            
            logger.info(f"Response {pending_response_id} rejected by counselor {counselor_id}")
            
            return {
                "status": "rejected",
                "response_sent": True,
                "final_response": replacement_response
            }
            
        except Exception as e:
            logger.error(f"Error rejecting response: {str(e)}")
            self.session.rollback()
            raise

    async def escalate_case(
        self,
        pending_response_id: str,
        counselor_id: str,
        escalation_reason: str,
        target_counselor_id: str | None = None
    ) -> Dict[str, Any]:
        """
        Escalate a case to another counselor or supervisor.
        """
        try:
            pending_response = self.session.get(PendingResponse, pending_response_id)
            if not pending_response:
                raise ValueError("Pending response not found")
            
            # Find target counselor (supervisor or specialist)
            if not target_counselor_id:
                target_counselor = await self._find_supervisor(
                    pending_response.organization_id
                )
                target_counselor_id = target_counselor.id if target_counselor else None
            
            if not target_counselor_id:
                raise ValueError("No available counselor for escalation")
            
            # Update pending response
            pending_response.assigned_counselor_id = target_counselor_id
            pending_response.priority = "urgent"  # Escalated cases are urgent
            pending_response.counselor_notes = f"Escalated: {escalation_reason}"
            
            # Log counselor action
            import uuid
            action = CounselorAction(
                counselor_id=uuid.UUID(counselor_id),
                pending_response_id=uuid.UUID(pending_response_id),
                user_id=pending_response.user_id,
                organization_id=pending_response.organization_id,
                action_type="escalated",
                original_response=pending_response.ai_generated_response,
                final_response=None,
                reason=escalation_reason,
                time_taken_seconds=self._calculate_review_time(pending_response)
            )
            
            self.session.add(action)
            self.session.commit()
            
            # Notify target counselor
            target_counselor = self.session.get(Counselor, target_counselor_id)
            if target_counselor:
                await self._notify_counselor(target_counselor, pending_response, is_escalation=True)
            
            logger.info(
                f"Case {pending_response_id} escalated by counselor {counselor_id} "
                f"to counselor {target_counselor_id}"
            )
            
            return {
                "status": "escalated",
                "assigned_to": target_counselor_id,
                "priority": "urgent"
            }
            
        except Exception as e:
            logger.error(f"Error escalating case: {str(e)}")
            self.session.rollback()
            raise

    async def get_organization_queue(
        self,
        organization_id: str,
        status: str = "pending",
        priority: str | None = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get all pending responses for an organization.
        """
        try:
            statement = select(PendingResponse).where(
                and_(
                    PendingResponse.organization_id == organization_id,
                    PendingResponse.status == status
                )
            )
            
            if priority:
                statement = statement.where(PendingResponse.priority == priority)
            
            statement = statement.order_by(
                PendingResponse.priority.desc(),
                PendingResponse.created_at.asc()
            ).limit(limit)
            
            pending_responses = self.session.exec(statement).all()
            
            # Enrich with additional data
            enriched_queue = []
            for response in pending_responses:
                user = self.session.get(User, response.user_id)
                ai_soul = self.session.get(AISoulEntity, response.ai_soul_id)
                counselor = self.session.get(Counselor, response.assigned_counselor_id) if response.assigned_counselor_id else None
                risk_assessment = self.session.get(RiskAssessment, response.risk_assessment_id)
                
                enriched_item = {
                    "id": str(response.id),
                    "user_name": user.full_name if user else "Unknown",
                    "ai_soul_name": ai_soul.name if ai_soul else "Unknown",
                    "assigned_counselor": counselor.user.full_name if counselor and counselor.user else "Unassigned",
                    "priority": response.priority,
                    "status": response.status,
                    "created_at": response.created_at,
                    "risk_level": risk_assessment.risk_level if risk_assessment else "unknown",
                    "time_in_queue_minutes": int((datetime.utcnow() - response.created_at).total_seconds() / 60)
                }
                enriched_queue.append(enriched_item)
            
            return enriched_queue
            
        except Exception as e:
            logger.error(f"Error getting organization queue: {str(e)}")
            return []

    async def get_counselor_performance(
        self,
        counselor_id: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get performance metrics for a counselor.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get counselor actions
            statement = (
                select(CounselorAction)
                .where(
                    and_(
                        CounselorAction.counselor_id == counselor_id,
                        CounselorAction.created_at >= cutoff_date
                    )
                )
            )
            actions = self.session.exec(statement).all()
            
            # Calculate metrics
            total_cases = len(actions)
            approvals = len([a for a in actions if a.action_type == "approved"])
            modifications = len([a for a in actions if a.action_type == "modified"])
            rejections = len([a for a in actions if a.action_type == "rejected"])
            escalations = len([a for a in actions if a.action_type == "escalated"])
            
            # Average review time
            review_times = [a.time_taken_seconds for a in actions if a.time_taken_seconds]
            avg_review_time = sum(review_times) / len(review_times) if review_times else 0
            
            # Get current queue size
            current_queue = await self.get_counselor_queue(counselor_id, "pending")
            
            return {
                "counselor_id": counselor_id,
                "period_days": days,
                "total_cases_reviewed": total_cases,
                "approvals": approvals,
                "modifications": modifications,
                "rejections": rejections,
                "escalations": escalations,
                "approval_rate": approvals / total_cases if total_cases > 0 else 0,
                "average_review_time_seconds": int(avg_review_time),
                "current_queue_size": len(current_queue),
                "cases_per_day": total_cases / days if days > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting counselor performance: {str(e)}")
            return {}

    async def get_organization_performance(
        self,
        organization_id: str | None = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get organization-wide performance metrics for admin users.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Get all counselor actions for the organization
            statement = select(CounselorAction).where(
                CounselorAction.created_at >= cutoff_date
            )
            
            if organization_id:
                statement = statement.where(CounselorAction.organization_id == organization_id)
            
            actions = self.session.exec(statement).all()
            
            # Calculate organization-wide metrics
            total_cases = len(actions)
            approvals = len([a for a in actions if a.action_type == "approved"])
            modifications = len([a for a in actions if a.action_type == "modified"])
            rejections = len([a for a in actions if a.action_type == "rejected"])
            escalations = len([a for a in actions if a.action_type == "escalated"])
            
            # Average review time across all counselors
            review_times = [a.time_taken_seconds for a in actions if a.time_taken_seconds]
            avg_review_time = sum(review_times) / len(review_times) if review_times else 0
            
            # Get current organization-wide queue size
            current_queue = await self.get_organization_queue(
                organization_id=organization_id,
                status="pending"
            )
            
            return {
                "counselor_id": "organization-wide",
                "period_days": days,
                "total_cases_reviewed": total_cases,
                "approvals": approvals,
                "modifications": modifications,
                "rejections": rejections,
                "escalations": escalations,
                "approval_rate": approvals / total_cases if total_cases > 0 else 0,
                "average_review_time_seconds": int(avg_review_time),
                "current_queue_size": len(current_queue),
                "cases_per_day": total_cases / days if days > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Error getting organization performance: {str(e)}")
            return {
                "counselor_id": "organization-wide",
                "period_days": days,
                "total_cases_reviewed": 0,
                "approvals": 0,
                "modifications": 0,
                "rejections": 0,
                "escalations": 0,
                "approval_rate": 0,
                "average_review_time_seconds": 0,
                "current_queue_size": 0,
                "cases_per_day": 0
            }

    async def _assign_counselor(
        self,
        organization_id: str | None,
        priority: str
    ) -> Optional[Counselor]:
        """
        Assign an available counselor based on workload and specialization.
        """
        try:
            # Get available counselors for the organization
            statement = select(Counselor).where(
                and_(
                    Counselor.organization_id == organization_id,
                    Counselor.is_available == True
                )
            )
            counselors = self.session.exec(statement).all()
            
            if not counselors:
                return None
            
            # Find counselor with lowest current workload
            best_counselor = None
            min_workload = float('inf')
            
            for counselor in counselors:
                # Count current pending cases
                current_cases = self.session.exec(
                    select(PendingResponse).where(
                        and_(
                            PendingResponse.assigned_counselor_id == counselor.id,
                            PendingResponse.status == "pending"
                        )
                    )
                ).all()
                
                workload = len(current_cases)
                
                # Skip if at max capacity
                if workload >= counselor.max_concurrent_cases:
                    continue
                
                # Prefer counselors with lower workload
                if workload < min_workload:
                    min_workload = workload
                    best_counselor = counselor
            
            return best_counselor
            
        except Exception as e:
            logger.error(f"Error assigning counselor: {str(e)}")
            return None

    async def _find_supervisor(self, organization_id: str | None) -> Optional[Counselor]:
        """
        Find a supervisor counselor for escalation.
        """
        # For now, find any available counselor
        # In the future, this could check for specific supervisor roles
        return await self._assign_counselor(organization_id, "urgent")

    def _calculate_review_time(self, pending_response: PendingResponse) -> int:
        """
        Calculate how long the review took in seconds.
        """
        if not pending_response.created_at:
            return 0
        
        review_time = datetime.utcnow() - pending_response.created_at
        return int(review_time.total_seconds())

    async def _send_response_to_user(
        self,
        pending_response: PendingResponse,
        final_response: str
    ) -> None:
        """
        Send the final approved/modified response to the user.
        """
        try:
            # Create the AI response message in the chat
            ai_message = ChatMessage(
                content=final_response,
                user_id=pending_response.user_id,
                ai_soul_id=pending_response.ai_soul_id,
                is_from_user=False
            )
            
            self.session.add(ai_message)
            self.session.commit()
            
            logger.info(
                f"Approved response sent to user {pending_response.user_id} "
                f"for pending response {pending_response.id} - this replaces temporary review message"
            )
            
        except Exception as e:
            logger.error(f"Error sending response to user: {str(e)}")
            raise

    async def _notify_counselor(
        self,
        counselor: Counselor,
        pending_response: PendingResponse,
        is_escalation: bool = False
    ) -> None:
        """
        Send notification to counselor about new case.
        """
        try:
            # TODO: Implement notification system (email, push, websocket)
            # For now, just log
            notification_type = "escalation" if is_escalation else "new_case"
            logger.info(
                f"Notification sent to counselor {counselor.id} "
                f"for {notification_type}: {pending_response.id}"
            )
            
        except Exception as e:
            logger.error(f"Error notifying counselor: {str(e)}")

    async def auto_approve_expired_responses(self) -> int:
        """
        Auto-approve responses that have exceeded their time limit.
        """
        try:
            # Find expired pending responses
            statement = (
                select(PendingResponse)
                .where(
                    and_(
                        PendingResponse.status == "pending",
                        PendingResponse.response_time_limit < datetime.utcnow()
                    )
                )
            )
            expired_responses = self.session.exec(statement).all()
            
            auto_approved_count = 0
            
            for response in expired_responses:
                # Auto-approve with system note
                response.status = "approved"
                response.reviewed_at = datetime.utcnow()
                response.counselor_notes = "Auto-approved due to time limit expiration"
                
                # Send original AI response
                await self._send_response_to_user(response, response.ai_generated_response)
                
                auto_approved_count += 1
            
            if auto_approved_count > 0:
                self.session.commit()
                logger.info(f"Auto-approved {auto_approved_count} expired responses")
            
            return auto_approved_count
            
        except Exception as e:
            logger.error(f"Error auto-approving expired responses: {str(e)}")
            return 0 