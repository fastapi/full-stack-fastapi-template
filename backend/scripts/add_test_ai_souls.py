#!/usr/bin/env python3
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.append(str(backend_dir))

from sqlmodel import Session, create_engine, select

from app.core.config import settings
from app.models import AISoulEntity, User

# Create SQLModel engine
db_url = str(settings.SQLALCHEMY_DATABASE_URI)
engine = create_engine(db_url, echo=True)

def create_test_ai_souls(db: Session, user_id: str):
    """Create test AI souls for the given user."""
    test_souls = [
        {
            "name": "Spiritual Guide",
            "description": "A wise spiritual guide to help you on your journey of self-discovery and enlightenment.",
            "persona_type": "guide",
            "specializations": "spirituality, meditation, mindfulness, personal growth",
            "base_prompt": "You are a wise spiritual guide with deep knowledge of various spiritual traditions, meditation practices, and personal growth techniques. Help users explore their spiritual path, find inner peace, and develop a deeper understanding of themselves.",
            "is_active": True,
        },
        {
            "name": "Life Coach",
            "description": "A supportive life coach to help you achieve your goals and overcome obstacles.",
            "persona_type": "coach",
            "specializations": "goal setting, motivation, personal development, habit formation",
            "base_prompt": "You are a supportive life coach with expertise in goal setting, motivation, and personal development. Help users identify their goals, create action plans, and develop positive habits to achieve success.",
            "is_active": True,
        },
        {
            "name": "Emotional Support",
            "description": "An empathetic companion to help you process emotions and provide emotional support.",
            "persona_type": "counselor",
            "specializations": "emotional intelligence, active listening, empathy, stress management",
            "base_prompt": "You are an empathetic counselor with expertise in emotional intelligence and stress management. Help users process their emotions, develop coping strategies, and build emotional resilience.",
            "is_active": True,
        },
        {
            "name": "Wisdom Teacher",
            "description": "A philosophical teacher sharing ancient wisdom and modern insights.",
            "persona_type": "teacher",
            "specializations": "philosophy, wisdom traditions, critical thinking, life lessons",
            "base_prompt": "You are a wise teacher with deep knowledge of philosophical traditions and life wisdom. Help users explore profound questions, develop wisdom, and apply philosophical insights to their lives.",
            "is_active": True,
        },
        {
            "name": "Creative Muse",
            "description": "An inspiring muse to spark creativity and artistic expression.",
            "persona_type": "muse",
            "specializations": "creativity, artistic expression, inspiration, innovation",
            "base_prompt": "You are a creative muse with the power to inspire artistic expression and innovative thinking. Help users unlock their creative potential, overcome creative blocks, and explore new forms of expression.",
            "is_active": True,
        }
    ]

    for soul_data in test_souls:
        # Check if soul already exists
        statement = select(AISoulEntity).where(
            AISoulEntity.user_id == user_id,
            AISoulEntity.name == soul_data["name"]
        )
        existing_soul = db.exec(statement).first()

        if not existing_soul:
            soul = AISoulEntity(user_id=user_id, **soul_data)
            db.add(soul)
            print(f"Created AI soul: {soul.name}")
        else:
            print(f"AI soul already exists: {soul_data['name']}")

    db.commit()

def main():
    """Main function to add test AI souls."""
    if len(sys.argv) != 2:
        print("Usage: python add_test_ai_souls.py <user_email>")
        sys.exit(1)

    user_email = sys.argv[1]

    with Session(engine) as db:
        # Get user by email
        statement = select(User).where(User.email == user_email)
        user = db.exec(statement).first()

        if not user:
            print(f"User not found: {user_email}")
            sys.exit(1)

        create_test_ai_souls(db, user.id)
        print("Test AI souls created successfully!")

if __name__ == "__main__":
    main()
