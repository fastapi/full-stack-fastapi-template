import os
from typing import Optional

from gemini_provider import GeminiAIProvider  
from openai_provider import OpenAIProvider    
from base import AIProvider       
def get_active_provider() -> Optional[AIProvider]:
    """
    Trả về một AIProvider đã khởi tạo, dựa trên cấu hình môi trường.
    Ưu tiên OpenAI nếu có, fallback về Gemini nếu không.
    """
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print("[AI Service] Using GeminiAIProvider.")
        return GeminiAIProvider(api_key=gemini_key, model_name="gemini-2.5-flash")


    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("[AI Service] Using OpenAIProvider.")
        return OpenAIProvider(model_name="gpt-4o")
    print("[AI Service] No valid AI provider found.")
    return None
def get_ai_response(
    *, character: Character, history: list[Message]
) -> str:
    """
    Gọi phản hồi AI dựa trên character và lịch sử hội thoại.

    Args:
        character: Đối tượng nhân vật (Character) dùng để cung cấp system_prompt.
        history: Danh sách các tin nhắn lịch sử, bao gồm user message cuối.

    Returns:
        Chuỗi phản hồi từ AI.
    """
    provider = get_active_provider()

    if not provider:
        return "AI service is not available due to missing API configuration."

    print(f"\n[AI Service] Character: {character.name}")
    print(f"[AI Service] Provider: {type(provider).__name__}")

    try:
        response = provider.get_completion(character=character, history=history)
        return response
    except Exception as e:
        print(f"[AI Service] Error during response generation: {e}")
        return "An error occurred while generating the AI response."