"""
RAG-related Background Tasks for Celery

This module contains tasks for:
- Search analytics and optimization
- Vector database maintenance
- Index rebuilding and optimization
- Performance monitoring
"""

import json
import logging
import uuid
from datetime import datetime, timedelta

from sqlmodel import Session, select

from app.celery_app import celery_app
from app.core.db import engine
from app.models import (
    DocumentChunkEnhanced,
    RAGConfiguration,
    SearchQuery,
    SearchResultClick,
    TrainingDocumentChunkEnhanced,
)
from app.services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)


@celery_app.task
def update_search_analytics():
    """
    Update search analytics and performance metrics.
    
    This task runs daily to:
    - Calculate search performance metrics
    - Update chunk relevance scores
    - Identify popular search patterns
    - Generate optimization recommendations
    """
    try:
        with Session(engine) as session:
            # Get recent search queries (last 7 days)
            seven_days_ago = datetime.utcnow() - timedelta(days=7)

            recent_queries = session.exec(
                select(SearchQuery).where(
                    SearchQuery.created_at >= seven_days_ago
                )
            ).all()

            # Calculate metrics
            total_queries = len(recent_queries)
            avg_response_time = sum(q.response_time_ms for q in recent_queries) / total_queries if total_queries > 0 else 0
            queries_with_clicks = sum(1 for q in recent_queries if q.user_clicked_result)
            click_through_rate = queries_with_clicks / total_queries if total_queries > 0 else 0

            # Update chunk performance metrics
            chunk_clicks = session.exec(
                select(SearchResultClick).where(
                    SearchResultClick.clicked_at >= seven_days_ago
                )
            ).all()

            # Group clicks by chunk
            chunk_performance = {}
            for click in chunk_clicks:
                chunk_id = str(click.chunk_id)
                if chunk_id not in chunk_performance:
                    chunk_performance[chunk_id] = {
                        "clicks": 0,
                        "total_similarity": 0,
                        "positions": []
                    }

                chunk_performance[chunk_id]["clicks"] += 1
                chunk_performance[chunk_id]["total_similarity"] += click.similarity_score
                chunk_performance[chunk_id]["positions"].append(click.result_position)

            # Update chunk relevance scores
            for chunk_id, metrics in chunk_performance.items():
                chunk = session.get(DocumentChunkEnhanced, chunk_id)
                if chunk:
                    # Calculate relevance score based on clicks and position
                    avg_position = sum(metrics["positions"]) / len(metrics["positions"])
                    avg_similarity = metrics["total_similarity"] / metrics["clicks"]

                    # Simple relevance formula (can be improved)
                    relevance_score = (avg_similarity * 0.7) + ((10 - avg_position) / 10 * 0.3)

                    chunk.relevance_score = relevance_score
                    chunk.search_count += metrics["clicks"]
                    chunk.last_accessed = datetime.utcnow()
                    session.add(chunk)

            session.commit()

            logger.info(f"Updated search analytics: {total_queries} queries, {click_through_rate:.2%} CTR")

            return {
                "status": "success",
                "total_queries": total_queries,
                "avg_response_time_ms": avg_response_time,
                "click_through_rate": click_through_rate,
                "chunks_updated": len(chunk_performance)
            }

    except Exception as exc:
        logger.error(f"Error updating search analytics: {exc}")
        return {"status": "error", "message": str(exc)}


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def rebuild_vector_index(self, user_id: str, ai_soul_id: str | None = None):
    """
    Rebuild vector index for a user's documents or specific AI soul.
    
    Args:
        user_id: UUID of the user
        ai_soul_id: Optional UUID of specific AI soul to rebuild
    """
    try:
        with Session(engine) as session:
            rag_service = EnhancedRAGService(session)

            # Get chunks to reindex
            if ai_soul_id:
                # Rebuild for specific AI soul (training documents)
                chunks = session.exec(
                    select(TrainingDocumentChunkEnhanced).where(
                        TrainingDocumentChunkEnhanced.ai_soul_id == uuid.UUID(ai_soul_id)
                    )
                ).all()
            else:
                # Rebuild for all user documents
                chunks = session.exec(
                    select(DocumentChunkEnhanced).where(
                        DocumentChunkEnhanced.user_id == uuid.UUID(user_id)
                    )
                ).all()

            if not chunks:
                return {"status": "success", "message": "No chunks to reindex"}

            # Regenerate embeddings and update vector database
            chunk_contents = [chunk.content for chunk in chunks]

            # Generate new embeddings
            embedding_results = rag_service.generate_embeddings_batch_sync(chunk_contents)

            # Update chunks with new embeddings
            for chunk, embedding in zip(chunks, embedding_results, strict=False):
                chunk.embedding = json.dumps(embedding.tolist())
                chunk.last_accessed = datetime.utcnow()
                session.add(chunk)

            session.commit()

            # Update vector database
            rag_service.update_vector_database(chunks)

            logger.info(f"Rebuilt vector index for {len(chunks)} chunks")

            return {
                "status": "success",
                "chunks_reindexed": len(chunks),
                "user_id": user_id,
                "ai_soul_id": ai_soul_id
            }

    except Exception as exc:
        logger.error(f"Error rebuilding vector index: {exc}")

        if self.request.retries < self.max_retries:
            raise self.retry(exc=exc)

        return {"status": "error", "message": str(exc)}


@celery_app.task
def optimize_rag_configuration(user_id: str):
    """
    Analyze user's search patterns and optimize RAG configuration.
    
    Args:
        user_id: UUID of the user to optimize for
    """
    try:
        with Session(engine) as session:
            # Get user's search history
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            user_queries = session.exec(
                select(SearchQuery).where(
                    SearchQuery.user_id == uuid.UUID(user_id),
                    SearchQuery.created_at >= thirty_days_ago
                )
            ).all()

            if not user_queries:
                return {"status": "success", "message": "No search history to analyze"}

            # Analyze search patterns
            avg_response_time = sum(q.response_time_ms for q in user_queries) / len(user_queries)
            avg_results_count = sum(q.results_count for q in user_queries) / len(user_queries)
            queries_with_clicks = sum(1 for q in user_queries if q.user_clicked_result)
            click_through_rate = queries_with_clicks / len(user_queries)

            # Get current RAG configuration
            rag_config = session.exec(
                select(RAGConfiguration).where(
                    RAGConfiguration.user_id == uuid.UUID(user_id)
                )
            ).first()

            if not rag_config:
                # Create default configuration
                rag_config = RAGConfiguration(
                    user_id=uuid.UUID(user_id),
                    chunking_strategy="semantic",
                    chunk_size=500,
                    chunk_overlap=50,
                    embedding_model="text-embedding-3-small",
                    search_algorithm="hybrid",
                    similarity_threshold=0.7,
                    max_results=10,
                    enable_reranking=True
                )
                session.add(rag_config)

            # Optimization recommendations
            recommendations = {}

            # If response time is too high, suggest smaller chunks or fewer results
            if avg_response_time > 2000:  # 2 seconds
                recommendations["reduce_chunk_size"] = True
                recommendations["reduce_max_results"] = True
                rag_config.chunk_size = min(rag_config.chunk_size, 400)
                rag_config.max_results = min(rag_config.max_results, 8)

            # If CTR is low, suggest enabling reranking or adjusting threshold
            if click_through_rate < 0.3:
                recommendations["enable_reranking"] = True
                recommendations["lower_similarity_threshold"] = True
                rag_config.enable_reranking = True
                rag_config.similarity_threshold = max(rag_config.similarity_threshold - 0.1, 0.5)

            # If users are getting too few results, increase max_results
            if avg_results_count < 3:
                recommendations["increase_max_results"] = True
                rag_config.max_results = min(rag_config.max_results + 2, 15)

            # Update configuration
            rag_config.updated_at = datetime.utcnow()
            session.add(rag_config)
            session.commit()

            logger.info(f"Optimized RAG configuration for user {user_id}")

            return {
                "status": "success",
                "user_id": user_id,
                "avg_response_time_ms": avg_response_time,
                "click_through_rate": click_through_rate,
                "recommendations": recommendations,
                "updated_config": {
                    "chunk_size": rag_config.chunk_size,
                    "max_results": rag_config.max_results,
                    "similarity_threshold": rag_config.similarity_threshold,
                    "enable_reranking": rag_config.enable_reranking
                }
            }

    except Exception as exc:
        logger.error(f"Error optimizing RAG configuration: {exc}")
        return {"status": "error", "message": str(exc)}


@celery_app.task
def update_chunk_popularity():
    """
    Update chunk popularity metrics based on recent search activity.
    """
    try:
        with Session(engine) as session:
            # Get recent search result clicks (last 24 hours)
            yesterday = datetime.utcnow() - timedelta(days=1)

            recent_clicks = session.exec(
                select(SearchResultClick).where(
                    SearchResultClick.clicked_at >= yesterday
                )
            ).all()

            # Group by chunk and update metrics
            chunk_updates = {}
            for click in recent_clicks:
                chunk_id = str(click.chunk_id)
                if chunk_id not in chunk_updates:
                    chunk_updates[chunk_id] = {
                        "clicks": 0,
                        "ratings": []
                    }

                chunk_updates[chunk_id]["clicks"] += 1
                if click.user_rating:
                    chunk_updates[chunk_id]["ratings"].append(click.user_rating)

            # Update chunks
            for chunk_id, metrics in chunk_updates.items():
                chunk = session.get(DocumentChunkEnhanced, chunk_id)
                if chunk:
                    chunk.click_count += metrics["clicks"]

                    # Update relevance score if we have ratings
                    if metrics["ratings"]:
                        avg_rating = sum(metrics["ratings"]) / len(metrics["ratings"])
                        # Weighted average with existing score
                        if chunk.relevance_score:
                            chunk.relevance_score = (chunk.relevance_score * 0.7) + (avg_rating / 5 * 0.3)
                        else:
                            chunk.relevance_score = avg_rating / 5

                    session.add(chunk)

            session.commit()

            logger.info(f"Updated popularity metrics for {len(chunk_updates)} chunks")

            return {
                "status": "success",
                "chunks_updated": len(chunk_updates),
                "total_clicks": sum(metrics["clicks"] for metrics in chunk_updates.values())
            }

    except Exception as exc:
        logger.error(f"Error updating chunk popularity: {exc}")
        return {"status": "error", "message": str(exc)}


@celery_app.task
def generate_search_suggestions(user_id: str):
    """
    Generate search suggestions based on user's document content and search history.
    
    Args:
        user_id: UUID of the user to generate suggestions for
    """
    try:
        with Session(engine) as session:
            # Get user's recent search queries
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            recent_queries = session.exec(
                select(SearchQuery).where(
                    SearchQuery.user_id == uuid.UUID(user_id),
                    SearchQuery.created_at >= thirty_days_ago
                )
            ).all()

            # Get user's document chunks to analyze content
            user_chunks = session.exec(
                select(DocumentChunkEnhanced).where(
                    DocumentChunkEnhanced.user_id == uuid.UUID(user_id)
                ).limit(100)  # Limit for performance
            ).all()

            if not user_chunks:
                return {"status": "success", "suggestions": []}

            # Extract common terms and topics from chunks
            # This is a simplified approach - in production, you'd use NLP techniques
            content_words = []
            for chunk in user_chunks:
                # Simple word extraction (you'd want proper NLP here)
                words = chunk.content.lower().split()
                content_words.extend([w for w in words if len(w) > 4])

            # Count word frequency
            word_counts = {}
            for word in content_words:
                word_counts[word] = word_counts.get(word, 0) + 1

            # Get most common words as potential suggestions
            common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20]

            # Generate suggestions
            suggestions = []
            for word, count in common_words[:10]:
                suggestions.append({
                    "query": word.capitalize(),
                    "frequency": count,
                    "type": "content_based"
                })

            # Add suggestions based on search history patterns
            query_patterns = [q.query_text for q in recent_queries]
            for pattern in set(query_patterns):
                if len(pattern) > 3:
                    suggestions.append({
                        "query": pattern,
                        "frequency": query_patterns.count(pattern),
                        "type": "history_based"
                    })

            # Sort by frequency and limit
            suggestions = sorted(suggestions, key=lambda x: x["frequency"], reverse=True)[:15]

            logger.info(f"Generated {len(suggestions)} search suggestions for user {user_id}")

            return {
                "status": "success",
                "user_id": user_id,
                "suggestions": suggestions
            }

    except Exception as exc:
        logger.error(f"Error generating search suggestions: {exc}")
        return {"status": "error", "message": str(exc)}
