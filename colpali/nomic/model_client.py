"""
ColNomic Model Client
Client functions to interact with the ColNomic model server.
"""

import requests
import base64
from io import BytesIO
from PIL import Image
from typing import List, Tuple
import numpy as np

class ModelClient:
    def __init__(self, server_url: str = "http://localhost:8001"):
        self.server_url = server_url
    
    def pil_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffer = BytesIO()
        image.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        return img_str
    
    def health_check(self) -> dict:
        """Check if the model server is healthy."""
        response = requests.get(f"{self.server_url}/health")
        response.raise_for_status()
        return response.json()
    
    def embed_and_mean_pool_batch(self, image_batch: List[Image.Image]) -> Tuple[List, List, List]:
        """
        Embed a batch of images and return original embeddings plus mean pooled versions.
        
        Args:
            image_batch: List of PIL Images
            
        Returns:
            Tuple of (original_embeddings, pooled_by_rows, pooled_by_columns)
        """
        # Convert images to base64
        base64_images = [self.pil_to_base64(img) for img in image_batch]
        
        # Make request to server
        response = requests.post(
            f"{self.server_url}/embed/images",
            json={"images": base64_images}
        )
        response.raise_for_status()
        
        result = response.json()
        return (
            result["original_embeddings"],
            result["pooled_by_rows"], 
            result["pooled_by_columns"]
        )
    
    def batch_embed_query(self, query_batch: List[str]) -> np.ndarray:
        """
        Embed a batch of queries.
        
        Args:
            query_batch: List of query strings
            
        Returns:
            NumPy array of embeddings
        """
        response = requests.post(
            f"{self.server_url}/embed/queries",
            json={"queries": query_batch}
        )
        response.raise_for_status()
        
        result = response.json()
        return np.array(result["embeddings"], dtype=np.float32)

# Global client instance
model_client = ModelClient()
