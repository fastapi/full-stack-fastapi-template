from typing import Literal
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.api import deps
from app.core.ai_client import ChatManager, AnthropicClient, OpenAIClient
from app.core.config import settings

router = APIRouter(tags=["learn"])

# Store chat managers in memory for now
active_chats: dict[str, ChatManager] = {}

class ChatRequest(BaseModel):
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

@router.get("/learn/test", response_model=TestResponse)
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

@router.post("/learn/chat", response_model=ChatResponse)
async def chat_general(
    request: ChatRequest,
    current_user = Depends(deps.get_current_user),
):
    """General purpose chat endpoint without path context."""
    chat_key = f"{current_user.id}_general"
    if chat_key not in active_chats:
        active_chats[chat_key] = ChatManager(client=request.model)
    
    response = await active_chats[chat_key].send_message(
        request.message,
        system=request.system_prompt
    )
    
    return ChatResponse(message=response)

@router.post("/learn/{path_id}", response_model=ChatResponse)
async def chat(
    path_id: str,
    request: ChatRequest,
    current_user = Depends(deps.get_current_user),
):
    """Path-specific chat endpoint that maintains conversation context for each path."""
    chat_key = f"{current_user.id}_{path_id}"
    if chat_key not in active_chats:
        active_chats[chat_key] = ChatManager(client=request.model)
    
    response = await active_chats[chat_key].send_message(
        request.message,
        system=request.system_prompt
    )
    
    return ChatResponse(message=response)
