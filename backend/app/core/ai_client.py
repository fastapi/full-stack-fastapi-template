from typing import AsyncGenerator, Dict, Protocol, Literal
from typing import Literal, TypedDict
from anthropic import AsyncAnthropic
from openai import AsyncOpenAI
from app.core.config import settings
import json
import logging

logger = logging.getLogger(__name__)

class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

class BaseAIClient(Protocol):
    async def chat(self, messages: list[Message], system: str | None = None) -> str:
        raise NotImplementedError
        
    async def chat_stream(self, messages: list[Message], system: str | None = None) -> AsyncGenerator[str, None]:
        raise NotImplementedError

class AnthropicClient(BaseAIClient):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
    
    async def chat(self, messages: list[Message], system: str | None = None) -> str:
        response = await self.client.messages.create(
            model=self.model,
            max_tokens=settings.MAX_TOKENS,
            temperature=settings.TEMPERATURE,
            system=system,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages]
        )
        return response.content[0].text

    async def chat_stream(self, messages: list[Message], system: str | None = None) -> AsyncGenerator[str, None]:
        """Stream chat responses."""
        request_params = {
            'messages': [{"role": m["role"], "content": m["content"]} for m in messages],
            'model': self.model,
            'max_tokens': settings.MAX_TOKENS,
            'temperature': settings.TEMPERATURE,
        }
        if system:
            request_params['system'] = system
        
        async with self.client.messages.stream(**request_params) as stream:
            async for text in stream.text_stream:
                yield f"data: {json.dumps({'type': 'content', 'content': text})}\n\n"
            
            # Get the final message for history
            message = await stream.get_final_message()
            self.add_message("assistant", message.content)  # Add to history
            yield f"data: {json.dumps({'type': 'done', 'content': ''})}\n\n"

class OpenAIClient(BaseAIClient):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def chat(self, messages: list[Message], system: str | None = None) -> str:
        if system:
            messages = [{"role": "system", "content": system}, *messages]
            
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages]
        )
        return response.choices[0].message.content

    async def chat_stream(self, messages: list[Message], system: str | None = None) -> AsyncGenerator[str, None]:
        """Stream chat responses."""
        if system:
            messages = [{"role": "system", "content": system}, *messages]
            
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=settings.TEMPERATURE,
            max_tokens=settings.MAX_TOKENS,
            messages=[{"role": m["role"], "content": m["content"]} for m in messages],
            stream=True
        )
        async for chunk in response:
            if chunk.choices:
                yield chunk.choices[0].delta.content

class ChatManager:
    def __init__(self, client: Literal["anthropic", "openai"] = "anthropic"):
        self.history: list[Message] = []
        self.client = AnthropicClient() if client == "anthropic" else OpenAIClient()
    
    def add_message(self, role: Literal["user", "assistant", "system"], content: str):
        self.history.append({"role": role, "content": content})
    
    async def send_message(self, content: str, system: str | None = None) -> str:
        self.add_message("user", content)
        response = await self.client.chat(self.history, system)
        self.add_message("assistant", response)
        return response

    async def stream_message(self, content: str, system: str | None = None) -> AsyncGenerator[str, None]:
        """Stream a message response."""
        self.add_message("user", content)
        async for chunk in self.client.chat_stream(self.history, system):
            yield chunk
        # Add the complete message to history after streaming
        if self.history[-1]["role"] == "user":
            last_chunk = None
            async for chunk in self.client.chat_stream(self.history, system):
                last_chunk = chunk
            self.add_message("assistant", last_chunk)  # Add the last chunk as the complete response
