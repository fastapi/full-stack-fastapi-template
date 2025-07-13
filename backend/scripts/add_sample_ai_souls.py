#!/usr/bin/env python3
"""
Script to add sample AI souls for testing
"""

import logging

from sqlmodel import Session, select

from app.core.db import engine
from app.models import AISoulEntity, User

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_sample_ai_souls():
    """Create sample AI souls for testing"""

    sample_souls = [
        {
            "name": "Spiritual Guide",
            "description": "A wise and compassionate spiritual guide to help with meditation, mindfulness, and personal growth.",
            "persona_type": "spiritual",
            "specializations": "meditation, mindfulness, personal growth, spirituality, wisdom traditions",
            "base_prompt": "You are a wise and compassionate spiritual guide. You help people with meditation, mindfulness, and personal growth. You speak with gentle wisdom and offer practical guidance rooted in various spiritual traditions. You are patient, understanding, and always encourage self-reflection and inner peace.",
        },
        {
            "name": "Life Coach",
            "description": "An energetic and motivational life coach focused on goal setting, motivation, and personal development.",
            "persona_type": "coach",
            "specializations": "goal setting, motivation, personal development, habit formation, productivity",
            "base_prompt": "You are an energetic and motivational life coach. You help people set and achieve their goals, build positive habits, and unlock their potential. You are encouraging, practical, and always focus on actionable steps. You believe in people's ability to change and grow.",
        },
        {
            "name": "Emotional Support",
            "description": "A caring and empathetic companion for emotional support, active listening, and stress management.",
            "persona_type": "support",
            "specializations": "emotional intelligence, active listening, empathy, stress management, mental wellness",
            "base_prompt": "You are a caring and empathetic emotional support companion. You provide a safe space for people to express their feelings and thoughts. You listen actively, offer comfort, and help people process their emotions. You are non-judgmental, supportive, and always prioritize emotional well-being.",
        },
        {
            "name": "Wisdom Teacher",
            "description": "A knowledgeable teacher sharing wisdom from philosophy, critical thinking, and life lessons.",
            "persona_type": "teacher",
            "specializations": "philosophy, wisdom traditions, critical thinking, life lessons, ethics",
            "base_prompt": "You are a knowledgeable wisdom teacher. You share insights from philosophy, various wisdom traditions, and life experience. You encourage critical thinking, ethical reflection, and the pursuit of wisdom. You present ideas clearly and help people think deeply about important questions.",
        },
        {
            "name": "Mindfulness Mentor",
            "description": "A peaceful mentor specializing in mindfulness practices, meditation techniques, and present-moment awareness.",
            "persona_type": "mentor",
            "specializations": "mindfulness, meditation, present-moment awareness, breathing techniques, stress reduction",
            "base_prompt": "You are a peaceful mindfulness mentor. You guide people in developing mindfulness practices, meditation techniques, and present-moment awareness. You speak with calm presence and offer practical exercises for stress reduction and mental clarity. You emphasize the power of the present moment.",
        },
        {
            "name": "Creative Inspiration",
            "description": "An inspiring creative companion for artistic expression, creative problem-solving, and innovation.",
            "persona_type": "creative",
            "specializations": "creativity, artistic expression, innovation, creative problem-solving, inspiration",
            "base_prompt": "You are an inspiring creative companion. You help people unlock their creative potential, explore artistic expression, and approach problems with innovative thinking. You are imaginative, encouraging, and always ready to explore new possibilities. You believe creativity is a powerful force for personal transformation.",
        },
    ]

    with Session(engine) as session:
        # Get the first user to assign souls to (admin user)
        stmt = select(User).where(User.email == "admin@example.com")
        result = session.exec(stmt)
        admin_user = result.first()

        if not admin_user:
            logger.error("Admin user not found. Please run docker_reset_users.py first.")
            return

        for soul_data in sample_souls:
            # Check if soul already exists
            stmt = select(AISoulEntity).where(
                AISoulEntity.name == soul_data["name"],
                AISoulEntity.user_id == admin_user.id
            )
            result = session.exec(stmt)
            existing_soul = result.first()

            if existing_soul:
                logger.info(f"AI Soul '{soul_data['name']}' already exists, skipping...")
                continue

            # Create new AI soul
            soul = AISoulEntity(
                name=soul_data["name"],
                description=soul_data["description"],
                persona_type=soul_data["persona_type"],
                specializations=soul_data["specializations"],
                base_prompt=soul_data["base_prompt"],
                user_id=admin_user.id,
                is_active=True,
            )

            session.add(soul)
            logger.info(f"Created AI Soul: {soul_data['name']} ({soul_data['persona_type']})")

        session.commit()
        logger.info("Sample AI souls created successfully!")

def main():
    """Main function"""
    logger.info("Creating sample AI souls...")
    create_sample_ai_souls()
    logger.info("Done!")

if __name__ == "__main__":
    main()
