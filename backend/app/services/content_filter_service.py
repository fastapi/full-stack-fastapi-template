import logging
import re
from datetime import datetime

from app.services.cohere_service import CohereService

logger = logging.getLogger(__name__)


class ContentFilterService:
    def __init__(self):
        # Initialize Cohere service for intelligent content filtering
        self.cohere_service = CohereService()
        
        # Keep simple fallback keywords for when AI service fails
        self.fallback_keywords = {
            "violence": ["kill", "murder", "violence", "hurt", "harm", "attack", "fight", "beat", "punch", "knife", "gun", "weapon"],
            "self_harm": ["suicide", "kill myself", "end my life", "hurt myself", "cut myself", "self harm", "self-harm",
                         "want to die", "death", "overdose", "hanging", "jump off", "worthless", "hopeless", "can't go on"],
            "sexual": ["sexual", "sex", "porn", "masturbation", "abuse", "assault", "rape", "molest", "inappropriate touching",
                      "sexual content", "explicit", "adult content"]
        }

        self.crisis_resources = {
            "suicide": {
                "message": "I'm very concerned about what you're sharing. Your life has value and there are people who want to help.",
                "resources": [
                    "🇺🇸 National Suicide Prevention Lifeline: 988 or 1-800-273-8255",
                    "🇺🇸 Crisis Text Line: Text HOME to 741741",
                    "🇺🇸 Trevor Lifeline (LGBTQ): 1-866-488-7386",
                    "🇺🇸 National Sexual Assault Hotline: 1-800-656-4673"
                ]
            },
            "violence": {
                "message": "I notice you're expressing thoughts about violence. Let's talk about healthier ways to handle these feelings.",
                "resources": [
                    "🇺🇸 National Domestic Violence Hotline: 1-800-799-7233",
                    "🇺🇸 Crisis Text Line: Text HOME to 741741"
                ]
            },
            "general_crisis": {
                "message": "I'm here to support you, but I want to make sure you have access to professional help too.",
                "resources": [
                    "🇺🇸 Crisis Text Line: Text HOME to 741741",
                    "🇺🇸 SAMHSA National Helpline: 1-800-662-4357",
                    "📍 For immediate danger, please call 911 or go to your nearest emergency room"
                ]
            }
        }

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

    async def analyze_content(self, content: str) -> dict[str, any]:
        """
        Analyze content for sensitive topics using AI-powered analysis
        """
        try:
            # Quick check for normal conversation to avoid unnecessary processing
            if self._is_normal_conversation(content):
                logger.info(f"Normal conversation detected, skipping content analysis: '{content[:50]}...'")
                return {
                    "flagged": False,
                    "categories": [],
                    "severity": "low",
                    "action": "allow",
                    "crisis_type": None,
                    "suggested_response": None,
                    "crisis_resources": []
                }
            
            # Use Cohere service for intelligent content analysis
            logger.info("Using Cohere LLM for content filtering analysis")
            analysis_result = await self.cohere_service.analyze_content_filter(content)
            
            # Convert Cohere result to expected format
            results = {
                "flagged": analysis_result.get("flagged", False),
                "categories": analysis_result.get("categories", []),
                "severity": analysis_result.get("severity", "low"),
                "action": analysis_result.get("action", "allow"),
                "crisis_type": analysis_result.get("crisis_type"),
                "suggested_response": analysis_result.get("suggested_response"),
                "crisis_resources": analysis_result.get("crisis_resources", [])
            }
            
            logger.info(f"Content analysis completed: flagged={results['flagged']}, "
                       f"severity={results['severity']}, categories={results['categories']}")
            
            return results
            
        except Exception as e:
            logger.error(f"Error in AI-powered content analysis: {str(e)}")
            # Fall back to simple keyword-based analysis
            return self._fallback_analysis(content)

    def _fallback_analysis(self, content: str) -> dict[str, any]:
        """
        Fallback keyword-based analysis when AI service fails
        """
        # First check if it's normal conversation
        if self._is_normal_conversation(content):
            logger.info(f"Normal conversation detected in fallback analysis: '{content[:50]}...'")
            return {
                "flagged": False,
                "categories": [],
                "severity": "low",
                "action": "allow",
                "crisis_type": None,
                "suggested_response": None,
                "crisis_resources": []
            }
        
        content_lower = content.lower()
        
        results = {
            "flagged": False,
            "categories": [],
            "severity": "low",
            "action": "allow",
            "crisis_type": None,
            "suggested_response": None,
            "crisis_resources": []
        }
        
        # Check for self-harm content (highest priority)
        self_harm_score = self._check_self_harm_fallback(content_lower)
        if self_harm_score > 0:
            results["flagged"] = True
            results["categories"].append("self_harm")
            
            if self_harm_score >= 3:
                results["severity"] = "critical"
                results["action"] = "crisis_intervention"
                results["crisis_type"] = "suicide"
                results["suggested_response"] = self.crisis_resources["suicide"]["message"]
                results["crisis_resources"] = self.crisis_resources["suicide"]["resources"]
            elif self_harm_score >= 2:
                results["severity"] = "high"
                results["action"] = "warn"
        
        # Check for violent content
        violence_score = self._check_violence_fallback(content_lower)
        if violence_score > 0:
            results["flagged"] = True
            results["categories"].append("violence")
            
            if violence_score >= 2 and results["severity"] != "critical":
                results["severity"] = "high"
                results["action"] = "warn"
                if not results["crisis_type"]:
                    results["crisis_type"] = "violence"
                    results["suggested_response"] = self.crisis_resources["violence"]["message"]
                    results["crisis_resources"] = self.crisis_resources["violence"]["resources"]
        
        # Check for sexual content
        sexual_score = self._check_sexual_content_fallback(content_lower)
        if sexual_score > 0:
            results["flagged"] = True
            results["categories"].append("sexual")
            
            if sexual_score >= 2 and results["severity"] in ["low", "medium"]:
                results["severity"] = "medium"
                results["action"] = "warn"
        
        # Set default crisis resources if flagged but no specific type
        if results["flagged"] and not results["crisis_resources"]:
            results["crisis_resources"] = self.crisis_resources["general_crisis"]["resources"]
        
        logger.info(f"Fallback analysis completed: flagged={results['flagged']}, severity={results['severity']}")
        return results

    def _check_self_harm_fallback(self, content: str) -> int:
        """Check for self-harm indicators using fallback keywords"""
        score = 0
        
        # Check for fallback keywords
        for keyword in self.fallback_keywords["self_harm"]:
            if keyword in content:
                if keyword in ["suicide", "kill myself", "end my life"]:
                    score += 3
                else:
                    score += 1
                    
        return min(score, 3)  # Cap at 3

    def _check_violence_fallback(self, content: str) -> int:
        """Check for violent content using fallback keywords"""
        score = 0
        
        # Check for fallback keywords
        for keyword in self.fallback_keywords["violence"]:
            if keyword in content:
                if keyword in ["kill", "murder", "gun", "knife", "weapon"]:
                    score += 2
                else:
                    score += 1
                    
        return min(score, 3)  # Cap at 3

    def _check_sexual_content_fallback(self, content: str) -> int:
        """Check for sexual content using fallback keywords"""
        score = 0
        
        # Check for fallback keywords
        for keyword in self.fallback_keywords["sexual"]:
            if keyword in content:
                if keyword in ["rape", "molest", "sexual assault", "sexual abuse"]:
                    score += 3
                else:
                    score += 1
                    
        return min(score, 3)  # Cap at 3

    def generate_filtered_response(self, analysis: dict[str, any], original_response: str) -> str:
        """Generate appropriate response based on content analysis"""

        if analysis["action"] == "crisis_intervention":
            crisis_response = f"""
{analysis['suggested_response']}

**Immediate Help Available:**
{chr(10).join(analysis['crisis_resources'])}

Please reach out to one of these resources right away. You don't have to go through this alone.

While I want to support you as your AI counselor, these crisis resources have specially trained professionals who can provide immediate help. Your life matters, and there are people who care about you and want to help.
            """.strip()
            return crisis_response

        elif analysis["action"] == "warn" and "self_harm" in analysis["categories"]:
            warning_response = f"""
I notice you're going through a very difficult time. While I'm here to support you, I want to make sure you have access to professional crisis support:

**Crisis Resources:**
{chr(10).join(analysis['crisis_resources'])}

{original_response}

Remember, reaching out for professional help is a sign of strength, not weakness.
            """.strip()
            return warning_response

        elif analysis["action"] == "warn":
            # For other warnings (violence, sexual content), add a gentler note
            warning_note = "I want to ensure our conversation remains supportive and appropriate. If you're struggling with difficult thoughts or situations, please consider reaching out to professional resources."
            return f"{original_response}\n\n{warning_note}"

        else:
            return original_response

    def log_flagged_content(self, user_id: str, content: str, analysis: dict[str, any]) -> None:
        """Log flagged content for monitoring and safety purposes"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "content_preview": content[:100] + "..." if len(content) > 100 else content,
            "categories": analysis["categories"],
            "severity": analysis["severity"],
            "action": analysis["action"]
        }

        # In a production environment, this would be logged to a secure monitoring system
        logger.warning(f"Content filtered: {log_entry}")

    def is_crisis_situation(self, analysis: dict[str, any]) -> bool:
        """Check if the content analysis indicates a crisis situation"""
        return analysis.get("severity") == "critical" or analysis.get("action") == "crisis_intervention"

    async def is_safe_content(self, content: str) -> bool:
        """
        Check if content is safe (simple wrapper around analyze_content)
        Returns True if content is safe, False if it should be blocked
        """
        analysis = await self.analyze_content(content)
        # Block content if it's flagged as high severity or requires crisis intervention
        return not (analysis.get("severity") in ["high", "critical"] or
                   analysis.get("action") in ["block", "crisis_intervention"])
