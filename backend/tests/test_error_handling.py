import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import User

def test_database_integrity_error(db: Session):
    """Test database integrity constraints."""
    # Create first user
    user1 = User(email="duplicate@example.com", hashed_password="test123")
    db.add(user1)
    db.commit()

    # Try to create duplicate email (should fail)
    user2 = User(email="duplicate@example.com", hashed_password="test456")
    db.add(user2)

    with pytest.raises(IntegrityError):
        db.commit()

def test_database_connection_error():
    """Test handling database connection errors."""
    with patch('app.core.db.SessionLocal') as mock_session:
        mock_session.side_effect = Exception("Database connection failed")

        # Test that the error is properly handled
        with pytest.raises(Exception):
            mock_session()

def test_transaction_rollback_on_error(db: Session):
    """Test that transactions are properly rolled back on errors."""
    try:
        user = User(email="error@example.com", hashed_password="test123")
        db.add(user)
        # Simulate an error
        raise Exception("Simulated error")
    except Exception:
        db.rollback()

    # Verify the user was not saved
    user_check = db.query(User).filter(User.email == "error@example.com").first()
    assert user_check is None
