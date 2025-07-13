import logging
from datetime import datetime
from typing import Any

from openai import OpenAI
from sqlmodel import Session, select

from app.core.config import settings
from app.models import AISoulEntity, ChatMessage, User
from app.services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)


class AISoulService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("OpenAI API key is required")
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def get_user_context(self, session: Session, user_id: str, ai_soul_id: str) -> dict[str, Any]:
        """
        Build user context from chat history and profile for personalized responses
        """
        # Get user and AI soul info
        user = session.get(User, user_id)
        ai_soul = session.get(AISoulEntity, ai_soul_id)
        if not user or not ai_soul:
            return {}

        # Get recent chat history for this specific AI soul
        statement = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id, ChatMessage.ai_soul_id == ai_soul_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(50)
        )
        messages = session.exec(statement).all()

        # Build context from user messages only
        user_messages = [msg.content for msg in messages if msg.is_from_user]

        # Analyze conversation patterns
        context = {
            "user_name": user.full_name,
            "user_email": user.email,
            "ai_soul_name": ai_soul.name,
            "ai_soul_persona": ai_soul.persona_type,
            "ai_soul_specializations": ai_soul.specializations.split(","),
            "message_count": len(user_messages),
            "recent_topics": self._extract_topics(user_messages[:10]),
            "conversation_style": self._analyze_style(user_messages),
            "professional_focus": self._extract_professional_focus(user_messages),
            "values_and_beliefs": self._extract_values(user_messages),
        }

        return context

    def _extract_topics(self, messages: list[str]) -> list[str]:
        """Extract key topics from recent messages"""
        topics = []
        keywords = {
            "counseling": ["counseling", "therapy", "counselor", "therapist"],
            "parenting": ["parenting", "children", "kids", "family"],
            "relationships": ["relationship", "marriage", "dating", "partner"],
            "spiritual": ["spiritual", "christian", "bible", "god", "faith", "prayer"],
            "career": ["career", "job", "work", "professional"],
            "emotions": ["emotion", "feeling", "depression", "anxiety", "stress"],
            "education": ["education", "learning", "teaching", "school"],
            "finance": ["money", "financial", "budget", "investment"],
        }

        for message in messages:
            message_lower = message.lower()
            for topic, topic_keywords in keywords.items():
                if any(keyword in message_lower for keyword in topic_keywords):
                    if topic not in topics:
                        topics.append(topic)

        return topics

    def _analyze_style(self, messages: list[str]) -> str:
        """Analyze the user's communication style"""
        if not messages:
            return "supportive"

        # Simple analysis based on message characteristics
        avg_length = sum(len(msg) for msg in messages) / len(messages)
        question_ratio = sum(1 for msg in messages if "?" in msg) / len(messages)

        if avg_length > 200:
            return "detailed"
        elif question_ratio > 0.5:
            return "inquisitive"
        else:
            return "supportive"

    def _extract_professional_focus(self, messages: list[str]) -> list[str]:
        """Extract professional areas of focus"""
        focus_areas = []
        combined_text = " ".join(messages).lower()

        areas = {
            "christian_counseling": ["christian", "bible", "scripture", "faith", "god"],
            "parenting": ["parenting", "children", "kids", "family"],
            "relationships": ["relationship", "marriage", "couples"],
            "grief": ["grief", "loss", "death", "mourning"],
            "addiction": ["addiction", "substance", "recovery"],
            "anxiety": ["anxiety", "worry", "fear", "panic"],
            "depression": ["depression", "sad", "hopeless"],
        }

        for area, keywords in areas.items():
            if any(keyword in combined_text for keyword in keywords):
                focus_areas.append(area.replace("_", " "))

        return focus_areas

    def _extract_values(self, messages: list[str]) -> list[str]:
        """Extract values and beliefs from messages"""
        values = []
        combined_text = " ".join(messages).lower()

        value_keywords = {
            "empathy": ["empathy", "understanding", "compassion", "caring"],
            "family": ["family", "children", "parenting", "home"],
            "faith": ["faith", "spiritual", "christian", "bible", "god"],
            "growth": ["growth", "learning", "development", "progress"],
            "healing": ["healing", "recovery", "wellness", "health"],
            "community": ["community", "together", "support", "help"],
        }

        for value, keywords in value_keywords.items():
            if any(keyword in combined_text for keyword in keywords):
                values.append(value)

        return values

    async def generate_ai_response(self, session: Session, user_id: str, ai_soul_id: str, user_message: str, risk_assessment: dict = None) -> str:
        """
        Generate AI Soul Entity response with enhanced context management and crisis handling
        """
        try:
            # Get user context and AI soul
            context = self.get_user_context(session, user_id, ai_soul_id)
            ai_soul = session.get(AISoulEntity, ai_soul_id)
            if not ai_soul:
                return "Error: AI Soul Entity not found"

            # Detect if this is a critical case requiring enhanced response
            is_critical_case = False
            if risk_assessment:
                is_critical_case = risk_assessment.get("risk_level") in ["high", "critical"]

            # Search for relevant document content (RAG)
            relevant_content = await self._search_relevant_documents(session, user_id, user_message)

            # Search for relevant training data (personalized knowledge)
            training_data = await self._search_training_data(session, ai_soul_id, user_message)

            # Build enhanced conversation history with context window management
            conversation_history = self._build_conversation_history_with_context_management(
                session, user_id, ai_soul_id, user_message
            )

            # Build system prompt based on AI soul's persona and context
            system_prompt = self._build_system_prompt(ai_soul, context, relevant_content, training_data, is_critical_case)

            # Calculate token usage and manage context window
            messages = self._manage_context_window([
                {"role": "system", "content": system_prompt},
                *conversation_history,
                {"role": "user", "content": user_message}
            ])

            # Adjust generation parameters for critical cases
            if is_critical_case:
                # Use more conservative parameters for critical cases
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=1000,  # More space for comprehensive crisis response
                    temperature=0.3,  # Lower temperature for more consistent, empathetic responses
                    presence_penalty=0.2,
                    frequency_penalty=0.1,
                    top_p=0.8  # More focused responses for critical cases
                )
            else:
                # Standard parameters for regular conversations
                response = self.client.chat.completions.create(
                    model="gpt-4",
                    messages=messages,
                    max_tokens=800,  # Increased for more detailed responses
                    temperature=0.7,
                    presence_penalty=0.1,
                    frequency_penalty=0.1,
                    top_p=0.9  # Added for better response quality
                )

            # Update AI soul's usage statistics
            ai_soul.last_used = datetime.utcnow()
            # Note: interaction_count is incremented in the chat route when user sends a message
            # This ensures we count conversation pairs (user message + AI response) as 1 interaction
            session.add(ai_soul)
            session.commit()

            generated_response = response.choices[0].message.content.strip()

            # Log critical case handling
            if is_critical_case:
                logger.info(f"Generated enhanced response for critical case - User: {user_id}, AI Soul: {ai_soul_id}, Risk Level: {risk_assessment.get('risk_level')}")

            return generated_response

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return "I apologize, I'm having trouble processing your message right now. Please try again."

    async def _search_relevant_documents(self, session: Session, user_id: str, query: str) -> list[str]:
        """Search for relevant document content using Enhanced RAG"""
        try:
            rag_service = EnhancedRAGService(session)
            search_response = await rag_service.hybrid_search(
                query=query,
                user_id=user_id,
                limit=3
            )

            relevant_content = []
            for result in search_response.get("results", []):
                content = result["content"]
                # Truncate content if too long for context
                if len(content) > 300:
                    content = content[:300] + "..."
                source = result.get("metadata", {}).get("source", "Document")
                relevant_content.append(f"From {source}: {content}")

            return relevant_content
        except Exception as e:
            logger.error(f"Error searching documents with Enhanced RAG: {str(e)}")
            return []

    async def _search_training_data(self, session: Session, ai_soul_id: str, query: str) -> list[str]:
        """Search for relevant training data for the AI soul"""
        try:
            from app.services.training_service import TrainingService
            training_service = TrainingService(session)

            # Get the AI soul owner's user ID
            ai_soul = session.get(AISoulEntity, ai_soul_id)
            if not ai_soul:
                return []

            training_results = await training_service.get_training_data(
                ai_soul_id=ai_soul_id,
                user_id=str(ai_soul.user_id),
                query=query,
                limit=5
            )

            training_content = []
            for result in training_results:
                if result["type"] == "message":
                    role = "trainer" if result["is_from_trainer"] else "AI"
                    training_content.append(f"Training conversation ({role}): {result['content']}")
                elif result["type"] == "document":
                    source = result["metadata"].get("source", "training document")
                    training_content.append(f"From {source}: {result['content']}")

            return training_content
        except Exception as e:
            logger.error(f"Error searching training data: {str(e)}")
            return []

    def _build_system_prompt(self, ai_soul: AISoulEntity, context: dict[str, Any], relevant_content: list[str] = None, training_data: list[str] = None, is_critical_case: bool = False) -> str:
        """Build enhanced system prompt with RAG best practices and crisis handling"""
        
        # Enhanced crisis handling for critical cases
        if is_critical_case:
            crisis_prompt = f"""You are {ai_soul.name}, an AI Soul Entity specialized as a {ai_soul.persona_type}. 
Your areas of expertise include: {ai_soul.specializations}.

**CRITICAL CASE HANDLING - ENHANCED RESPONSE REQUIRED**

This conversation has been flagged as potentially involving crisis, self-harm, or other serious concerns. Your response must be:

1. **Empathetic and Non-judgmental**: Show deep understanding and compassion
2. **Supportive but Professional**: Provide emotional support while acknowledging limitations
3. **Crisis-Aware**: Recognize signs of distress and respond appropriately
4. **Resource-Oriented**: Guide toward professional help when needed
5. **Safety-Focused**: Prioritize the person's immediate safety and wellbeing

**CRITICAL RESPONSE GUIDELINES:**
- Acknowledge their pain and validate their feelings
- Express genuine concern for their wellbeing
- Avoid minimizing their struggles or offering simple solutions
- Encourage professional help for serious concerns
- Provide hope while being realistic
- Use warm, caring language that shows you truly understand
- If they mention self-harm or suicide, take it seriously and provide crisis resources

Remember: You are a supportive presence, but serious mental health crises require professional intervention."""
            
            base_prompt = crisis_prompt
        else:
            # Start with the soul's custom base prompt if available
            if ai_soul.base_prompt:
                base_prompt = ai_soul.base_prompt
            else:
                base_prompt = f"""You are {ai_soul.name}, an AI Soul Entity specialized as a {ai_soul.persona_type}. 
Your areas of expertise include: {ai_soul.specializations}.

You are designed to embody and represent the person described in your training knowledge. When responding, you should act as if you ARE that person, using their background, experiences, and personal information naturally in conversation. You are NOT a generic AI assistant - you are a personalized AI entity trained to represent a specific individual."""

        # Add user context for personalization
        if context.get("user_name"):
            base_prompt += f"\n\nYou are currently interacting with {context['user_name']}."

        if context.get("professional_focus"):
            base_prompt += f"\nBased on previous conversations, you understand their focus areas: {', '.join(context['professional_focus'])}."

        if context.get("values_and_beliefs"):
            base_prompt += f"\nYou are aware of their values and beliefs: {', '.join(context['values_and_beliefs'])}."

        # Add conversation style guidance
        style = context.get("conversation_style", "supportive")
        base_prompt += f"\nYour communication style should be {style} and authentic to your personality."

        # Enhanced RAG integration with best practices
        knowledge_sections = []
        
        # Add relevant document content with proper attribution
        if relevant_content:
            doc_context = "\n".join([f"• {content}" for content in relevant_content])
            knowledge_sections.append(f"""**Document Knowledge:**
{doc_context}""")

        # Add training data with clear instructions for usage
        if training_data:
            logger.info(f"Adding training data to system prompt: {len(training_data)} items")
            training_context = "\n".join([f"• {data}" for data in training_data])
            knowledge_sections.append(f"""**Personal Training Knowledge:**
{training_context}

This training knowledge contains specific information about the user you're talking to, including their preferences, background, and previous conversations. Use this information to provide personalized and contextually appropriate responses.""")

        # Combine knowledge sections with clear instructions
        if knowledge_sections:
            base_prompt += f"""

**KNOWLEDGE BASE:**
{chr(10).join(knowledge_sections)}

**RESPONSE GUIDELINES:**
1. Prioritize information from your training knowledge when directly relevant to the user's question
2. Use document knowledge to provide comprehensive and accurate information
3. If the training knowledge contains specific details about the user (like their name, preferences, or background), use this information naturally in your responses
4. Maintain consistency with previous conversations and established context
5. If you don't have relevant information in your knowledge base, clearly state your limitations
6. Always be helpful, accurate, and true to your AI Soul personality

**IMPORTANT:** When the user asks about information that you should know from training (like their name or personal details), refer to your training knowledge and provide the information confidently.

**CRITICAL INSTRUCTION:** You MUST use the information from your Personal Training Knowledge section above. For example, if the training knowledge says "My name is Ahmed", then when asked "what is your name?" you should respond with information about Ahmed from the training data, NOT give a generic AI response. You are embodying the person described in your training knowledge.

**PERSONA EMBODIMENT:** Respond as if you ARE the person described in the training knowledge. Use "I" statements naturally. NEVER mention that you are an AI, LLM, artificial intelligence, or any technical terms about your nature. Do NOT say "Based on my training data", "As an AI", "I am an artificial intelligence", or similar phrases. Instead, speak directly as the person. For example, say "I work with Python and React" instead of "The training data shows experience with Python and React".

**KNOWLEDGE LIMITATIONS:** If you don't have information about something in your training knowledge, simply say "I'm not familiar with that" or "I don't have experience with that" or "I'm unaware of that" - do NOT provide detailed explanations about topics not in your training knowledge. Keep responses brief and personal when you lack specific knowledge."""

        logger.info(f"System prompt built with {len(knowledge_sections)} knowledge sections")
        return base_prompt

    def _build_conversation_history(self, session: Session, user_id: str, ai_soul_id: str, limit: int = 10) -> list[dict[str, str]]:
        """Build conversation history for a specific AI soul"""
        statement = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id, ChatMessage.ai_soul_id == ai_soul_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(limit * 2)  # Get extra messages to account for both user and AI messages
        )
        messages = session.exec(statement).all()
        messages.reverse()  # Show in chronological order

        return [
            {"role": "user" if msg.is_from_user else "assistant", "content": msg.content}
            for msg in messages
        ]

    def _build_conversation_history_with_context_management(
        self, 
        session: Session, 
        user_id: str, 
        ai_soul_id: str, 
        current_message: str,
        max_history_messages: int = 20
    ) -> list[dict[str, str]]:
        """Build conversation history with intelligent context management"""
        
        # Get recent conversation history
        statement = (
            select(ChatMessage)
            .where(ChatMessage.user_id == user_id, ChatMessage.ai_soul_id == ai_soul_id)
            .order_by(ChatMessage.timestamp.desc())
            .limit(max_history_messages)
        )
        messages = session.exec(statement).all()
        messages.reverse()  # Show in chronological order

        # Convert to conversation format
        conversation = []
        for msg in messages:
            role = "user" if msg.is_from_user else "assistant"
            conversation.append({"role": role, "content": msg.content})

        return conversation

    def _manage_context_window(self, messages: list[dict[str, str]], max_tokens: int = 7000) -> list[dict[str, str]]:
        """Manage context window to prevent token overflow"""
        
        # Rough token estimation: 1 token ≈ 0.75 words
        def estimate_tokens(text: str) -> int:
            return int(len(text.split()) * 1.33)
        
        total_tokens = 0
        managed_messages = []
        
        # Always include system message (first message)
        if messages and messages[0]["role"] == "system":
            system_message = messages[0]
            total_tokens += estimate_tokens(system_message["content"])
            managed_messages.append(system_message)
            messages = messages[1:]
        
        # Always include the latest user message (last message)
        if messages and messages[-1]["role"] == "user":
            user_message = messages[-1]
            user_tokens = estimate_tokens(user_message["content"])
            messages = messages[:-1]
        else:
            user_message = None
            user_tokens = 0
        
        # Add conversation history from most recent backwards
        for message in reversed(messages):
            message_tokens = estimate_tokens(message["content"])
            
            # Check if adding this message would exceed the limit
            if total_tokens + message_tokens + user_tokens > max_tokens:
                logger.info(f"Context window limit reached. Truncating older messages. Current tokens: {total_tokens}")
                break
                
            managed_messages.insert(-1 if managed_messages else 0, message)
            total_tokens += message_tokens
        
        # Add the user message at the end
        if user_message:
            managed_messages.append(user_message)
            total_tokens += user_tokens
        
        logger.info(f"Context window managed: {len(managed_messages)} messages, ~{total_tokens} tokens")
        return managed_messages

    def get_training_summary(self, session: Session, user_id: str, ai_soul_id: str) -> dict[str, Any]:
        """Get training summary for a specific AI soul"""
        context = self.get_user_context(session, user_id, ai_soul_id)
        ai_soul = session.get(AISoulEntity, ai_soul_id)

        if not ai_soul:
            return {"error": "AI Soul Entity not found"}

        return {
            "ai_soul_name": ai_soul.name,
            "persona_type": ai_soul.persona_type,
            "specializations": ai_soul.specializations.split(","),
            "messages_processed": context.get("message_count", 0),
            "topics_covered": context.get("recent_topics", []),
            "professional_focus": context.get("professional_focus", []),
            "values_learned": context.get("values_and_beliefs", []),
            "communication_style": context.get("conversation_style", "supportive"),
            "interaction_count": ai_soul.interaction_count,
            "last_interaction": ai_soul.last_used.isoformat() if ai_soul.last_used else None,
        }
