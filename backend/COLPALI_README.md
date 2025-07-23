# ColPali Integration

This document describes the ColPali integration added to the FastAPI template, providing multimodal document embedding and search capabilities.

## Overview

ColPali is a multimodal document retrieval system that combines vision and language understanding to enable semantic search over documents containing both text and images. This integration provides:

- **Document Embedding**: Process and embed documents using ColPali's multimodal approach
- **Semantic Search**: Search through embedded documents using natural language queries
- **Vector Storage**: Store embeddings in Qdrant vector database with optimized configurations
- **Batch Processing**: Efficient batch processing with dimension consistency handling

## API Endpoints

### Authentication
All ColPali endpoints require authentication using the same JWT token system as other API endpoints.

### Core Endpoints

#### `POST /api/v1/colpali/search`
Search for documents using natural language queries.

**Request Body:**
```json
{
  "query": "Megalithic statues on Pasqua Island",
  "collection_name": "le-collection",
  "search_limit": 20,
  "prefetch_limit": 200
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "uuid-string",
      "score": 0.85,
      "payload": {
        "source": "dataset-name",
        "index": 42
      }
    }
  ],
  "query": "Megalithic statues on Pasqua Island",
  "collection_name": "le-collection",
  "total_results": 15
}
```

#### `POST /api/v1/colpali/upload`
Upload and embed a dataset into a Qdrant collection.

**Request Body:**
```json
{
  "dataset_name": "davanstrien/ufo-ColPali",
  "collection_name": "le-collection",
  "batch_size": 4
}
```

**Response:**
```json
{
  "message": "Upload completed. 1000 out of 1000 items uploaded successfully.",
  "collection_name": "le-collection",
  "total_uploaded": 1000,
  "total_items": 1000,
  "success": true
}
```

### Collection Management

#### `GET /api/v1/colpali/collections`
List all available collections.

#### `GET /api/v1/colpali/collections/{collection_name}/info`
Get detailed information about a specific collection.

#### `POST /api/v1/colpali/collections/{collection_name}/create`
Create a new empty collection with ColPali vector configuration.

#### `DELETE /api/v1/colpali/collections/{collection_name}`
Delete a collection (superuser only).

### Health Check

#### `GET /api/v1/colpali/health`
Check the health status of ColPali service components.

## Configuration

### Environment Variables

Add these to your `.env` file:

```env
# Qdrant Configuration
QDRANT_URL=http://localhost:6333
```

### Qdrant Setup

1. **Using Docker:**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

2. **Using Docker Compose:**
Add to your `docker-compose.yml`:
```yaml
services:
  qdrant:
    image: qdrant/qdrant
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
volumes:
  qdrant_data:
```

## Installation

1. **Install Dependencies:**
```bash
cd backend
uv sync
```

2. **GPU Support (Optional but Recommended):**
For better performance, ensure CUDA is available:
```bash
# Check CUDA availability
python -c "import torch; print(torch.cuda.is_available())"
```

## Usage Examples

### Python Client Example

```python
import httpx

# Authentication
auth_response = httpx.post("http://localhost:8000/api/v1/login/access-token", 
                          data={"username": "user@example.com", "password": "password"})
token = auth_response.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Search documents
search_response = httpx.post(
    "http://localhost:8000/api/v1/colpali/search",
    json={
        "query": "ancient monuments",
        "collection_name": "le-collection",
        "search_limit": 10
    },
    headers=headers
)
results = search_response.json()
```

### cURL Example

```bash
# Get access token
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/login/access-token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=password" | jq -r '.access_token')

# Search documents
curl -X POST "http://localhost:8000/api/v1/colpali/search" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "ancient monuments",
    "collection_name": "le-collection",
    "search_limit": 10
  }'
```

## Architecture

### Components

1. **ColPali Service** (`app/services/colpali.py`):
   - Handles model initialization and inference
   - Manages vector embedding and search operations
   - Implements batch processing with dimension consistency

2. **API Routes** (`app/api/routes/colpali.py`):
   - RESTful endpoints for search and upload operations
   - Collection management endpoints
   - Health check and monitoring

3. **Models** (`app/models.py`):
   - Pydantic models for request/response validation
   - Type safety and API documentation

### Vector Configuration

The system uses three vector types for optimal search performance:

- **original**: Raw ColPali embeddings with multi-vector configuration
- **mean_pooling_rows**: Row-wise mean pooled embeddings
- **mean_pooling_columns**: Column-wise mean pooled embeddings

### Search Strategy

The search uses a reranking approach:
1. **Prefetch**: Retrieve candidates using mean-pooled vectors
2. **Rerank**: Final ranking using original embeddings
3. **Results**: Return top-k results with scores and metadata

## Performance Considerations

### Batch Processing
- Default batch size: 4 (adjustable based on GPU memory)
- Automatic dimension padding to handle inconsistent vector lengths
- Progress tracking with tqdm

### Memory Management
- Models loaded once and reused across requests
- Efficient tensor operations with proper device management
- Automatic cleanup of intermediate tensors

### Scaling
- Stateless service design for horizontal scaling
- Background task support for long-running uploads
- Connection pooling for Qdrant client

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory:**
   - Reduce batch_size in upload requests
   - Use CPU-only mode by setting `device_map="cpu"`

2. **Dimension Inconsistency Errors:**
   - The service automatically handles this with vector padding
   - Check logs for detailed error information

3. **Qdrant Connection Issues:**
   - Verify Qdrant is running on the configured URL
   - Check firewall and network connectivity

### Monitoring

Use the health check endpoint to monitor service status:
```bash
curl http://localhost:8000/api/v1/colpali/health
```

## Development

### Adding New Features

1. **New Embedding Models:**
   - Modify `ColPaliService._initialize_model()`
   - Update vector configurations in `create_collection_if_not_exists()`

2. **Custom Search Strategies:**
   - Extend `reranking_search_batch()` method
   - Add new search endpoints in the router

3. **Additional Vector Stores:**
   - Create new service implementations
   - Maintain the same interface for consistency

### Testing

```bash
# Run tests
cd backend
python -m pytest tests/

# Test specific ColPali functionality
python -m pytest tests/test_colpali.py -v
```

## Security Considerations

- All endpoints require authentication
- Collection deletion restricted to superusers
- Input validation and sanitization
- Rate limiting recommended for production

## License

This integration follows the same license as the main FastAPI template project.
