"""
Risk Assessment Service for AI Counselor Override System

This service analyzes user messages for potential risks and determines
whether human counselor intervention is required.
"""

import json
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List

from openai import OpenAI
from sqlmodel import Session, select

from app.core.config import settings
from app.models import (
    AISoulEntity,
    ChatMessage,
    Organization,
    RiskAssessment,
    User,
)
from app.services.cohere_service import CohereService

logger = logging.getLogger(__name__)


class RiskAssessmentService:
    """Service for assessing risk levels in user conversations using AI-powered analysis."""
    
    def __init__(self):
        # Initialize Cohere service for intelligent risk assessment
        self.cohere_service = CohereService()
        
        # Keep OpenAI for backward compatibility with existing AI analysis method
        if settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        else:
            self.client = None
            logger.warning("OpenAI API key not configured - AI analysis will be limited")
        
        # Crisis resources (moved from hardcoded keywords to centralized location)
        self.crisis_resources = {
            "suicide": [
                "🆘 National Suicide Prevention Lifeline: 988 or 1-800-273-8255",
                "🆘 Crisis Text Line: Text HOME to 741741",
                "🆘 If you're in immediate danger, call 911"
            ],
            "self_harm": [
                "🆘 Self-Injury Outreach & Support: 1-800-366-8288",
                "🆘 Crisis Text Line: Text HOME to 741741",
                "🆘 If you're in immediate danger, call 911"
            ],
            "violence": [
                "🆘 National Domestic Violence Hotline: 1-800-799-7233",
                "🆘 If you're in immediate danger, call 911",
                "🆘 Crisis Text Line: Text HOME to 741741"
            ],
            "substance_abuse": [
                "🆘 SAMHSA National Helpline: 1-800-662-HELP (4357)",
                "🆘 Crisis Text Line: Text HOME to 741741"
            ],
            "abuse": [
                "🆘 National Domestic Violence Hotline: 1-800-799-7233",
                "🆘 Childhelp National Child Abuse Hotline: 1-800-422-4453",
                "🆘 If you're in immediate danger, call 911"
            ],
            "mental_health_crisis": [
                "🆘 National Suicide Prevention Lifeline: 988",
                "🆘 Crisis Text Line: Text HOME to 741741",
                "🆘 NAMI Helpline: 1-800-950-NAMI (6264)"
            ],
            "general_crisis": [
                "🆘 National Suicide Prevention Lifeline: 988",
                "🆘 Crisis Text Line: Text HOME to 741741",
                "🆘 If you're in immediate danger, call 911"
            ]
        }

    async def assess_message_risk(
        self, 
        session: Session, 
        user_message: str, 
        user_id: str, 
        ai_soul_id: str, 
        chat_message_id: str,
        organization_id: str | None = None,
        content_analysis: Dict[str, Any] | None = None
    ) -> Dict[str, Any]:
        """
        Assess the risk level of a user message using AI-powered analysis.
        
        Returns:
            Dict containing risk assessment results
        """
        try:
            # Get conversation context for better analysis
            context = await self._get_conversation_context(session, user_id, ai_soul_id)
            
            # Use Cohere LLM for intelligent risk assessment
            logger.info(f"Using Cohere LLM for risk assessment of message from user {user_id}")
            cohere_assessment = await self.cohere_service.assess_risk(
                content=user_message,
                context=context,
                analysis_type="crisis_detection"
            )
            
            # Convert Cohere response to our expected format
            assessment_result = {
                "risk_level": cohere_assessment.risk_level,
                "risk_categories": cohere_assessment.risk_categories,
                "confidence_score": cohere_assessment.confidence_score,
                "reasoning": cohere_assessment.reasoning,
                "requires_human_review": cohere_assessment.requires_human_review,
                "auto_response_blocked": cohere_assessment.auto_response_blocked,
                "crisis_resources": self._get_crisis_resources_for_categories(cohere_assessment.risk_categories)
            }
            
            # If content analysis is provided, combine insights
            if content_analysis and content_analysis.get("flagged"):
                content_assessment = self._convert_content_analysis_to_risk_assessment(content_analysis)
                
                # Use the higher risk level between LLM and content analysis
                if self._get_risk_level_priority(content_assessment["risk_level"]) > self._get_risk_level_priority(assessment_result["risk_level"]):
                    logger.info("Content analysis detected higher risk than LLM - using content analysis result")
                    assessment_result = content_assessment
                else:
                    logger.info("LLM assessment maintained as primary result")
            
            # Save assessment to database
            risk_assessment = await self._save_risk_assessment(
                session=session,
                chat_message_id=chat_message_id,
                user_id=user_id,
                ai_soul_id=ai_soul_id,
                organization_id=organization_id,
                assessment_result=assessment_result
            )
            
            # Add database ID to result
            assessment_result["assessment_id"] = str(risk_assessment.id)
            
            logger.info(
                f"AI-powered risk assessment completed for user {user_id}: "
                f"Level={assessment_result['risk_level']}, "
                f"Requires review={assessment_result['requires_human_review']}, "
                f"Auto blocked={assessment_result['auto_response_blocked']}, "
                f"Confidence={assessment_result['confidence_score']:.2f}"
            )
            
            return assessment_result
            
        except Exception as e:
            logger.error(f"Error in AI-powered risk assessment: {str(e)}")
            # Return safe default - require human review on error
            return {
                "risk_level": "high",
                "risk_categories": ["system_error"],
                "confidence_score": 0.0,
                "reasoning": f"Risk assessment failed: {str(e)}",
                "requires_human_review": True,
                "auto_response_blocked": True,
                "crisis_resources": self._get_crisis_resources()
            }

    def _get_crisis_resources_for_categories(self, risk_categories: List[str]) -> List[str]:
        """
        Get appropriate crisis resources based on risk categories.
        """
        resources = []
        
        for category in risk_categories:
            if category in self.crisis_resources:
                resources.extend(self.crisis_resources[category])
        
        # If no specific resources found, use general crisis resources
        if not resources and risk_categories:
            resources = self.crisis_resources.get("general_crisis", [])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_resources = []
        for resource in resources:
            if resource not in seen:
                seen.add(resource)
                unique_resources.append(resource)
        
        return unique_resources

    async def _ai_risk_analysis(
        self, 
        message: str, 
        user_id: str, 
        ai_soul_id: str, 
        session: Session
    ) -> Dict[str, Any]:
        """
        Use AI to perform more nuanced risk analysis.
        """
        try:
            # Get conversation context for better analysis
            context = await self._get_conversation_context(session, user_id, ai_soul_id)
            
            # Build analysis prompt
            system_prompt = """You are a professional risk assessment AI designed to evaluate mental health and safety risks in user messages. 

Your task is to analyze the user's message and conversation context to determine:
1. Risk level: low, medium, high, or critical
2. Risk categories: suicide, self_harm, violence, substance_abuse, abuse, mental_health_crisis, relationship_crisis, financial_crisis
3. Confidence score: 0.0 to 1.0
4. Whether human counselor review is required
5. Whether AI response should be blocked until review

Guidelines:
- CRITICAL: Immediate suicide/self-harm intent, specific plans, imminent danger
- HIGH: Strong indicators of crisis, distress, or harmful thoughts without immediate intent
- MEDIUM: Concerning patterns, mild distress indicators, potential risk factors
- LOW: Normal conversation, no significant risk indicators

Be conservative - err on the side of safety. When in doubt, recommend human review.

Respond with valid JSON only."""

            user_prompt = f"""
Analyze this message for risk:

Message: "{message}"

Context: {context}

Provide assessment as JSON with keys: risk_level, risk_categories, confidence_score, reasoning, requires_human_review, auto_response_blocked
"""

            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent risk assessment
            )
            
            # Parse AI response
            ai_result = json.loads(response.choices[0].message.content.strip())
            
            # Validate and enhance result
            validated_result = self._validate_ai_assessment(ai_result)
            
            # Add crisis resources if needed
            if validated_result["requires_human_review"]:
                validated_result["crisis_resources"] = self._get_crisis_resources()
            else:
                validated_result["crisis_resources"] = []
            
            return validated_result
            
        except Exception as e:
            logger.error(f"AI risk analysis failed: {str(e)}")
            # Fallback to keyword-based screening
            return self._quick_risk_screening(message)

    def _validate_ai_assessment(self, ai_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and sanitize AI assessment results.
        """
        # Ensure required fields exist with defaults
        validated = {
            "risk_level": ai_result.get("risk_level", "medium"),
            "risk_categories": ai_result.get("risk_categories", []),
            "confidence_score": float(ai_result.get("confidence_score", 0.5)),
            "reasoning": ai_result.get("reasoning", "AI analysis completed"),
            "requires_human_review": bool(ai_result.get("requires_human_review", False)),
            "auto_response_blocked": bool(ai_result.get("auto_response_blocked", False))
        }
        
        # Validate risk level
        if validated["risk_level"] not in ["low", "medium", "high", "critical"]:
            validated["risk_level"] = "medium"
        
        # Validate confidence score
        validated["confidence_score"] = max(0.0, min(1.0, validated["confidence_score"]))
        
        # Ensure critical/high risk requires review
        if validated["risk_level"] in ["critical", "high"]:
            validated["requires_human_review"] = True
        
        # Critical risk should block auto response
        if validated["risk_level"] == "critical":
            validated["auto_response_blocked"] = True
        
        return validated

    async def _get_conversation_context(
        self, 
        session: Session, 
        user_id: str, 
        ai_soul_id: str
    ) -> str:
        """
        Get recent conversation context for risk analysis.
        """
        try:
            # Get recent messages
            statement = (
                select(ChatMessage)
                .where(
                    ChatMessage.user_id == user_id,
                    ChatMessage.ai_soul_id == ai_soul_id
                )
                .order_by(ChatMessage.timestamp.desc())
                .limit(5)
            )
            messages = session.exec(statement).all()
            
            if not messages:
                return "No previous conversation context available."
            
            context_parts = []
            for msg in reversed(messages):  # Show chronological order
                role = "User" if msg.is_from_user else "AI"
                context_parts.append(f"{role}: {msg.content[:200]}...")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.error(f"Error getting conversation context: {str(e)}")
            return "Context unavailable due to error."

    async def _save_risk_assessment(
        self,
        session: Session,
        chat_message_id: str,
        user_id: str,
        ai_soul_id: str,
        organization_id: str | None,
        assessment_result: Dict[str, Any]
    ) -> RiskAssessment:
        """
        Save risk assessment to database.
        """
        risk_assessment = RiskAssessment(
            chat_message_id=chat_message_id,
            user_id=user_id,
            ai_soul_id=ai_soul_id,
            organization_id=organization_id,
            risk_level=assessment_result["risk_level"],
            risk_categories=json.dumps(assessment_result["risk_categories"]),
            confidence_score=assessment_result["confidence_score"],
            reasoning=assessment_result["reasoning"],
            requires_human_review=assessment_result["requires_human_review"],
            auto_response_blocked=assessment_result["auto_response_blocked"]
        )
        
        session.add(risk_assessment)
        session.commit()
        session.refresh(risk_assessment)
        
        return risk_assessment

    def _convert_content_analysis_to_risk_assessment(self, content_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Convert content filter analysis to risk assessment format."""
        # Map content filter categories to risk assessment categories
        category_mapping = {
            "self_harm": "suicide",
            "violence": "violence",
            "sexual": "mental_health_crisis"  # Sexual content concerns mapped to mental health
        }
        
        # Map severity levels
        severity_mapping = {
            "critical": "critical",
            "high": "high", 
            "medium": "medium",
            "low": "low"
        }
        
        risk_categories = []
        for category in content_analysis.get("categories", []):
            mapped_category = category_mapping.get(category, "mental_health_crisis")
            if mapped_category not in risk_categories:
                risk_categories.append(mapped_category)
        
        risk_level = severity_mapping.get(content_analysis.get("severity", "low"), "low")
        
        # Determine if human review is required
        requires_review = (
            content_analysis.get("action") in ["crisis_intervention", "warn"] or
            content_analysis.get("severity") in ["high", "critical"]
        )
        
        # Block auto-response for crisis situations
        block_response = content_analysis.get("action") == "crisis_intervention"
        
        return {
            "risk_level": risk_level,
            "risk_categories": risk_categories,
            "confidence_score": 0.8,  # High confidence since content filter already analyzed
            "reasoning": f"Content filter detected {content_analysis.get('severity', 'unknown')} severity content with categories: {', '.join(content_analysis.get('categories', []))}",
            "requires_human_review": requires_review,
            "auto_response_blocked": block_response,
            "crisis_resources": content_analysis.get("crisis_resources", self._get_crisis_resources()) if requires_review else []
        }

    def _get_crisis_resources(self) -> List[str]:
        """
        Get crisis intervention resources.
        """
        return self.crisis_resources.get("general_crisis", [
            "🆘 National Suicide Prevention Lifeline: 988 or 1-800-273-8255",
            "📞 Crisis Text Line: Text HOME to 741741",
            "🌐 Online Chat: suicidepreventionlifeline.org",
            "🏥 Emergency Services: Call 911 immediately if in immediate danger",
            "💬 SAMHSA National Helpline: 1-800-662-4357 (24/7 treatment referral)",
            "🤝 Crisis Support: If you're in immediate danger, please contact emergency services or go to your nearest emergency room"
        ])

    async def get_recent_risk_assessments(
        self,
        session: Session,
        user_id: str | None = None,
        organization_id: str | None = None,
        days: int = 7,
        limit: int = 50
    ) -> List[RiskAssessment]:
        """
        Get recent risk assessments for monitoring.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            statement = select(RiskAssessment).where(
                RiskAssessment.assessed_at >= cutoff_date
            )
            
            if user_id:
                statement = statement.where(RiskAssessment.user_id == user_id)
            
            if organization_id:
                statement = statement.where(RiskAssessment.organization_id == organization_id)
            
            statement = statement.order_by(RiskAssessment.assessed_at.desc()).limit(limit)
            
            assessments = session.exec(statement).all()
            return list(assessments)
            
        except Exception as e:
            logger.error(f"Error getting recent risk assessments: {str(e)}")
            return []

    async def get_high_risk_conversations(
        self,
        session: Session,
        organization_id: str | None = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get conversations with high risk assessments for counselor dashboard.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(hours=hours)
            
            statement = (
                select(RiskAssessment)
                .where(
                    RiskAssessment.assessed_at >= cutoff_date,
                    RiskAssessment.risk_level.in_(["high", "critical"])
                )
            )
            
            if organization_id:
                statement = statement.where(RiskAssessment.organization_id == organization_id)
            
            statement = statement.order_by(RiskAssessment.assessed_at.desc())
            
            assessments = session.exec(statement).all()
            
            # Enrich with user and conversation details
            enriched_conversations = []
            for assessment in assessments:
                user = session.get(User, assessment.user_id)
                ai_soul = session.get(AISoulEntity, assessment.ai_soul_id)
                chat_message = session.get(ChatMessage, assessment.chat_message_id)
                
                enriched_conversations.append({
                    "assessment_id": str(assessment.id),
                    "risk_level": assessment.risk_level,
                    "risk_categories": json.loads(assessment.risk_categories),
                    "confidence_score": assessment.confidence_score,
                    "reasoning": assessment.reasoning,
                    "assessed_at": assessment.assessed_at,
                    "user_name": user.full_name if user else "Unknown",
                    "user_email": user.email if user else "Unknown",
                    "ai_soul_name": ai_soul.name if ai_soul else "Unknown",
                    "message_content": chat_message.content if chat_message else "Message not found",
                    "requires_review": assessment.requires_human_review,
                    "response_blocked": assessment.auto_response_blocked
                })
            
            return enriched_conversations
            
        except Exception as e:
            logger.error(f"Error getting high risk conversations: {str(e)}")
            return [] 

    def _get_risk_level_priority(self, risk_level: str) -> int:
        """Get priority number for risk level comparison."""
        priority_map = {
            "low": 1,
            "medium": 2,
            "high": 3,
            "critical": 4
        }
        return priority_map.get(risk_level, 1) 