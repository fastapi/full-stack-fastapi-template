from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.api import deps
from app.core.ai_client import ChatManager, AnthropicClient, OpenAIClient
from app.core.config import settings

router = APIRouter(prefix="/learn", tags=["learn"])

# Store chat managers in memory for now
active_chats: dict[str, ChatManager] = {}

class ChatRequest(BaseModel):
    """Request model for chat streaming endpoint."""
    message: str
    system_prompt: str | None = None
    model: Literal["anthropic", "openai"] = "anthropic"

class ChatResponse(BaseModel):
    message: str

class TestResponse(BaseModel):
    anthropic_key_set: bool
    openai_key_set: bool
    anthropic_model: str
    openai_model: str
    test_message: str | None = None

class ChatStreamResponse(BaseModel):
    """Response model for individual stream messages."""
    type: Literal["content"]
    content: str

class ChatMessageResponse(BaseModel):
    """Response model for non-streaming chat messages."""
    message: str

class ChatStreamRequest(BaseModel):
    """Request model for chat streaming endpoint."""
    message: str
    system_prompt: str | None = None
    model: Literal["anthropic", "openai"] = "anthropic"
    
    class Config:
        schema_extra = {
            'example': {
                'message': 'Write a haiku about coding',
                'model': 'anthropic'
            }
        }

@router.get("/test", response_model=TestResponse)
async def test_configuration():
    """Test the LLM configuration and basic functionality."""
    response = TestResponse(
        anthropic_key_set=bool(settings.ANTHROPIC_API_KEY),
        openai_key_set=bool(settings.OPENAI_API_KEY),
        anthropic_model=settings.ANTHROPIC_MODEL,
        openai_model=settings.OPENAI_MODEL
    )
    
    # Test a simple message if keys are configured
    if response.anthropic_key_set:
        try:
            client = AnthropicClient()
            test_msg = await client.chat(
                messages=[{"role": "user", "content": "Say 'API test successful' in exactly those words"}],
                system="You must respond exactly as instructed"
            )
            response.test_message = test_msg
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Anthropic API test failed: {str(e)}")
    
    return response

@router.post("/chat", response_model=ChatMessageResponse)
async def chat_general(
    request: ChatRequest,
    current_user = Depends(deps.get_current_user),
):
    """
    Send a message to the AI and get a response.
    """
    chat_key = f"{current_user.id}_general"
    if chat_key not in active_chats:
        active_chats[chat_key] = ChatManager(client=request.model)
    
    response = await active_chats[chat_key].send_message(
        request.message,
        system=request.system_prompt
    )
    
    return ChatMessageResponse(message=response)

@router.post("/chat/stream",
    response_class=StreamingResponse,
    openapi_extra={
        'responses': {
            '200': {
                'description': 'Streaming response',
                'headers': {
                    'Transfer-Encoding': {
                        'schema': {
                            'type': 'string',
                            'enum': ['chunked']
                        }
                    }
                },
                'content': {
                    'text/event-stream': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string', 'enum': ['content']},
                                'content': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    }
)
async def chat_stream(
    request: ChatStreamRequest,
    current_user = Depends(deps.get_current_user),
) -> StreamingResponse:
    """
    Send a message to the AI and get a streaming response.
    Returns a StreamingResponse with Server-Sent Events containing partial messages.

    The stream will emit events in the format:
    data: {"type": "content", "content": "partial message..."}
    """
    chat_key = f"{current_user.id}_general"
    if chat_key not in active_chats:
        active_chats[chat_key] = ChatManager(client=request.model)
    
    return StreamingResponse(
        active_chats[chat_key].stream_message(
            request.message,
            system=request.system_prompt
        ),
        media_type='text/event-stream'
    )

@router.post("/{path_id}/chat/stream",
    openapi_extra={
        'responses': {
            '200': {
                'description': 'Streaming response',
                'content': {
                    'text/event-stream': {
                        'schema': {
                            'type': 'object',
                            'properties': {
                                'type': {'type': 'string', 'enum': ['content']},
                                'content': {'type': 'string'}
                            }
                        }
                    }
                }
            }
        }
    }
)
async def path_chat_stream(
    path_id: str,
    request: ChatRequest,
    current_user = Depends(deps.get_current_user),
) -> StreamingResponse:
    """
    Path-specific chat endpoint that maintains conversation context for each path.
    Returns a StreamingResponse with Server-Sent Events containing partial messages.
    """
    chat_key = f"{current_user.id}_{path_id}"
    if chat_key not in active_chats:
        active_chats[chat_key] = ChatManager(client=request.model)
    
    return StreamingResponse(
        active_chats[chat_key].stream_message(
            request.message,
            system=request.system_prompt
        ),
        media_type='text/event-stream'
    )
