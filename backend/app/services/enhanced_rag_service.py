"""
Enhanced RAG Service for AI Soul Entity Project

This service provides advanced document processing, semantic search, and retrieval
capabilities using Qdrant vector database, intelligent chunking, and hybrid search.

Features:
- Intelligent semantic chunking
- Multi-stage retrieval with reranking
- Performance analytics and monitoring
- Caching for improved response times
- Support for multiple document formats
"""

import json
import logging
import time
import uuid
from datetime import datetime
from typing import Any

import numpy as np
from openai import AsyncOpenAI
from sqlmodel import Session, select

from app.core.config import settings
from app.models import (
    Document,
    DocumentChunkEnhanced,
    DocumentProcessingLog,
    RAGConfiguration,
    SearchQuery,
    SearchResultClick,
)

logger = logging.getLogger(__name__)

# Optional imports with graceful fallbacks
try:
    # Import redis with compatibility handling
    import redis.asyncio as aioredis
    REDIS_AVAILABLE = True
    logger.info("Using redis.asyncio for Redis operations")
except ImportError:
    try:
        import aioredis
        REDIS_AVAILABLE = True
        logger.info("Using aioredis for Redis operations")
    except ImportError:
        logger.warning("Redis not available - caching will be disabled")
        REDIS_AVAILABLE = False
    except Exception as e:
        logger.warning(f"aioredis import failed: {e} - trying fallback")
        REDIS_AVAILABLE = False
except Exception as e:
    logger.warning(f"Redis import failed: {e} - caching will be disabled")
    REDIS_AVAILABLE = False

try:
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        CollectionStatus,
        Distance,
        FieldCondition,
        Filter,
        MatchValue,
        PointStruct,
        VectorParams,
    )
    QDRANT_AVAILABLE = True
except ImportError:
    logger.warning("Qdrant not available - vector search will be limited")
    QDRANT_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    logger.warning("Sentence Transformers not available - semantic chunking will be limited")
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    logger.warning("Scikit-learn not available - reranking will be limited")
    SKLEARN_AVAILABLE = False


class EnhancedRAGService:
    """Enhanced RAG service with intelligent chunking and hybrid search."""

    def __init__(self, db_session: Session):
        self.db = db_session
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

        # Initialize Qdrant client if available
        self.qdrant_client = None
        if QDRANT_AVAILABLE:
            try:
                self.qdrant_client = QdrantClient(
                    url=settings.QDRANT_URL or "http://localhost:6333",
                    timeout=60
                )
                logger.info(f"Qdrant client initialized successfully with URL: {settings.QDRANT_URL or 'http://localhost:6333'}")
            except Exception as e:
                logger.error(f"Failed to connect to Qdrant: {e}")
                self.qdrant_client = None
        else:
            logger.error("Qdrant client library not available")

        # Collection names
        self.documents_collection = "ai_soul_documents"
        self.training_collection = "ai_soul_training"

        # Initialize Redis for caching
        self.redis_client = None
        self.redis_initialized = False

        # Initialize sentence transformer for semantic chunking
        self.sentence_transformer = None
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_sentence_transformer()

        # TF-IDF vectorizer for hybrid search
        if SKLEARN_AVAILABLE:
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=1000,
                stop_words='english',
                ngram_range=(1, 2)
            )
        else:
            self.tfidf_vectorizer = None

        # Collections will be initialized on first use
        self.collections_initialized = False

    async def _initialize_redis(self):
        """Initialize Redis connection for caching."""
        try:
            # Use the appropriate Redis client based on what was imported
            if hasattr(aioredis, 'from_url'):
                self.redis_client = await aioredis.from_url(
                    settings.REDIS_URL or "redis://localhost:6379",
                    decode_responses=True
                )
            else:
                # Fallback for older aioredis versions
                self.redis_client = aioredis.Redis.from_url(
                    settings.REDIS_URL or "redis://localhost:6379",
                    decode_responses=True
                )
            
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}")
            self.redis_client = None

    def _initialize_sentence_transformer(self):
        """Initialize sentence transformer for semantic chunking."""
        try:
            self.sentence_transformer = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Sentence transformer initialized")
        except Exception as e:
            logger.warning(f"Sentence transformer initialization failed: {e}")
            self.sentence_transformer = None

    async def _ensure_initialization(self):
        """Ensure all services are initialized before use."""
        # Initialize Redis if not already done
        if REDIS_AVAILABLE and not self.redis_initialized:
            await self._initialize_redis()
            self.redis_initialized = True

        # Initialize Qdrant collections if not already done
        if self.qdrant_client and not self.collections_initialized:
            await self._initialize_collections()
            self.collections_initialized = True

    async def _initialize_collections(self):
        """Initialize Qdrant collections for documents and training data."""
        if not self.qdrant_client:
            return

        try:
            # Check if collections exist
            collections = self.qdrant_client.get_collections()
            existing_collections = [col.name for col in collections.collections]

            # Create documents collection if it doesn't exist
            if self.documents_collection not in existing_collections:
                self.qdrant_client.create_collection(
                    collection_name=self.documents_collection,
                    vectors_config=VectorParams(
                        size=1536,  # OpenAI text-embedding-3-small dimension
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.documents_collection}")

            # Create training collection if it doesn't exist
            if self.training_collection not in existing_collections:
                self.qdrant_client.create_collection(
                    collection_name=self.training_collection,
                    vectors_config=VectorParams(
                        size=1536,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Created collection: {self.training_collection}")

        except Exception as e:
            logger.error(f"Error initializing Qdrant collections: {e}")

    async def get_embedding(self, text: str, model: str = "text-embedding-3-small") -> list[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = await self.openai_client.embeddings.create(
                model=model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return [0.0] * 1536  # Return zero vector on error

    async def intelligent_chunking(
        self,
        text: str,
        chunk_size: int = 500,
        overlap: int = 50,
        strategy: str = "semantic"
    ) -> list[dict[str, Any]]:
        """
        Intelligent chunking with semantic boundaries.
        
        Args:
            text: Input text to chunk
            chunk_size: Target chunk size in characters
            overlap: Overlap between chunks
            strategy: Chunking strategy ('semantic', 'sentence', 'paragraph')
        
        Returns:
            List of chunk dictionaries with content and metadata
        """
        chunks = []

        if strategy == "semantic" and self.sentence_transformer:
            chunks = await self._semantic_chunking(text, chunk_size, overlap)
        elif strategy == "sentence":
            chunks = await self._sentence_chunking(text, chunk_size, overlap)
        elif strategy == "paragraph":
            chunks = await self._paragraph_chunking(text, chunk_size, overlap)
        else:
            # Fallback to simple chunking
            chunks = await self._simple_chunking(text, chunk_size, overlap)

        # Add metadata to chunks and ensure size constraints
        final_chunks = []
        for i, chunk in enumerate(chunks):
            content = chunk["content"]

            # If chunk is still too large, split it further
            if len(content) > 3500:
                # Simple split for oversized chunks
                sub_chunks = []
                start = 0
                while start < len(content):
                    end = start + 3500
                    sub_chunk_content = content[start:end]
                    sub_chunks.append({
                        "content": sub_chunk_content,
                        "metadata": chunk.get("metadata", {})
                    })
                    start = end

                # Add sub-chunks with updated indices
                for j, sub_chunk in enumerate(sub_chunks):
                    sub_chunk.update({
                        "chunk_index": len(final_chunks),
                        "total_chunks": -1,  # Will be updated later
                        "chunking_strategy": strategy,
                        "chunk_size_target": chunk_size,
                        "actual_size": len(sub_chunk["content"]),
                        "created_at": datetime.utcnow().isoformat()
                    })
                    final_chunks.append(sub_chunk)
            else:
                chunk.update({
                    "chunk_index": len(final_chunks),
                    "total_chunks": -1,  # Will be updated later
                    "chunking_strategy": strategy,
                    "chunk_size_target": chunk_size,
                    "actual_size": len(chunk["content"]),
                    "created_at": datetime.utcnow().isoformat()
                })
                final_chunks.append(chunk)

        # Update total_chunks count
        for chunk in final_chunks:
            chunk["total_chunks"] = len(final_chunks)

        return final_chunks

    async def _semantic_chunking(self, text: str, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
        """Semantic chunking using sentence embeddings."""
        if not self.sentence_transformer:
            logger.warning("Sentence transformer not available, falling back to sentence chunking")
            return await self._sentence_chunking(text, chunk_size, overlap)

        try:
            # Split into sentences
            sentences = self._split_sentences(text)
            if not sentences:
                return [{"content": text, "metadata": {"type": "fallback"}}]

            # Generate embeddings for sentences
            sentence_embeddings = self.sentence_transformer.encode(sentences)

            chunks = []
            current_chunk = []
            current_length = 0

            for i, sentence in enumerate(sentences):
                sentence_length = len(sentence)

                # Check if adding this sentence would exceed chunk size
                if current_length + sentence_length > chunk_size and current_chunk:
                    # Calculate semantic coherence of current chunk
                    chunk_text = " ".join(current_chunk)
                    coherence_score = self._calculate_semantic_coherence(
                        current_chunk, sentence_embeddings[i-len(current_chunk):i]
                    )

                    chunks.append({
                        "content": chunk_text,
                        "metadata": {
                            "type": "semantic",
                            "sentence_count": len(current_chunk),
                            "coherence_score": coherence_score,
                            "start_sentence": i - len(current_chunk),
                            "end_sentence": i - 1
                        }
                    })

                    # Start new chunk with overlap
                    overlap_sentences = max(1, overlap // 50)  # Approximate sentences for overlap
                    current_chunk = current_chunk[-overlap_sentences:] + [sentence]
                    current_length = sum(len(s) for s in current_chunk)
                else:
                    current_chunk.append(sentence)
                    current_length += sentence_length

            # Add final chunk
            if current_chunk:
                chunk_text = " ".join(current_chunk)
                coherence_score = self._calculate_semantic_coherence(
                    current_chunk, sentence_embeddings[-len(current_chunk):]
                )

                chunks.append({
                    "content": chunk_text,
                    "metadata": {
                        "type": "semantic",
                        "sentence_count": len(current_chunk),
                        "coherence_score": coherence_score,
                        "start_sentence": len(sentences) - len(current_chunk),
                        "end_sentence": len(sentences) - 1
                    }
                })

            return chunks

        except Exception as e:
            logger.error(f"Error in semantic chunking: {e}")
            return await self._simple_chunking(text, chunk_size, overlap)

    async def _sentence_chunking(self, text: str, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
        """Chunking based on sentence boundaries."""
        sentences = self._split_sentences(text)
        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            if current_length + len(sentence) > chunk_size and current_chunk:
                chunks.append({
                    "content": " ".join(current_chunk),
                    "metadata": {
                        "type": "sentence",
                        "sentence_count": len(current_chunk)
                    }
                })

                # Handle overlap
                overlap_sentences = max(1, overlap // 50)
                current_chunk = current_chunk[-overlap_sentences:] + [sentence]
                current_length = sum(len(s) for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_length += len(sentence)

        if current_chunk:
            chunks.append({
                "content": " ".join(current_chunk),
                "metadata": {
                    "type": "sentence",
                    "sentence_count": len(current_chunk)
                }
            })

        return chunks

    async def _paragraph_chunking(self, text: str, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
        """Chunking based on paragraph boundaries."""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = []
        current_length = 0

        for paragraph in paragraphs:
            if current_length + len(paragraph) > chunk_size and current_chunk:
                chunks.append({
                    "content": "\n\n".join(current_chunk),
                    "metadata": {
                        "type": "paragraph",
                        "paragraph_count": len(current_chunk)
                    }
                })

                current_chunk = [paragraph]
                current_length = len(paragraph)
            else:
                current_chunk.append(paragraph)
                current_length += len(paragraph) + 2  # +2 for \n\n

        if current_chunk:
            chunks.append({
                "content": "\n\n".join(current_chunk),
                "metadata": {
                    "type": "paragraph",
                    "paragraph_count": len(current_chunk)
                }
            })

        return chunks

    async def _simple_chunking(self, text: str, chunk_size: int, overlap: int) -> list[dict[str, Any]]:
        """Simple character-based chunking with overlap."""
        chunks = []
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "content": chunk_text,
                "metadata": {
                    "type": "simple",
                    "start_char": start,
                    "end_char": end
                }
            })

            start += chunk_size - overlap

        return chunks

    def _split_sentences(self, text: str) -> list[str]:
        """Split text into sentences using simple heuristics."""
        import re

        # Simple sentence splitting - can be enhanced with NLTK or spaCy
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences

    def _calculate_semantic_coherence(self, sentences: list[str], embeddings: np.ndarray) -> float:
        """Calculate semantic coherence score for a chunk."""
        if len(embeddings) < 2:
            return 1.0

        try:
            from sklearn.metrics.pairwise import cosine_similarity

            # Calculate average pairwise cosine similarity
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    similarity = cosine_similarity(
                        embeddings[i].reshape(1, -1),
                        embeddings[j].reshape(1, -1)
                    )[0][0]
                    similarities.append(similarity)

            return float(np.mean(similarities)) if similarities else 0.0
        except ImportError:
            # Fallback to simple calculation
            return 0.8  # Default coherence score

    async def process_document(
        self,
        document: Document,
        user_id: str,
        config: RAGConfiguration | None = None
    ) -> dict[str, Any]:
        """
        Process a document with enhanced chunking and indexing.
        
        Args:
            document: Document model instance
            user_id: User ID for tracking
            config: RAG configuration (optional)
        
        Returns:
            Processing results with metrics
        """
        start_time = time.time()

        # Log processing start
        processing_log = DocumentProcessingLog(
            document_id=document.id,
            user_id=uuid.UUID(user_id),
            processing_stage="started",
            status="started",
            created_at=datetime.utcnow()
        )
        self.db.add(processing_log)
        self.db.commit()

        try:
            # Ensure initialization
            await self._ensure_initialization()

            # Get configuration or use defaults
            if not config:
                config = await self._get_or_create_config(user_id)

            # Extract text from document
            text_content = await self._extract_document_text(document.file_path)

            # Update processing log
            processing_log.processing_stage = "text_extraction"
            processing_log.status = "completed"
            processing_log.processing_time_ms = int((time.time() - start_time) * 1000)
            self.db.commit()

            # Intelligent chunking with database constraint
            chunk_start = time.time()
            # Ensure chunk size doesn't exceed database limit
            max_chunk_size = min(config.chunk_size, 3500)  # Leave some buffer for metadata
            chunks = await self.intelligent_chunking(
                text_content,
                chunk_size=max_chunk_size,
                overlap=config.chunk_overlap,
                strategy=config.chunking_strategy
            )

            # Update processing log for chunking
            processing_log.processing_stage = "chunking"
            processing_log.chunks_created = len(chunks)
            processing_log.processing_time_ms = int((time.time() - chunk_start) * 1000)
            self.db.commit()

            # Generate embeddings and store in Qdrant
            embedding_start = time.time()
            stored_chunks = []

            for chunk_data in chunks:
                # Generate embedding
                embedding = await self.get_embedding(
                    chunk_data["content"],
                    config.embedding_model
                )

                # Create enhanced chunk record
                chunk_record = DocumentChunkEnhanced(
                    document_id=document.id,
                    user_id=uuid.UUID(user_id),
                    content=chunk_data["content"],
                    chunk_index=chunk_data["chunk_index"],
                    chunk_metadata=json.dumps(chunk_data["metadata"]),
                    semantic_metadata=json.dumps({
                        "coherence_score": chunk_data["metadata"].get("coherence_score", 0.0),
                        "sentence_count": chunk_data["metadata"].get("sentence_count", 0),
                        "chunking_strategy": chunk_data["metadata"].get("chunking_strategy", "unknown")
                    }),
                    embedding_model=config.embedding_model,
                    embedding_dimension=len(embedding),
                    created_at=datetime.utcnow()
                )

                self.db.add(chunk_record)
                self.db.flush()  # Get the ID

                # Store in Qdrant if available
                if self.qdrant_client:
                    point = PointStruct(
                        id=str(chunk_record.id),
                        vector=embedding,
                        payload={
                            "document_id": str(document.id),
                            "user_id": user_id,
                            "chunk_index": chunk_data["chunk_index"],
                            "content": chunk_data["content"][:500],  # Truncated for payload
                            "metadata": chunk_data["metadata"],
                            "created_at": datetime.utcnow().isoformat()
                        }
                    )

                    self.qdrant_client.upsert(
                        collection_name=self.documents_collection,
                        points=[point]
                    )
                else:
                    logger.warning("Qdrant client not available - skipping vector storage")

                stored_chunks.append(chunk_record)

            self.db.commit()

            # Update final processing log
            processing_log.processing_stage = "completed"
            processing_log.status = "completed"
            processing_log.processing_time_ms = int((time.time() - start_time) * 1000)
            processing_log.completed_at = datetime.utcnow()

            # Update document
            document.processing_status = "completed"
            document.chunk_count = len(chunks)

            self.db.commit()

            return {
                "status": "success",
                "chunks_created": len(chunks),
                "processing_time_ms": int((time.time() - start_time) * 1000),
                "embedding_model": config.embedding_model,
                "chunking_strategy": config.chunking_strategy
            }

        except Exception as e:
            logger.error(f"Error processing document {document.id}: {e}")

            # Update processing log with error
            processing_log.processing_stage = "failed"
            processing_log.status = "failed"
            processing_log.error_message = str(e)
            processing_log.processing_time_ms = int((time.time() - start_time) * 1000)

            # Update document status
            document.processing_status = "failed"

            self.db.commit()

            raise

    async def _extract_document_text(self, file_path: str) -> str:
        """Extract text from various document formats."""
        try:
            if file_path.lower().endswith('.pdf'):
                return await self._extract_pdf_text(file_path)
            elif file_path.lower().endswith(('.doc', '.docx')):
                return await self._extract_docx_text(file_path)
            elif file_path.lower().endswith('.txt'):
                return await self._extract_txt_text(file_path)
            else:
                raise ValueError(f"Unsupported file format: {file_path}")
        except Exception as e:
            logger.error(f"Error extracting text from {file_path}: {e}")
            raise

    async def _extract_pdf_text(self, file_path: str) -> str:
        """Extract text from PDF using PyMuPDF."""
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            text = ""

            for page in doc:
                text += page.get_text()

            doc.close()
            return text

        except ImportError:
            # Fallback to PyPDF2
            from PyPDF2 import PdfReader

            reader = PdfReader(file_path)
            text = ""

            for page in reader.pages:
                text += page.extract_text()

            return text

    async def _extract_docx_text(self, file_path: str) -> str:
        """Extract text from DOCX files."""
        from docx import Document

        doc = Document(file_path)
        text = ""

        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"

        return text

    async def _extract_txt_text(self, file_path: str) -> str:
        """Extract text from plain text files."""
        with open(file_path, encoding='utf-8') as file:
            return file.read()

    async def _get_or_create_config(self, user_id: str) -> RAGConfiguration:
        """Get or create RAG configuration for user."""
        config = self.db.exec(
            select(RAGConfiguration).where(
                RAGConfiguration.user_id == uuid.UUID(user_id),
                RAGConfiguration.ai_soul_id.is_(None)  # Default config
            )
        ).first()

        if not config:
            config = RAGConfiguration(
                user_id=uuid.UUID(user_id),
                chunking_strategy="semantic",
                chunk_size=500,
                chunk_overlap=50,
                embedding_model="text-embedding-3-small",
                search_algorithm="hybrid",
                similarity_threshold=0.1,
                max_results=10,
                enable_reranking=True
            )
            self.db.add(config)
            self.db.commit()
            self.db.refresh(config)

        return config

    async def hybrid_search(
        self,
        query: str,
        user_id: str,
        ai_soul_id: str | None = None,
        filters: dict[str, Any] | None = None,
        limit: int = 10
    ) -> dict[str, Any]:
        """
        Perform hybrid search combining vector similarity and keyword matching.
        
        Args:
            query: Search query
            user_id: User ID for filtering and analytics
            ai_soul_id: Optional AI Soul ID for filtering
            filters: Additional filters
            limit: Maximum number of results
        
        Returns:
            Search results with metadata and analytics
        """
        start_time = time.time()

        try:
            # Ensure initialization
            await self._ensure_initialization()

            # If Qdrant is not available, use database-only search
            if not self.qdrant_client:
                logger.warning("Qdrant not available, falling back to database-only search")
                return await self._database_only_search(query, user_id, ai_soul_id, filters, limit)

            # Check cache first
            cache_key = self._generate_cache_key(query, user_id, ai_soul_id, filters, limit)
            cached_results = await self._get_cached_results(cache_key)

            if cached_results:
                # Log cached search
                await self._log_search_query(
                    query, user_id, ai_soul_id, filters,
                    len(cached_results["results"]),
                    int((time.time() - start_time) * 1000),
                    cached=True
                )
                return cached_results

            # Get user configuration
            config = await self._get_or_create_config(user_id)

            # Generate query embedding
            query_embedding = await self.get_embedding(query, config.embedding_model)

            # Build Qdrant filter
            qdrant_filter = self._build_qdrant_filter(user_id, ai_soul_id, filters)

            # Vector search in Qdrant
            vector_results = self.qdrant_client.search(
                collection_name=self.documents_collection,
                query_vector=query_embedding,
                query_filter=qdrant_filter,
                limit=min(limit * 2, 50),  # Get more for reranking
                with_payload=True,
                with_vectors=False,
                score_threshold=0.05  # Lower threshold for testing
            )

            # Convert to standardized format
            search_results = []
            for result in vector_results:
                # Get full chunk data from database
                chunk = self.db.get(DocumentChunkEnhanced, uuid.UUID(result.id))
                if chunk:
                    search_results.append({
                        "chunk_id": str(chunk.id),
                        "document_id": str(chunk.document_id),
                        "content": chunk.content,
                        "similarity_score": result.score,
                        "chunk_index": chunk.chunk_index,
                        "metadata": json.loads(chunk.chunk_metadata or "{}"),
                        "semantic_metadata": json.loads(chunk.semantic_metadata or "{}"),
                        "embedding_model": chunk.embedding_model
                    })
                else:
                    logger.warning(f"Chunk not found in database for ID: {result.id}")

            # Apply reranking if enabled
            if config.enable_reranking and len(search_results) > 1:
                search_results = await self._rerank_results(query, search_results)

            # Apply additional filtering and ranking
            final_results = await self._apply_business_logic_filtering(
                search_results, config, limit
            )

            # Prepare response
            response = {
                "query": query,
                "results": final_results[:limit],
                "total_found": len(final_results),
                "response_time_ms": int((time.time() - start_time) * 1000),
                "search_algorithm": config.search_algorithm,
                "similarity_threshold": config.similarity_threshold,
                "reranking_enabled": config.enable_reranking
            }

            # Cache results
            await self._cache_results(cache_key, response)

            # Log search query
            await self._log_search_query(
                query, user_id, ai_soul_id, filters,
                len(final_results),
                response["response_time_ms"]
            )

            # Update chunk search counts
            await self._update_chunk_analytics(final_results)

            return response

        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")

            # Log failed search
            await self._log_search_query(
                query, user_id, ai_soul_id, filters, 0,
                int((time.time() - start_time) * 1000),
                error=str(e)
            )

            raise

    async def _rerank_results(
        self,
        query: str,
        results: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """
        Rerank search results using cross-encoder or other reranking methods.
        
        For now, implements a simple TF-IDF based reranking.
        Can be enhanced with cross-encoder models later.
        """
        try:
            if not results:
                return results

            # Extract content for TF-IDF
            documents = [result["content"] for result in results]
            documents.append(query)  # Add query as last document

            # Fit TF-IDF and get similarity scores
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            query_tfidf = tfidf_matrix[-1]  # Query is the last document
            doc_tfidf = tfidf_matrix[:-1]   # Documents are all except last

            # Calculate TF-IDF similarities
            tfidf_similarities = cosine_similarity(query_tfidf, doc_tfidf).flatten()

            # Combine vector similarity and TF-IDF similarity
            for i, result in enumerate(results):
                vector_sim = result["similarity_score"]
                tfidf_sim = tfidf_similarities[i]

                # Weighted combination (can be tuned)
                combined_score = 0.7 * vector_sim + 0.3 * tfidf_sim

                result["rerank_score"] = combined_score
                result["tfidf_similarity"] = float(tfidf_sim)

            # Sort by combined score
            results.sort(key=lambda x: x["rerank_score"], reverse=True)

            return results

        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            # Return original results if reranking fails
            return results

    def _build_qdrant_filter(
        self,
        user_id: str,
        ai_soul_id: str | None = None,
        additional_filters: dict[str, Any] | None = None
    ) -> Filter | None:
        """Build Qdrant filter from search parameters."""
        conditions = []

        # Always filter by user
        conditions.append(
            FieldCondition(
                key="user_id",
                match=MatchValue(value=user_id)
            )
        )

        # Add AI Soul filter if specified
        if ai_soul_id:
            conditions.append(
                FieldCondition(
                    key="ai_soul_id",
                    match=MatchValue(value=ai_soul_id)
                )
            )

        # Add additional filters
        if additional_filters:
            for key, value in additional_filters.items():
                if key in ["document_id", "content_type", "created_after", "created_before"]:
                    conditions.append(
                        FieldCondition(
                            key=key,
                            match=MatchValue(value=value)
                        )
                    )

        return Filter(must=conditions) if conditions else None

    async def _apply_business_logic_filtering(
        self,
        results: list[dict[str, Any]],
        config: RAGConfiguration,
        limit: int
    ) -> list[dict[str, Any]]:
        """Apply business logic filtering and ranking."""
        filtered_results = []

        for result in results:
            # Apply similarity threshold
            score_to_check = result.get("rerank_score", result["similarity_score"])



            if score_to_check >= config.similarity_threshold:
                # Add relevance indicators
                result["above_threshold"] = True
                result["relevance_tier"] = self._calculate_relevance_tier(score_to_check)

                filtered_results.append(result)
            else:
                result["above_threshold"] = False

        # Sort by best available score
        filtered_results.sort(
            key=lambda x: x.get("rerank_score", x["similarity_score"]),
            reverse=True
        )

        return filtered_results

    def _calculate_relevance_tier(self, score: float) -> str:
        """Calculate relevance tier based on score."""
        if score >= 0.9:
            return "excellent"
        elif score >= 0.8:
            return "good"
        elif score >= 0.7:
            return "moderate"
        else:
            return "low"

    def _generate_cache_key(
        self,
        query: str,
        user_id: str,
        ai_soul_id: str | None,
        filters: dict[str, Any] | None,
        limit: int
    ) -> str:
        """Generate cache key for search results."""
        import hashlib

        key_parts = [
            query.lower().strip(),
            user_id,
            ai_soul_id or "",
            json.dumps(filters or {}, sort_keys=True),
            str(limit)
        ]

        key_string = "|".join(key_parts)
        return f"rag_search:{hashlib.md5(key_string.encode()).hexdigest()}"

    async def _get_cached_results(self, cache_key: str) -> dict[str, Any] | None:
        """Get cached search results."""
        if not self.redis_client:
            return None

        try:
            cached_data = await self.redis_client.get(cache_key)
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning(f"Error getting cached results: {e}")

        return None

    async def _cache_results(self, cache_key: str, results: dict[str, Any]) -> None:
        """Cache search results."""
        if not self.redis_client:
            return

        try:
            # Cache for 1 hour
            await self.redis_client.setex(
                cache_key,
                3600,
                json.dumps(results, default=str)
            )
        except Exception as e:
            logger.warning(f"Error caching results: {e}")

    async def _log_search_query(
        self,
        query: str,
        user_id: str,
        ai_soul_id: str | None,
        filters: dict[str, Any] | None,
        results_count: int,
        response_time_ms: int,
        cached: bool = False,
        error: str | None = None
    ) -> None:
        """Log search query for analytics."""
        try:
            search_log = SearchQuery(
                query_text=query,
                user_id=uuid.UUID(user_id),
                ai_soul_id=uuid.UUID(ai_soul_id) if ai_soul_id else None,
                filters_applied=json.dumps(filters) if filters else None,
                results_count=results_count,
                response_time_ms=response_time_ms,
                user_clicked_result=False,  # Will be updated when user clicks
                created_at=datetime.utcnow()
            )

            self.db.add(search_log)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error logging search query: {e}")

    async def _update_chunk_analytics(self, results: list[dict[str, Any]]) -> None:
        """Update analytics for returned chunks."""
        try:
            for result in results:
                chunk_id = uuid.UUID(result["chunk_id"])
                chunk = self.db.get(DocumentChunkEnhanced, chunk_id)

                if chunk:
                    chunk.search_count += 1
                    chunk.last_accessed = datetime.utcnow()

            self.db.commit()

        except Exception as e:
            logger.error(f"Error updating chunk analytics: {e}")

    async def track_result_click(
        self,
        search_query_id: str,
        chunk_id: str,
        user_id: str,
        result_position: int,
        similarity_score: float,
        rerank_score: float | None = None
    ) -> None:
        """Track when user clicks on a search result."""
        try:
            click_record = SearchResultClick(
                search_query_id=uuid.UUID(search_query_id),
                chunk_id=uuid.UUID(chunk_id),
                user_id=uuid.UUID(user_id),
                result_position=result_position,
                similarity_score=similarity_score,
                rerank_score=rerank_score,
                clicked_at=datetime.utcnow()
            )

            self.db.add(click_record)

            # Update chunk click count
            chunk = self.db.get(DocumentChunkEnhanced, uuid.UUID(chunk_id))
            if chunk:
                chunk.click_count += 1

            # Update search query
            search_query = self.db.get(SearchQuery, uuid.UUID(search_query_id))
            if search_query:
                search_query.user_clicked_result = True

            self.db.commit()

        except Exception as e:
            logger.error(f"Error tracking result click: {e}")

    async def get_search_analytics(
        self,
        user_id: str,
        days: int = 30
    ) -> dict[str, Any]:
        """Get search analytics for a user."""
        try:
            from datetime import timedelta

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            # Get search queries
            search_queries = self.db.exec(
                select(SearchQuery).where(
                    SearchQuery.user_id == uuid.UUID(user_id),
                    SearchQuery.created_at >= cutoff_date
                )
            ).all()

            # Calculate metrics
            total_searches = len(search_queries)
            avg_response_time = np.mean([q.response_time_ms for q in search_queries]) if search_queries else 0
            click_through_rate = len([q for q in search_queries if q.user_clicked_result]) / total_searches if total_searches > 0 else 0

            # Get top queries
            query_counts = {}
            for query in search_queries:
                query_counts[query.query_text] = query_counts.get(query.query_text, 0) + 1

            top_queries = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)[:10]

            return {
                "total_searches": total_searches,
                "avg_response_time_ms": round(avg_response_time, 2),
                "click_through_rate": round(click_through_rate, 3),
                "top_queries": top_queries,
                "period_days": days
            }

        except Exception as e:
            logger.error(f"Error getting search analytics: {e}")
            return {
                "total_searches": 0,
                "avg_response_time_ms": 0,
                "click_through_rate": 0,
                "top_queries": [],
                "period_days": days,
                "error": str(e)
            }

    async def delete_document_from_index(self, document_id: str, user_id: str) -> bool:
        """Delete document and its chunks from the vector index."""
        try:
            # Get all chunks for this document
            chunks = self.db.exec(
                select(DocumentChunkEnhanced).where(
                    DocumentChunkEnhanced.document_id == uuid.UUID(document_id),
                    DocumentChunkEnhanced.user_id == uuid.UUID(user_id)
                )
            ).all()

            # Delete from Qdrant
            chunk_ids = [str(chunk.id) for chunk in chunks]
            if chunk_ids:
                self.qdrant_client.delete(
                    collection_name=self.documents_collection,
                    points_selector=chunk_ids
                )

            # Delete from database (will cascade)
            for chunk in chunks:
                self.db.delete(chunk)

            self.db.commit()

            return True

        except Exception as e:
            logger.error(f"Error deleting document from index: {e}")
            return False

    async def get_collection_info(self) -> dict[str, Any]:
        """Get information about Qdrant collections."""
        try:
            collections = self.qdrant_client.get_collections()

            info = {}
            for collection in collections.collections:
                if collection.name in [self.documents_collection, self.training_collection]:
                    collection_info = self.qdrant_client.get_collection(collection.name)
                    info[collection.name] = {
                        "status": collection_info.status,
                        "vectors_count": collection_info.vectors_count,
                        "points_count": collection_info.points_count,
                        "segments_count": collection_info.segments_count,
                    }

            return info

        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"error": str(e)}

    async def health_check(self) -> dict[str, Any]:
        """Perform health check on RAG system components."""
        health = {
            "status": "healthy",
            "components": {},
            "timestamp": datetime.utcnow().isoformat()
        }

        # Check Qdrant
        try:
            collections = self.qdrant_client.get_collections()
            health["components"]["qdrant"] = {
                "status": "healthy",
                "collections": len(collections.collections)
            }
        except Exception as e:
            health["components"]["qdrant"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["status"] = "degraded"

        # Check Redis
        try:
            if self.redis_client:
                await self.redis_client.ping()
                health["components"]["redis"] = {"status": "healthy"}
            else:
                health["components"]["redis"] = {"status": "unavailable"}
        except Exception as e:
            health["components"]["redis"] = {
                "status": "unhealthy",
                "error": str(e)
            }

        # Check OpenAI
        try:
            # Simple test embedding
            test_embedding = await self.get_embedding("test")
            health["components"]["openai"] = {
                "status": "healthy",
                "embedding_dimension": len(test_embedding)
            }
        except Exception as e:
            health["components"]["openai"] = {
                "status": "unhealthy",
                "error": str(e)
            }
            health["status"] = "degraded"

        return health

    async def _database_only_search(
        self,
        query: str,
        user_id: str,
        ai_soul_id: str | None = None,
        filters: dict[str, Any] | None = None,
        limit: int = 10
    ) -> dict[str, Any]:
        """
        Fallback search using only database when Qdrant is not available.
        Uses simple text matching on chunk content.
        """
        start_time = time.time()

        try:
            # Simple text search using LIKE
            query_lower = query.lower()

            # Build base query
            stmt = select(DocumentChunkEnhanced).where(
                DocumentChunkEnhanced.user_id == uuid.UUID(user_id)
            )

            # Add text search condition
            stmt = stmt.where(
                DocumentChunkEnhanced.content.ilike(f"%{query}%")
            )

            # Execute query
            chunks = self.db.exec(stmt.limit(limit)).all()

            # Format results
            results = []
            for chunk in chunks:
                # Simple relevance scoring based on query term frequency
                content_lower = chunk.content.lower()
                query_terms = query_lower.split()
                score = sum(content_lower.count(term) for term in query_terms) / len(chunk.content)

                results.append({
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "content": chunk.content,
                    "similarity_score": min(score, 1.0),  # Cap at 1.0
                    "chunk_index": chunk.chunk_index,
                    "metadata": json.loads(chunk.chunk_metadata or "{}"),
                    "semantic_metadata": json.loads(chunk.semantic_metadata or "{}"),
                    "embedding_model": chunk.embedding_model,
                    "search_method": "database_only"
                })

            # Sort by relevance score
            results.sort(key=lambda x: x["similarity_score"], reverse=True)

            response = {
                "query": query,
                "results": results[:limit],
                "total_found": len(results),
                "response_time_ms": int((time.time() - start_time) * 1000),
                "search_algorithm": "database_only",
                "similarity_threshold": 0.0,
                "reranking_enabled": False
            }

            # Log search query
            await self._log_search_query(
                query, user_id, ai_soul_id, filters,
                len(results),
                response["response_time_ms"]
            )

            return response

        except Exception as e:
            logger.error(f"Error in database-only search: {e}")
            raise

    async def simple_hybrid_search(
        self,
        query: str,
        user_id: str,
        ai_soul_id: str | None = None,
        filters: dict[str, Any] | None = None,
        limit: int = 10
    ) -> dict[str, Any]:
        """
        Simple hybrid search that works even with missing dependencies.
        Falls back to database text search when vector search is unavailable.
        """
        start_time = time.time()

        try:
            # Ensure initialization
            await self._ensure_initialization()

            # If Qdrant is available, use the full hybrid search
            if self.qdrant_client:
                return await self.hybrid_search(query, user_id, ai_soul_id, filters, limit)

            # Fallback to database text search
            logger.info("Using fallback database text search")

            # Build database query
            query_conditions = [
                DocumentChunkEnhanced.user_id == uuid.UUID(user_id)
            ]

            if ai_soul_id:
                # Note: This would need a relationship to AI souls in the chunk model
                pass

            # Simple text search using LIKE
            text_search_query = select(DocumentChunkEnhanced).where(
                *query_conditions,
                DocumentChunkEnhanced.content.ilike(f"%{query}%")
            ).limit(limit)

            chunks = self.db.exec(text_search_query).all()

            # Convert to response format
            results = []
            for chunk in chunks:
                results.append({
                    "chunk_id": str(chunk.id),
                    "document_id": str(chunk.document_id),
                    "content": chunk.content,
                    "similarity_score": 0.5,  # Default score for text match
                    "chunk_index": chunk.chunk_index,
                    "metadata": json.loads(chunk.chunk_metadata or "{}"),
                    "semantic_metadata": json.loads(chunk.semantic_metadata or "{}"),
                    "embedding_model": chunk.embedding_model,
                    "search_method": "database_text_search"
                })

            response = {
                "query": query,
                "results": results,
                "total_found": len(results),
                "response_time_ms": int((time.time() - start_time) * 1000),
                "search_algorithm": "database_fallback",
                "similarity_threshold": 0.0,
                "reranking_enabled": False
            }

            # Log search query
            await self._log_search_query(
                query, user_id, ai_soul_id, filters,
                len(results),
                response["response_time_ms"]
            )

            return response

        except Exception as e:
            logger.error(f"Error in simple hybrid search: {e}")

            # Log failed search
            await self._log_search_query(
                query, user_id, ai_soul_id, filters, 0,
                int((time.time() - start_time) * 1000),
                error=str(e)
            )

            # Return empty results instead of raising
            return {
                "query": query,
                "results": [],
                "total_found": 0,
                "response_time_ms": int((time.time() - start_time) * 1000),
                "search_algorithm": "error_fallback",
                "similarity_threshold": 0.0,
                "reranking_enabled": False,
                "error": str(e)
            }

    def create_intelligent_chunks_sync(
        self,
        text: str,
        document_id: str,
        user_id: str,
        document_type: str = "general"
    ) -> list[DocumentChunkEnhanced]:
        """
        Synchronous version of intelligent chunking for Celery tasks.
        
        Args:
            text: Text content to chunk
            document_id: Document ID
            user_id: User ID
            document_type: Type of document
            
        Returns:
            List of DocumentChunkEnhanced objects
        """
        try:
            # Get configuration
            config = self.db.exec(
                select(RAGConfiguration).where(
                    RAGConfiguration.user_id == uuid.UUID(user_id),
                    RAGConfiguration.ai_soul_id.is_(None)
                )
            ).first()

            if not config:
                config = RAGConfiguration(
                    user_id=uuid.UUID(user_id),
                    chunking_strategy="semantic",
                    chunk_size=500,
                    chunk_overlap=50,
                    embedding_model="text-embedding-3-small"
                )

            # Simple chunking for sync operation
            chunks = []
            chunk_size = min(config.chunk_size, 3500)  # Database constraint
            overlap = config.chunk_overlap

            start = 0
            chunk_index = 0

            while start < len(text):
                end = start + chunk_size
                chunk_content = text[start:end]

                # Create chunk record
                if document_type == "training":
                    from app.models import TrainingDocumentChunkEnhanced
                    chunk = TrainingDocumentChunkEnhanced(
                        training_document_id=uuid.UUID(document_id),
                        ai_soul_id=None,  # Will be set by caller
                        user_id=uuid.UUID(user_id),
                        content=chunk_content,
                        chunk_index=chunk_index,
                        chunk_metadata=json.dumps({
                            "type": "simple",
                            "start_char": start,
                            "end_char": end
                        }),
                        embedding_model=config.embedding_model
                    )
                else:
                    chunk = DocumentChunkEnhanced(
                        document_id=uuid.UUID(document_id),
                        user_id=uuid.UUID(user_id),
                        content=chunk_content,
                        chunk_index=chunk_index,
                        chunk_metadata=json.dumps({
                            "type": "simple",
                            "start_char": start,
                            "end_char": end
                        }),
                        embedding_model=config.embedding_model
                    )

                chunks.append(chunk)
                start += chunk_size - overlap
                chunk_index += 1

            return chunks

        except Exception as e:
            logger.error(f"Error in sync chunking: {e}")
            raise

    def generate_embeddings_batch_sync(self, texts: list[str]) -> list[list[float]]:
        """
        Synchronous version of batch embedding generation for Celery tasks.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        try:
            from openai import OpenAI

            # Use sync OpenAI client
            client = OpenAI(api_key=settings.OPENAI_API_KEY)

            embeddings = []

            # Process in batches to avoid API limits
            batch_size = 100
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]

                response = client.embeddings.create(
                    model="text-embedding-3-small",
                    input=batch
                )

                batch_embeddings = [item.embedding for item in response.data]
                embeddings.extend(batch_embeddings)

            return embeddings

        except Exception as e:
            logger.error(f"Error in sync embedding generation: {e}")
            # Return zero vectors on error
            return [[0.0] * 1536 for _ in texts]

    def update_vector_database(self, chunks: list[DocumentChunkEnhanced]) -> None:
        """
        Update vector database with new chunks.
        
        Args:
            chunks: List of chunks to update in vector database
        """
        try:
            if not self.qdrant_client:
                logger.warning("Qdrant client not available - skipping vector database update")
                return

            points = []
            for chunk in chunks:
                if hasattr(chunk, 'embedding') and chunk.embedding:
                    try:
                        embedding = json.loads(chunk.embedding)
                        point = PointStruct(
                            id=str(chunk.id),
                            vector=embedding,
                            payload={
                                "document_id": str(chunk.document_id),
                                "user_id": str(chunk.user_id),
                                "chunk_index": chunk.chunk_index,
                                "content": chunk.content[:500],  # Truncated for payload
                                "created_at": chunk.created_at.isoformat()
                            }
                        )
                        points.append(point)
                    except json.JSONDecodeError:
                        logger.warning(f"Invalid embedding JSON for chunk {chunk.id}")

            if points:
                self.qdrant_client.upsert(
                    collection_name=self.documents_collection,
                    points=points
                )
                logger.info(f"Updated {len(points)} points in vector database")

        except Exception as e:
            logger.error(f"Error updating vector database: {e}")
