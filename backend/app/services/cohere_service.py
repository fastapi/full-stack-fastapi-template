"""
Cohere LLM Service for Intelligent Risk Assessment

This service uses Cohere's LLM API to perform intelligent risk assessment
and content filtering, replacing hardcoded keyword matching with AI-powered analysis.
"""

import json
import logging
from typing import Any, Dict, List

import httpx
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class RiskAssessmentRequest(BaseModel):
    """Request model for risk assessment"""
    content: str
    context: str = ""
    analysis_type: str = "general"  # general, content_filter, crisis_detection


class RiskAssessmentResponse(BaseModel):
    """Response model for risk assessment"""
    risk_level: str  # low, medium, high, critical
    risk_categories: List[str]
    confidence_score: float
    reasoning: str
    requires_human_review: bool
    auto_response_blocked: bool
    crisis_resources_needed: bool


class CohereService:
    """Service for intelligent risk assessment using Cohere LLM"""
    
    def __init__(self):
        # Use Cohere as the primary LLM service
        if settings.COHERE_API_KEY:
            self.api_key = settings.COHERE_API_KEY
            self.base_url = "https://api.cohere.ai/v1"
            self.model = settings.COHERE_CHAT_MODEL
            self.use_cohere = True
        else:
            raise ValueError("COHERE_API_KEY is required for LLM service")
        
        # Risk categories mapping
        self.risk_categories = [
            "suicide",
            "self_harm", 
            "violence",
            "substance_abuse",
            "abuse",
            "mental_health_crisis",
            "relationship_crisis",
            "financial_crisis",
            "sexual_content",
            "general_distress"
        ]
        
        # Crisis resources
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
            ]
        }

    async def assess_risk(self, content: str, context: str = "", analysis_type: str = "general") -> RiskAssessmentResponse:
        """
        Assess risk level of content using Cohere LLM
        
        Args:
            content: The content to assess
            context: Additional context for the assessment
            analysis_type: Type of analysis (general, content_filter, crisis_detection)
        
        Returns:
            RiskAssessmentResponse with detailed risk assessment
        """
        try:
            # Quick check for normal conversation to avoid unnecessary API calls
            if self._is_normal_conversation(content):
                logger.info(f"Normal conversation detected, skipping AI assessment: '{content[:50]}...'")
                return RiskAssessmentResponse(
                    risk_level="low",
                    risk_categories=[],
                    confidence_score=0.95,
                    reasoning="Normal conversation pattern detected",
                    requires_human_review=False,
                    auto_response_blocked=False,
                    crisis_resources_needed=False
                )
            
            # Build the system prompt based on analysis type
            system_prompt = self._build_system_prompt(analysis_type)
            
            # Build the user prompt
            user_prompt = self._build_user_prompt(content, context, analysis_type)
            
            # Make API call to Cohere
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "message": user_prompt,
                        "preamble": system_prompt,
                        "max_tokens": 500,
                        "temperature": 0.1,  # Low temperature for consistent results
                        "p": 0.9,
                        "stream": False
                    },
                    timeout=30.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Cohere API error: {response.status_code} - {response.text}")
                    return self._fallback_assessment(content, "API_ERROR")
                
                result = response.json()
                ai_response = result["text"]
                
                # Parse the AI response
                return self._parse_ai_response(ai_response, content)
                
        except Exception as e:
            logger.error(f"Error in Cohere risk assessment: {str(e)}")
            return self._fallback_assessment(content, f"ERROR: {str(e)}")



    def _build_system_prompt(self, analysis_type: str) -> str:
        """Build system prompt based on analysis type"""
        
        base_prompt = """You are a professional risk assessment AI designed to evaluate mental health, safety, and content risks in user messages.

Your task is to analyze content and provide a detailed risk assessment in JSON format.

Risk Levels:
- CRITICAL: Immediate suicide/self-harm intent, specific plans, imminent danger to self or others
- HIGH: Strong indicators of crisis, distress, harmful thoughts, or inappropriate content
- MEDIUM: Concerning patterns, mild distress indicators, potential risk factors
- LOW: Normal conversation, no significant risk indicators

Risk Categories:
- suicide: Suicidal ideation, plans, or intent
- self_harm: Self-injury, cutting, or other self-destructive behaviors
- violence: Threats or plans to harm others, violent ideation
- substance_abuse: Drug or alcohol abuse, addiction concerns
- abuse: Domestic violence, child abuse, sexual abuse
- mental_health_crisis: Severe depression, anxiety, psychosis, breakdown
- relationship_crisis: Relationship problems, divorce, breakup distress
- financial_crisis: Bankruptcy, debt, financial distress
- sexual_content: Inappropriate sexual content, sexual abuse
- general_distress: General emotional distress, stress, worry

NORMAL CONVERSATION PATTERNS (DO NOT FLAG):
- Simple greetings: "hello", "hi", "good morning", "how are you"
- Basic questions: "what's your name", "how does this work", "can you help me"
- Casual conversation: "I'm fine", "thank you", "okay", "sure"
- General topics: weather, hobbies, work, school (without distress indicators)
- Positive expressions: "I'm happy", "good day", "thanks"

Guidelines:
- ONLY flag messages with genuine risk indicators or inappropriate content
- DO NOT flag normal conversation, greetings, or casual chat
- Look for specific indicators of harm, crisis, or inappropriate content
- Assess intent and severity carefully
- Normal emotional expression does not require review unless severe
- Only recommend human review for actual concerning content

HUMAN REVIEW CRITERIA (All must be met):
1. Content contains explicit harm indicators OR inappropriate content
2. Message shows clear intent or planning of harmful actions
3. Content is beyond normal emotional expression or casual conversation

Response Format (JSON only):
{
  "risk_level": "low|medium|high|critical",
  "risk_categories": ["category1", "category2"],
  "confidence_score": 0.0-1.0,
  "reasoning": "brief explanation of assessment",
  "requires_human_review": true/false,
  "auto_response_blocked": true/false,
  "crisis_resources_needed": true/false
}"""

        if analysis_type == "content_filter":
            base_prompt += """

CONTENT FILTERING FOCUS:
- Pay special attention to sexual content, violence, and self-harm
- Consider age-appropriateness and context
- Block inappropriate sexual content
- Allow crisis-related content to go through (with human review)"""

        elif analysis_type == "crisis_detection":
            base_prompt += """

CRISIS DETECTION FOCUS:
- Prioritize detection of immediate danger
- Look for specific plans or intent
- Consider timeline and immediacy
- Assess support systems and coping mechanisms"""

        return base_prompt

    def _build_user_prompt(self, content: str, context: str, analysis_type: str) -> str:
        """Build user prompt for assessment"""
        
        prompt = f"""Analyze this content for risk assessment:

Content: "{content}"
"""
        
        if context:
            prompt += f"Context: {context}\n"
        
        prompt += f"Analysis Type: {analysis_type}\n"
        prompt += "\nProvide risk assessment as JSON only (no additional text):"
        
        return prompt

    def _parse_ai_response(self, ai_response: str, content: str) -> RiskAssessmentResponse:
        """Parse AI response and convert to RiskAssessmentResponse"""
        try:
            # Try to extract JSON from response
            response_text = ai_response.strip()
            
            # Handle cases where AI might include extra text
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                response_text = response_text[json_start:json_end]
            elif "{" in response_text:
                json_start = response_text.find("{")
                json_end = response_text.rfind("}") + 1
                response_text = response_text[json_start:json_end]
            
            # Parse JSON
            parsed = json.loads(response_text)
            
            # Validate and normalize the response
            risk_level = parsed.get("risk_level", "medium").lower()
            if risk_level not in ["low", "medium", "high", "critical"]:
                risk_level = "medium"
            
            risk_categories = parsed.get("risk_categories", [])
            if not isinstance(risk_categories, list):
                risk_categories = []
            
            confidence_score = float(parsed.get("confidence_score", 0.5))
            confidence_score = max(0.0, min(1.0, confidence_score))
            
            reasoning = parsed.get("reasoning", "AI-based risk assessment")
            requires_human_review = parsed.get("requires_human_review", risk_level in ["high", "critical"])
            auto_response_blocked = parsed.get("auto_response_blocked", risk_level == "critical")
            crisis_resources_needed = parsed.get("crisis_resources_needed", risk_level in ["high", "critical"])
            
            return RiskAssessmentResponse(
                risk_level=risk_level,
                risk_categories=risk_categories,
                confidence_score=confidence_score,
                reasoning=reasoning,
                requires_human_review=requires_human_review,
                auto_response_blocked=auto_response_blocked,
                crisis_resources_needed=crisis_resources_needed
            )
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            logger.error(f"AI response was: {ai_response}")
            return self._fallback_assessment(content, f"PARSE_ERROR: {str(e)}")

    def _is_normal_conversation(self, content: str) -> bool:
        """Check if content is normal conversation that doesn't need review"""
        content_lower = content.lower().strip()
        
        # Simple greetings and common phrases
        normal_patterns = [
            "hello", "hi", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "how's it going", "what's up", "nice to meet you",
            "thanks", "thank you", "you're welcome", "please", "sure", "okay", "ok",
            "yes", "no", "maybe", "i don't know", "i'm fine", "i'm good", "i'm okay",
            "what's your name", "who are you", "how does this work", "can you help me",
            "what can you do", "tell me about", "i'm happy", "good day", "bye", "goodbye",
            "see you later", "have a good day", "nice talking to you"
        ]
        
        # Check if the entire message (or close to it) is just normal conversation
        for pattern in normal_patterns:
            if pattern in content_lower and len(content_lower) <= len(pattern) + 10:
                return True
        
        # Check for very short messages (likely greetings or simple responses)
        if len(content_lower) <= 15 and not any(word in content_lower for word in 
            ["kill", "die", "hurt", "hate", "suicide", "cut", "blood", "pain", "kill myself"]):
            return True
        
        return False

    def _fallback_assessment(self, content: str, error_reason: str) -> RiskAssessmentResponse:
        """Provide fallback assessment when AI fails"""
        
        # First check if it's normal conversation
        if self._is_normal_conversation(content):
            return RiskAssessmentResponse(
                risk_level="low",
                risk_categories=[],
                confidence_score=0.9,
                reasoning="Normal conversation pattern detected",
                requires_human_review=False,
                auto_response_blocked=False,
                crisis_resources_needed=False
            )
        
        # Simple keyword-based fallback for safety
        content_lower = content.lower()
        
        critical_keywords = [
            "suicide", "kill myself", "end my life", "want to die", "going to die",
            "kill him", "kill her", "murder", "hurt others", "going to hurt",
            "plan to kill", "want to kill"
        ]
        
        high_risk_keywords = [
            "hurt myself", "cut myself", "cutting", "self harm", "self-harm",
            "overdose", "can't go on", "hopeless", "worthless", "end it all",
            "sexual abuse", "molest", "rape", "inappropriate touch"
        ]
        
        risk_level = "low"
        risk_categories = []
        
        # Check for critical keywords with context
        for keyword in critical_keywords:
            if keyword in content_lower:
                risk_level = "critical"
                if any(term in keyword for term in ["suicide", "kill myself", "end my life", "want to die"]):
                    risk_categories.append("suicide")
                elif any(term in keyword for term in ["kill", "murder", "hurt others"]):
                    risk_categories.append("violence")
                break
        
        # Check for high-risk keywords if not already critical
        if risk_level == "low":
            for keyword in high_risk_keywords:
                if keyword in content_lower:
                    risk_level = "high"
                    if any(term in keyword for term in ["hurt myself", "cut myself", "cutting", "self harm"]):
                        risk_categories.append("self_harm")
                    elif any(term in keyword for term in ["hopeless", "worthless", "can't go on"]):
                        risk_categories.append("mental_health_crisis")
                    elif any(term in keyword for term in ["sexual", "abuse", "molest", "rape"]):
                        risk_categories.append("sexual_content")
                    break
        
        return RiskAssessmentResponse(
            risk_level=risk_level,
            risk_categories=risk_categories,
            confidence_score=0.6,  # Medium confidence for fallback
            reasoning=f"Fallback assessment due to: {error_reason}",
            requires_human_review=risk_level in ["high", "critical"],
            auto_response_blocked=risk_level == "critical",
            crisis_resources_needed=risk_level in ["high", "critical"]
        )

    def get_crisis_resources(self, risk_categories: List[str]) -> List[str]:
        """Get appropriate crisis resources based on risk categories"""
        resources = []
        
        for category in risk_categories:
            if category in self.crisis_resources:
                resources.extend(self.crisis_resources[category])
        
        # Remove duplicates while preserving order
        seen = set()
        unique_resources = []
        for resource in resources:
            if resource not in seen:
                seen.add(resource)
                unique_resources.append(resource)
        
        return unique_resources

    async def analyze_content_filter(self, content: str) -> Dict[str, Any]:
        """
        Analyze content for filtering (compatibility with ContentFilterService)
        
        Returns:
            Dict with filtering results in the expected format
        """
        assessment = await self.assess_risk(content, analysis_type="content_filter")
        
        # Convert to ContentFilterService format
        return {
            "flagged": assessment.risk_level in ["medium", "high", "critical"],
            "categories": assessment.risk_categories,
            "severity": assessment.risk_level,
            "action": "block" if assessment.auto_response_blocked else "warn" if assessment.requires_human_review else "allow",
            "crisis_type": assessment.risk_categories[0] if assessment.risk_categories else None,
            "suggested_response": "Crisis resources available" if assessment.crisis_resources_needed else None,
            "crisis_resources": self.get_crisis_resources(assessment.risk_categories) if assessment.crisis_resources_needed else []
        } 