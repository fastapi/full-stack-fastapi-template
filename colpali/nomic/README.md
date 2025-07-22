# ColNomic Server-Based Implementation

This implementation separates the ColQwen2.5 model loading from the main processing logic by using a FastAPI server. This approach prevents the need to reload the heavy model every time you make changes to your implementation.

## Architecture

- **`model_server.py`**: FastAPI server that loads the ColQwen2.5 model once and provides embedding endpoints
- **`model_client.py`**: Client library with helper functions to interact with the model server
- **`main.py`**: Your main processing logic that uses the model client
- **`start_server.py`**: Convenience script to start the model server

## Usage

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Model Server

```bash
python start_server.py
```

Or directly:
```bash
python model_server.py
```

The server will:
- Load the ColQwen2.5 model once on startup
- Provide endpoints at `http://localhost:8001`
- Keep the model in memory for fast inference

### 3. Run Your Main Script

In another terminal, run your main processing:

```bash
python main.py
```

The main script will now use the model server instead of loading the model directly.

## API Endpoints

The model server provides the following endpoints:

- `GET /health` - Check server health and model status
- `POST /embed/images` - Embed images and return original + mean pooled embeddings
- `POST /embed/queries` - Embed text queries

## Benefits

1. **Faster Development**: No need to reload the model when making changes to `main.py`
2. **Memory Efficiency**: Model stays loaded in one process
3. **Scalability**: Multiple clients can use the same model server
4. **Separation of Concerns**: Model serving is separate from business logic

## Development Workflow

1. Start the model server once: `python start_server.py`
2. Modify and run `main.py` as many times as needed
3. The model stays loaded and ready for inference
4. Stop the server with Ctrl+C when done

## Error Handling

The client includes proper error handling and will raise exceptions if:
- The model server is not running
- Network requests fail
- The server returns an error

Make sure the model server is running before executing `main.py`.
