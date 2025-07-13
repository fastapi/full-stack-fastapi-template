import json
import logging
import os
import uuid
from typing import Any

from fastapi import HTTPException, UploadFile
from openai import OpenAI
from PyPDF2 import PdfReader
from sqlmodel import Session, select

# ChromaDB removed - using Enhanced RAG with Qdrant instead
from app.core.config import settings
from app.models import (
    AISoulEntity,
    TrainingDocument,
    TrainingDocumentChunk,
    TrainingMessage,
)
from app.utils import get_file_hash
from app.models import User

logger = logging.getLogger(__name__)


class TrainingService:
    def __init__(self, db: Session):
        self.db = db
        self.upload_dir = os.path.join(settings.UPLOAD_DIR, "training")
        os.makedirs(self.upload_dir, exist_ok=True)
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

        # ChromaDB removed - Enhanced RAG with Qdrant will handle training data storage

    async def send_training_message(
        self,
        user_id: str,
        ai_soul_id: str,
        content: str,
        is_from_trainer: bool = True
    ) -> TrainingMessage:
        """Send a training message and generate embedding."""
        try:
            # Verify AI soul exists
            ai_soul = self.db.get(AISoulEntity, ai_soul_id)
            if not ai_soul:
                raise HTTPException(status_code=404, detail="AI Soul not found")

            # Get user to check role
            user = self.db.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check authorization: admins can train any soul, trainers can only train their own
            if not user.is_superuser and user.role not in ["admin", "super_admin"]:
                if ai_soul.user_id != uuid.UUID(user_id):
                    raise HTTPException(status_code=403, detail="Not authorized to train this AI soul")

            # Generate embedding for the message
            embedding = await self.generate_embedding(content)

            # Generate message ID
            message_id = str(uuid.uuid4())

            # Create training message
            training_message = TrainingMessage(
                id=uuid.UUID(message_id),
                content=content,
                is_from_trainer=is_from_trainer,
                ai_soul_id=uuid.UUID(ai_soul_id),
                user_id=uuid.UUID(user_id),
                embedding=json.dumps(embedding)
            )

            # Increment interaction count for this training conversation pair
            ai_soul.interaction_count += 1
            self.db.add(ai_soul)
            
            self.db.add(training_message)
            self.db.commit()
            self.db.refresh(training_message)

            # Generate AI response
            response_content = await self.generate_ai_response(content, ai_soul_id)
            response_embedding = await self.generate_embedding(response_content)

            # Generate response ID
            response_id = str(uuid.uuid4())

            # Create AI response message
            response_message = TrainingMessage(
                id=uuid.UUID(response_id),
                content=response_content,
                is_from_trainer=False,
                ai_soul_id=uuid.UUID(ai_soul_id),
                user_id=uuid.UUID(user_id),
                embedding=json.dumps(response_embedding)
            )

            self.db.add(response_message)
            self.db.commit()
            self.db.refresh(response_message)

            return training_message

        except Exception as e:
            logger.error(f"Error sending training message: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to send training message")

    async def generate_ai_response(self, user_message: str, ai_soul_id: str) -> str:
        """Generate AI response using similar training data."""
        try:
            # Get recent training messages for context (simple database query)
            recent_messages = self.db.exec(
                select(TrainingMessage)
                .where(TrainingMessage.ai_soul_id == uuid.UUID(ai_soul_id))
                .order_by(TrainingMessage.timestamp.desc())
                .limit(5)
            ).all()

            # Build context from recent messages
            context = "\n".join([
                f"{'Trainer' if msg.is_from_trainer else 'AI'}: {msg.content}"
                for msg in recent_messages
            ])

            # Generate response using OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI assistant trained to respond in a way that reflects the training data provided. Use the context to understand the communication style and preferences of the trainer."},
                    {"role": "user", "content": f"Context:\n{context}\n\nUser message: {user_message}\n\nRespond in a way that reflects the training data style:"}
                ]
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            return f"I understand. I'll learn from your message: \"{user_message}\". This helps me better understand your communication style and preferences."

    async def upload_training_document(
        self,
        file: UploadFile,
        user_id: str,
        ai_soul_id: str,
        description: str | None = None
    ) -> TrainingDocument:
        """Upload a training document and create initial database record."""
        try:
            # Verify AI soul exists
            ai_soul = self.db.get(AISoulEntity, ai_soul_id)
            if not ai_soul:
                raise HTTPException(status_code=404, detail="AI Soul not found")

            # Get user to check role
            user = self.db.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check authorization: admins can upload to any soul, trainers can only upload to their own
            if not user.is_superuser and user.role not in ["admin", "super_admin"]:
                if ai_soul.user_id != uuid.UUID(user_id):
                    raise HTTPException(status_code=403, detail="Not authorized to train this AI soul")

            # Validate file type
            allowed_types = ["application/pdf", "text/plain", "text/markdown"]
            # Some browsers send different MIME types for markdown
            if file.content_type not in allowed_types and not file.filename.endswith(('.txt', '.md', '.pdf')):
                raise HTTPException(
                    status_code=400,
                    detail="Only PDF, TXT, and Markdown files are supported"
                )

            # Read file content and validate
            content = await file.read()
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(status_code=400, detail="File too large")

            # Generate unique filename
            file_hash = get_file_hash(content)
            ext = os.path.splitext(file.filename)[1]
            filename = f"{file_hash}{ext}"
            file_path = os.path.join(self.upload_dir, filename)

            # Save file to disk
            with open(file_path, "wb") as f:
                f.write(content)

            # Create training document record
            training_document = TrainingDocument(
                filename=filename,
                original_filename=file.filename,
                file_size=len(content),
                content_type=file.content_type,
                description=description,
                file_path=file_path,
                ai_soul_id=uuid.UUID(ai_soul_id),
                user_id=uuid.UUID(user_id),
            )

            self.db.add(training_document)
            self.db.commit()
            self.db.refresh(training_document)

            # Start async processing
            await self.process_training_document(training_document)

            return training_document

        except Exception as e:
            logger.error(f"Error uploading training document: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to upload training document")

    async def process_training_document(self, training_document: TrainingDocument) -> None:
        """Process uploaded training document and create chunks with embeddings."""
        try:
            # Update status to processing
            training_document.processing_status = "processing"
            self.db.commit()

            # Extract text chunks based on file type
            if training_document.content_type == "application/pdf":
                chunks = self._extract_pdf_chunks(training_document.file_path)
            else:  # text/plain, text/markdown, or other text files
                chunks = self._extract_text_chunks(training_document.file_path)

            # Create chunks with embeddings
            for idx, (content, metadata) in enumerate(chunks):
                # Generate embedding for chunk
                embedding = await self.generate_embedding(content)

                # Generate chunk ID
                chunk_id = str(uuid.uuid4())

                chunk = TrainingDocumentChunk(
                    id=uuid.UUID(chunk_id),
                    training_document_id=training_document.id,
                    ai_soul_id=training_document.ai_soul_id,
                    user_id=training_document.user_id,
                    content=content,
                    chunk_index=idx,
                    chunk_metadata=json.dumps(metadata),
                    embedding=json.dumps(embedding)
                )
                self.db.add(chunk)

            # Update document status and chunk count
            training_document.processing_status = "completed"
            training_document.chunk_count = len(chunks)
            self.db.commit()

        except Exception as e:
            logger.error(f"Error processing training document: {str(e)}")
            training_document.processing_status = "failed"
            self.db.commit()
            raise

    def _extract_pdf_chunks(self, file_path: str) -> list[tuple[str, dict[str, Any]]]:
        """Extract text from PDF and split into optimized chunks for better context."""
        chunks = []

        try:
            with open(file_path, "rb") as file:
                pdf_reader = PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    
                    if text.strip():
                        # Enhanced chunking strategy for maximum context
                        # Use larger chunk size (1000 words) with 200-word overlap for better context
                        words = text.split()
                        chunk_size = 1000  # Increased from 200 for more context
                        overlap_size = 200  # Overlap for context continuity
                        
                        for i in range(0, len(words), chunk_size - overlap_size):
                            chunk_words = words[i:i + chunk_size]
                            chunk_text = " ".join(chunk_words)
                            
                            # Only create chunk if it has substantial content
                            if len(chunk_text.strip()) > 100:
                                metadata = {
                                    "page": page_num + 1,
                                    "chunk_start": i,
                                    "chunk_end": i + len(chunk_words),
                                    "chunk_size": len(chunk_words),
                                    "source": "pdf",
                                    "total_pages": len(pdf_reader.pages)
                                }
                                
                                chunks.append((chunk_text, metadata))

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from PDF: {str(e)}"
            )

        return chunks

    def _extract_text_chunks(self, file_path: str) -> list[tuple[str, dict[str, Any]]]:
        """Extract text from plain text file and split into optimized chunks."""
        chunks = []

        try:
            with open(file_path, encoding="utf-8") as file:
                text = file.read()

                # Enhanced chunking strategy for text files
                # Split by paragraphs first, then by words if needed
                paragraphs = text.split('\n\n')
                current_chunk = ""
                chunk_index = 0
                word_count = 0
                max_words_per_chunk = 1000  # Increased for more context
                overlap_words = 200
                
                for paragraph in paragraphs:
                    paragraph = paragraph.strip()
                    if not paragraph:
                        continue
                        
                    paragraph_words = len(paragraph.split())
                    
                    # If adding this paragraph would exceed limit, save current chunk
                    if word_count + paragraph_words > max_words_per_chunk and current_chunk:
                        metadata = {
                            "chunk_index": chunk_index,
                            "word_count": word_count,
                            "source": "text",
                            "chunk_type": "paragraph_based"
                        }
                        
                        chunks.append((current_chunk.strip(), metadata))
                        
                        # Start new chunk with overlap from previous chunk
                        words = current_chunk.split()
                        if len(words) > overlap_words:
                            overlap_text = " ".join(words[-overlap_words:])
                            current_chunk = overlap_text + "\n\n" + paragraph
                            word_count = overlap_words + paragraph_words
                        else:
                            current_chunk = paragraph
                            word_count = paragraph_words
                            
                        chunk_index += 1
                    else:
                        # Add paragraph to current chunk
                        if current_chunk:
                            current_chunk += "\n\n" + paragraph
                        else:
                            current_chunk = paragraph
                        word_count += paragraph_words
                
                # Add final chunk if it has content
                if current_chunk.strip():
                    metadata = {
                        "chunk_index": chunk_index,
                        "word_count": word_count,
                        "source": "text",
                        "chunk_type": "paragraph_based"
                    }
                    
                    chunks.append((current_chunk.strip(), metadata))

        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to extract text from file: {str(e)}"
            )

        return chunks

    async def generate_embedding(self, text: str) -> list[float]:
        """Generate embedding for text using OpenAI."""
        try:
            response = self.client.embeddings.create(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to generate embedding"
            )

    async def get_training_data(
        self,
        ai_soul_id: str,
        user_id: str,
        query: str,
        limit: int = 10
    ) -> list[dict[str, Any]]:
        """Get relevant training data for AI soul based on semantic similarity with strict isolation."""
        try:
            # Verify AI soul exists and get owner info
            ai_soul = self.db.get(AISoulEntity, ai_soul_id)
            if not ai_soul:
                raise HTTPException(status_code=404, detail="AI Soul not found")

            logger.info(f"Searching training data for AI soul {ai_soul_id} with query: '{query}'")
            logger.info(f"AI Soul owner: {ai_soul.user_id}, Requester: {user_id}")

            # Generate embedding for the query
            query_embedding = await self.generate_embedding(query)
            
            results = []

            # Get ONLY training messages for THIS specific AI soul (strict isolation)
            training_messages = self.db.exec(
                select(TrainingMessage)
                .where(
                    TrainingMessage.ai_soul_id == uuid.UUID(ai_soul_id),
                    TrainingMessage.embedding.is_not(None)
                )
                .order_by(TrainingMessage.timestamp.desc())
                .limit(100)  # Increased limit for better search
            ).all()

            logger.info(f"Found {len(training_messages)} training messages with embeddings for AI soul {ai_soul_id}")

            # Calculate semantic similarity for training messages
            for message in training_messages:
                try:
                    # Parse the stored embedding
                    message_embedding = json.loads(message.embedding)
                    
                    # Calculate cosine similarity
                    similarity = self.cosine_similarity(query_embedding, message_embedding)
                    
                    # Boost trainer messages slightly for better learning
                    if message.is_from_trainer:
                        similarity += 0.05
                    
                    # Only include results with reasonable similarity (lowered threshold for better recall)
                    if similarity > 0.25:  # Lowered from 0.3 for better recall
                        results.append({
                            "type": "message",
                            "content": message.content,
                            "similarity": similarity,
                            "timestamp": message.timestamp,
                            "is_from_trainer": message.is_from_trainer,
                            "ai_soul_id": str(message.ai_soul_id)  # Include for verification
                        })
                        
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to parse embedding for message {message.id}: {e}")
                    continue

            # Get ONLY training document chunks for THIS specific AI soul (strict isolation)
            training_chunks = self.db.exec(
                select(TrainingDocumentChunk)
                .where(
                    TrainingDocumentChunk.ai_soul_id == uuid.UUID(ai_soul_id),
                    TrainingDocumentChunk.embedding.is_not(None)
                )
                .limit(50)  # Increased limit for better search
            ).all()

            logger.info(f"Found {len(training_chunks)} document chunks with embeddings for AI soul {ai_soul_id}")

            # Calculate semantic similarity for document chunks
            for chunk in training_chunks:
                try:
                    # Parse the stored embedding
                    chunk_embedding = json.loads(chunk.embedding)
                    
                    # Calculate cosine similarity
                    similarity = self.cosine_similarity(query_embedding, chunk_embedding)
                    
                    # Only include results with reasonable similarity
                    if similarity > 0.25:  # Lowered threshold for better recall
                        results.append({
                            "type": "document",
                            "content": chunk.content,
                            "similarity": similarity,
                            "metadata": json.loads(chunk.chunk_metadata) if chunk.chunk_metadata else {},
                            "ai_soul_id": str(chunk.ai_soul_id)  # Include for verification
                        })
                        
                except (json.JSONDecodeError, TypeError) as e:
                    logger.warning(f"Failed to parse embedding for chunk {chunk.id}: {e}")
                    continue

            # Sort by similarity (highest first)
            results.sort(key=lambda x: x["similarity"], reverse=True)

            # Verify data isolation - all results should belong to the requested AI soul
            for result in results:
                if result.get("ai_soul_id") != ai_soul_id:
                    logger.error(f"Data isolation breach detected! Found data from soul {result.get('ai_soul_id')} in results for soul {ai_soul_id}")
                    raise HTTPException(status_code=500, detail="Data isolation error")

            logger.info(f"Returning {len(results[:limit])} relevant training results. Top scores: {[round(r['similarity'], 3) for r in results[:3]]}")
            return results[:limit]

        except Exception as e:
            logger.error(f"Error getting training data: {str(e)}")
            return []

    def cosine_similarity(self, vec1: list[float], vec2: list[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        try:
            import math

            dot_product = sum(a * b for a, b in zip(vec1, vec2, strict=False))
            magnitude1 = math.sqrt(sum(a * a for a in vec1))
            magnitude2 = math.sqrt(sum(a * a for a in vec2))

            if magnitude1 == 0 or magnitude2 == 0:
                return 0

            return dot_product / (magnitude1 * magnitude2)

        except Exception as e:
            logger.error(f"Error calculating cosine similarity: {str(e)}")
            return 0

    def get_training_messages(
        self,
        ai_soul_id: str,
        user_id: str,
        skip: int = 0,
        limit: int = 50
    ) -> list[TrainingMessage]:
        """Get training messages for an AI soul."""
        try:
            # Verify AI soul exists
            ai_soul = self.db.get(AISoulEntity, ai_soul_id)
            if not ai_soul:
                raise HTTPException(status_code=404, detail="AI Soul not found")

            # Get user to check role
            user = self.db.get(User, user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            # Check authorization: admins can view any soul's training, trainers can only view their own
            if not user.is_superuser and user.role not in ["admin", "super_admin"]:
                if ai_soul.user_id != uuid.UUID(user_id):
                    raise HTTPException(status_code=403, detail="Not authorized to access this AI soul")

            # Get training messages
            messages = self.db.exec(
                select(TrainingMessage)
                .where(TrainingMessage.ai_soul_id == uuid.UUID(ai_soul_id))
                .order_by(TrainingMessage.timestamp.desc())
                .offset(skip)
                .limit(limit)
            ).all()

            return list(messages)

        except Exception as e:
            logger.error(f"Error getting training messages: {str(e)}")
            return []
