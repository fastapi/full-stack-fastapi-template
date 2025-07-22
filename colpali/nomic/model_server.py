"""
ColNomic Model Server
A FastAPI server that loads the ColQwen2.5 model once and provides embedding endpoints.
This prevents the need to reload the model on every script execution.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Any, AsyncIterator
import torch
import numpy as np
from colpali_engine.models import ColQwen2_5, ColQwen2_5_Processor
import uvicorn
import base64
from io import BytesIO
from PIL import Image

# Global model variables
colqwen_model = None
colqwen_processor = None

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan context manager for FastAPI app."""
    global colqwen_model, colqwen_processor
    
    # Startup
    print("Loading ColQwen2.5 model...")
    colqwen_model = ColQwen2_5.from_pretrained(
        "nomic-ai/colnomic-embed-multimodal-3b",
        torch_dtype=torch.bfloat16,
        device_map="cuda:0" if torch.cuda.is_available() else "cpu"
    ).eval()
    
    colqwen_processor = ColQwen2_5_Processor.from_pretrained("nomic-ai/colnomic-embed-multimodal-3b")
    print("Model loaded successfully!")
    
    yield  # This is where the application runs
    
    # Shutdown
    if colqwen_model is not None:
        del colqwen_model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    print("Model unloaded successfully!")

app = FastAPI(
    title="ColNomic Model Server",
    version="1.0.0",
    lifespan=lifespan
)

class EmbedImagesRequest(BaseModel):
    images: List[str]  # Base64 encoded images
    
class EmbedQueriesRequest(BaseModel):
    queries: List[str]

class EmbedImagesResponse(BaseModel):
    original_embeddings: List[List[float]]
    pooled_by_rows: List[List[float]]
    pooled_by_columns: List[List[float]]

class EmbedQueriesResponse(BaseModel):
    embeddings: List[List[float]]

def get_patches(image_size, model_processor, model):
    """Get the number of patches for an image."""
    return model_processor.get_n_patches(image_size,
                                       spatial_merge_size=model.spatial_merge_size)

def base64_to_pil(base64_string: str) -> Image.Image:
    """Convert base64 string to PIL Image."""
    image_data = base64.b64decode(base64_string)
    image = Image.open(BytesIO(image_data))
    return image

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "model_loaded": colqwen_model is not None,
        "device": str(colqwen_model.device) if colqwen_model else None
    }

@app.post("/embed/images", response_model=EmbedImagesResponse)
async def embed_images(request: EmbedImagesRequest):
    """Embed images and return original embeddings plus mean pooled versions."""
    if colqwen_model is None or colqwen_processor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Convert base64 images to PIL Images
        image_batch = [base64_to_pil(img_b64) for img_b64 in request.images]
        
        # Embed images
        with torch.no_grad():
            processed_images = colqwen_processor.process_images(image_batch).to(colqwen_model.device)
            image_embeddings = colqwen_model(**processed_images)

        image_embeddings_batch = image_embeddings.cpu().float().numpy().tolist()

        # Mean pooling
        pooled_by_rows_batch = []
        pooled_by_columns_batch = []

        for image_embedding, tokenized_image, image in zip(image_embeddings,
                                                           processed_images.input_ids,
                                                           image_batch):
            x_patches, y_patches = get_patches(image.size, colqwen_processor, colqwen_model)

            image_tokens_mask = (tokenized_image == colqwen_processor.image_token_id)
            image_tokens = image_embedding[image_tokens_mask].view(x_patches, y_patches, colqwen_model.dim)
            
            pooled_by_rows = torch.mean(image_tokens, dim=0)
            pooled_by_columns = torch.mean(image_tokens, dim=1)

            image_token_idxs = torch.nonzero(image_tokens_mask.int(), as_tuple=False)
            first_image_token_idx = image_token_idxs[0].cpu().item()
            last_image_token_idx = image_token_idxs[-1].cpu().item()

            prefix_tokens = image_embedding[:first_image_token_idx]
            suffix_tokens = image_embedding[last_image_token_idx + 1:]

            pooled_by_rows_with_context = torch.cat([prefix_tokens, pooled_by_rows.flatten(), suffix_tokens])
            pooled_by_columns_with_context = torch.cat([prefix_tokens, pooled_by_columns.flatten(), suffix_tokens])

            pooled_by_rows_batch.append(pooled_by_rows_with_context.cpu().float().numpy().tolist())
            pooled_by_columns_batch.append(pooled_by_columns_with_context.cpu().float().numpy().tolist())

        return EmbedImagesResponse(
            original_embeddings=image_embeddings_batch,
            pooled_by_rows=pooled_by_rows_batch,
            pooled_by_columns=pooled_by_columns_batch
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing images: {str(e)}")

@app.post("/embed/queries", response_model=EmbedQueriesResponse)
async def embed_queries(request: EmbedQueriesRequest):
    """Embed text queries."""
    if colqwen_model is None or colqwen_processor is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        with torch.no_grad():
            processed_queries = colqwen_processor.process_queries(request.queries).to(colqwen_model.device)
            query_embeddings_batch = colqwen_model(**processed_queries)
        
        embeddings = query_embeddings_batch.cpu().float().numpy().tolist()
        
        return EmbedQueriesResponse(embeddings=embeddings)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing queries: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
