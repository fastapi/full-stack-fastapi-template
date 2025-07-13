"""
Cleanup and Maintenance Tasks for Celery

This module contains tasks for:
- Cleaning up expired sessions
- Removing old processing logs
- Archiving old data
- Database maintenance
"""

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlmodel import Session, delete, select

from app.core.db import engine
from app.models import (
    AISoulEntity,
    ChatMessage,
    Document,
    DocumentChunk,
    TrainingDocument,
    TrainingDocumentChunk,
    TrainingMessage,
    User,
)

logger = logging.getLogger(__name__)


def cleanup_expired_chat_sessions():
    """
    Clean up old chat messages and training data.
    """
    try:
        with Session(engine) as session:
            # Clean up old chat messages (older than 90 days)
            ninety_days_ago = datetime.now(timezone.utc) - timedelta(days=90)
            
            old_messages = session.exec(
                select(ChatMessage).where(
                    ChatMessage.timestamp < ninety_days_ago
                )
            ).all()
            
            if not old_messages:
                return {"status": "success", "message": "No old chat messages to clean up"}
            
            # Delete old messages
            session.exec(
                delete(ChatMessage).where(
                    ChatMessage.timestamp < ninety_days_ago
                )
            )
            
            session.commit()
            logger.info(f"Cleaned up {len(old_messages)} old chat messages")
            
            return {
                "status": "success",
                "message": f"Cleaned up {len(old_messages)} old chat messages"
            }
            
    except Exception as exc:
        logger.error(f"Error cleaning up expired chat sessions: {exc}")
        return {"status": "error", "message": str(exc)}


def cleanup_old_documents():
    """
    Clean up old document processing logs and unused documents.
    """
    try:
        with Session(engine) as session:
            # Clean up old document chunks (older than 180 days)
            six_months_ago = datetime.now(timezone.utc) - timedelta(days=180)
            
            old_chunks = session.exec(
                select(DocumentChunk).where(
                    DocumentChunk.created_at < six_months_ago
                )
            ).all()
            
            if old_chunks:
                # Delete old chunks
                session.exec(
                    delete(DocumentChunk).where(
                        DocumentChunk.created_at < six_months_ago
                    )
                )
                
                session.commit()
                logger.info(f"Cleaned up {len(old_chunks)} old document chunks")
                
                return {
                    "status": "success",
                    "message": f"Cleaned up {len(old_chunks)} old document chunks"
                }
            else:
                return {"status": "success", "message": "No old document chunks to clean up"}
                
    except Exception as exc:
        logger.error(f"Error cleaning up old documents: {exc}")
        return {"status": "error", "message": str(exc)}


def cleanup_old_training_data():
    """
    Clean up old training data that is no longer needed.
    """
    try:
        with Session(engine) as session:
            # Clean up training data older than 1 year
            one_year_ago = datetime.now(timezone.utc) - timedelta(days=365)
            
            old_training_chunks = session.exec(
                select(TrainingDocumentChunk).where(
                    TrainingDocumentChunk.created_at < one_year_ago
                )
            ).all()
            
            old_training_messages = session.exec(
                select(TrainingMessage).where(
                    TrainingMessage.timestamp < one_year_ago
                )
            ).all()
            
            chunks_deleted = 0
            messages_deleted = 0
            
            if old_training_chunks:
                session.exec(
                    delete(TrainingDocumentChunk).where(
                        TrainingDocumentChunk.created_at < one_year_ago
                    )
                )
                chunks_deleted = len(old_training_chunks)
            
            if old_training_messages:
                session.exec(
                    delete(TrainingMessage).where(
                        TrainingMessage.timestamp < one_year_ago
                    )
                )
                messages_deleted = len(old_training_messages)
            
            if chunks_deleted > 0 or messages_deleted > 0:
                session.commit()
                logger.info(f"Cleaned up {chunks_deleted} training chunks and {messages_deleted} training messages")
                
                return {
                    "status": "success",
                    "chunks_deleted": chunks_deleted,
                    "messages_deleted": messages_deleted
                }
            else:
                return {"status": "success", "message": "No old training data to clean up"}
                
    except Exception as exc:
        logger.error(f"Error cleaning up old training data: {exc}")
        return {"status": "error", "message": str(exc)}


def get_system_stats():
    """
    Get system statistics for monitoring.
    """
    try:
        with Session(engine) as session:
            # Count various entities
            total_users = session.exec(select(User)).count()
            total_ai_souls = session.exec(select(AISoulEntity)).count()
            total_chat_messages = session.exec(select(ChatMessage)).count()
            total_documents = session.exec(select(Document)).count()
            total_training_documents = session.exec(select(TrainingDocument)).count()
            total_training_messages = session.exec(select(TrainingMessage)).count()
            
            # Get recent activity (last 7 days)
            seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
            recent_messages = session.exec(
                select(ChatMessage).where(
                    ChatMessage.timestamp >= seven_days_ago
                )
            ).count()
            
            recent_training = session.exec(
                select(TrainingMessage).where(
                    TrainingMessage.timestamp >= seven_days_ago
                )
            ).count()
            
            return {
                "status": "success",
                "stats": {
                    "total_users": total_users,
                    "total_ai_souls": total_ai_souls,
                    "total_chat_messages": total_chat_messages,
                    "total_documents": total_documents,
                    "total_training_documents": total_training_documents,
                    "total_training_messages": total_training_messages,
                    "recent_chat_messages": recent_messages,
                    "recent_training_messages": recent_training
                }
            }
            
    except Exception as exc:
        logger.error(f"Error getting system stats: {exc}")
        return {"status": "error", "message": str(exc)}
