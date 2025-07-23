"""
ColPali service for document embedding and search functionality.
"""
import uuid
from typing import Any

import numpy as np
import torch
from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
from datasets import load_dataset
from qdrant_client import QdrantClient, models
from tqdm import tqdm

from app.core.config import settings


class ColPaliService:
    """Service for ColPali document embedding and search operations."""
    
    def __init__(self):
        self.client = QdrantClient(url=settings.QDRANT_URL or "http://localhost:6333")
        self.model = None
        self.processor = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize ColPali model and processor."""
        if self.model is None:
            self.model = ColQwen2_5.from_pretrained(
                "nomic-ai/colnomic-embed-multimodal-3b",
                torch_dtype=torch.bfloat16,
                device_map="cuda:0" if torch.cuda.is_available() else "cpu"
            ).eval()
            
        if self.processor is None:
            self.processor = ColQwen2_5_Processor.from_pretrained(
                "nomic-ai/colnomic-embed-multimodal-3b"
            )
    
    def create_collection_if_not_exists(self, collection_name: str) -> bool:
        """Create a collection only if it doesn't already exist.
        
        Args:
            collection_name: Name of the collection to create
            
        Returns:
            bool: True if collection was created, False if it already existed
        """
        collections = self.client.get_collections().collections
        collection_names = [collection.name for collection in collections]
        
        if collection_name in collection_names:
            return False
        
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config={
                "original": models.VectorParams(
                    size=128,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    ),
                    hnsw_config=models.HnswConfigDiff(
                        m=0  # switching off HNSW
                    )
                ),
                "mean_pooling_columns": models.VectorParams(
                    size=128,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    )
                ),
                "mean_pooling_rows": models.VectorParams(
                    size=128,
                    distance=models.Distance.COSINE,
                    multivector_config=models.MultiVectorConfig(
                        comparator=models.MultiVectorComparator.MAX_SIM
                    )
                )
            }
        )
        return True
    
    def get_patches(self, image_size):
        """Get number of patches for an image."""
        return self.processor.get_n_patches(image_size, spatial_merge_size=self.model.spatial_merge_size)
    
    def pad_vectors_to_same_length(self, vectors_batch: list[list]) -> list[list]:
        """Pad vectors to the same length to avoid dimension inconsistencies."""
        if not vectors_batch:
            return vectors_batch
            
        max_length = max(len(vector) for vector in vectors_batch)
        padded_vectors = []
        
        for vector in vectors_batch:
            if len(vector) < max_length:
                # Pad with zeros
                padded_vector = vector + [[0.0] * len(vector[0])] * (max_length - len(vector))
                padded_vectors.append(padded_vector)
            else:
                padded_vectors.append(vector)
        
        return padded_vectors
    
    def embed_and_mean_pool_batch(self, image_batch):
        """Embed images and perform mean pooling."""
        # Embed
        with torch.no_grad():
            processed_images = self.processor.process_images(image_batch).to(self.model.device)
            image_embeddings = self.model(**processed_images)

        image_embeddings_batch = image_embeddings.cpu().float().numpy().tolist()

        # Mean pooling
        pooled_by_rows_batch = []
        pooled_by_columns_batch = []

        for image_embedding, tokenized_image, image in zip(
            image_embeddings, processed_images.input_ids, image_batch
        ):
            x_patches, y_patches = self.get_patches(image.size)

            image_tokens_mask = (tokenized_image == self.processor.image_token_id)
            image_tokens = image_embedding[image_tokens_mask].view(x_patches, y_patches, self.model.dim)
            
            pooled_by_rows = torch.mean(image_tokens, dim=0)
            pooled_by_columns = torch.mean(image_tokens, dim=1)

            image_token_idxs = torch.nonzero(image_tokens_mask.int(), as_tuple=False)
            first_image_token_idx = image_token_idxs[0].cpu().item()
            last_image_token_idx = image_token_idxs[-1].cpu().item()

            prefix_tokens = image_embedding[:first_image_token_idx]
            postfix_tokens = image_embedding[last_image_token_idx + 1:]

            # Adding back prefix and postfix special tokens
            pooled_by_rows = torch.cat(
                (prefix_tokens, pooled_by_rows, postfix_tokens), dim=0
            ).cpu().float().numpy().tolist()
            pooled_by_columns = torch.cat(
                (prefix_tokens, pooled_by_columns, postfix_tokens), dim=0
            ).cpu().float().numpy().tolist()

            pooled_by_rows_batch.append(pooled_by_rows)
            pooled_by_columns_batch.append(pooled_by_columns)

        return image_embeddings_batch, pooled_by_rows_batch, pooled_by_columns_batch
    
    def upload_batch(self, original_batch, pooled_by_rows_batch, pooled_by_columns_batch, 
                    payload_batch, collection_name: str) -> bool:
        """Upload a batch of vectors to Qdrant."""
        try:
            # Pad vectors to ensure consistent dimensions
            original_batch = self.pad_vectors_to_same_length(original_batch)
            pooled_by_rows_batch = self.pad_vectors_to_same_length(pooled_by_rows_batch)
            pooled_by_columns_batch = self.pad_vectors_to_same_length(pooled_by_columns_batch)
            
            # Convert to numpy arrays with explicit float32 dtype
            vectors = {
                "mean_pooling_columns": np.asarray(pooled_by_columns_batch, dtype=np.float32),
                "original": np.asarray(original_batch, dtype=np.float32),
                "mean_pooling_rows": np.asarray(pooled_by_rows_batch, dtype=np.float32)
            }
            
            self.client.upload_collection(
                collection_name=collection_name,
                vectors=vectors,
                payload=payload_batch,
                ids=[str(uuid.uuid4()) for _ in range(len(original_batch))]
            )
            return True
        except Exception as e:
            print(f"Error during upload: {e}")
            return False
    
    def batch_embed_query(self, query_batch):
        """Embed a batch of queries."""
        with torch.no_grad():
            processed_queries = self.processor.process_queries(query_batch).to(self.model.device)
            query_embeddings_batch = self.model(**processed_queries)
        return query_embeddings_batch.cpu().float().numpy()
    
    def reranking_search_batch(self, query_batch, collection_name: str, 
                              search_limit: int = 20, prefetch_limit: int = 200):
        """Perform reranking search on a batch of queries."""
        search_queries = [
            models.QueryRequest(
                query=query,
                prefetch=[
                    models.Prefetch(
                        query=query,
                        limit=prefetch_limit,
                        using="mean_pooling_columns"
                    ),
                    models.Prefetch(
                        query=query,
                        limit=prefetch_limit,
                        using="mean_pooling_rows"
                    ),
                ],
                limit=search_limit,
                with_payload=True,
                with_vector=False,
                using="original"
            ) for query in query_batch
        ]
        return self.client.query_batch_points(
            collection_name=collection_name,
            requests=search_queries
        )
    
    def upload_dataset(self, dataset_name: str, collection_name: str, batch_size: int = 4) -> dict[str, Any]:
        """Upload a dataset to Qdrant collection."""
        # Create collection if it doesn't exist
        self.create_collection_if_not_exists(collection_name)
        
        # Load dataset
        dataset = load_dataset(dataset_name, split="train")
        
        successful_uploads = 0
        total_items = len(dataset)
        
        with tqdm(total=total_items, desc=f"Uploading \"{dataset_name}\" to \"{collection_name}\"") as pbar:
            for i in range(0, total_items, batch_size):
                batch = dataset[i : i + batch_size]
                image_batch = batch["image"]
                current_batch_size = len(image_batch)
                
                try:
                    # Process batch
                    original_batch, pooled_by_rows_batch, pooled_by_columns_batch = self.embed_and_mean_pool_batch(
                        image_batch
                    )
                    
                    # Create payload with source and index information
                    payload_batch = [{"source": dataset_name, "index": i + j} 
                                   for j in range(current_batch_size)]
                    
                    # Upload batch
                    success = self.upload_batch(
                        original_batch,
                        pooled_by_rows_batch,
                        pooled_by_columns_batch,
                        payload_batch,
                        collection_name
                    )
                    
                    if success:
                        successful_uploads += current_batch_size
                        
                except Exception as e:
                    print(f"Error processing batch starting at index {i}: {e}")
                    continue
                    
                pbar.update(current_batch_size)
        
        return {
            "total_uploaded": successful_uploads,
            "total_items": total_items,
            "success": successful_uploads > 0
        }
    
    def search(self, query: str, collection_name: str, search_limit: int = 20, 
              prefetch_limit: int = 200) -> list[dict[str, Any]]:
        """Search for documents using ColPali."""
        # Embed query
        query_embeddings = self.batch_embed_query([query])
        
        # Perform search
        search_results = self.reranking_search_batch(
            query_embeddings, collection_name, search_limit, prefetch_limit
        )
        
        # Format results
        results = []
        if search_results and len(search_results) > 0:
            for point in search_results[0].points:
                results.append({
                    "id": point.id,
                    "score": point.score,
                    "payload": point.payload
                })
        
        return results


# Global service instance
colpali_service = ColPaliService()
