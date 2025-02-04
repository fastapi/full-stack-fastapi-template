from typing import AsyncGenerator, Dict, Protocol, Literal
from typing import Literal, TypedDict
from anthropic import Anthropic
from openai import AsyncOpenAI
from app.core.config import settings

class Message(TypedDict):
    role: Literal["user", "assistant", "system"]
    content: str

class BaseAIClient:
    async def chat(self, messages: list[Message], system: str | None = None) -> str:
        raise NotImplementedError

class AnthropicClient(BaseAIClient):
    def __init__(self):
        self.client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
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
