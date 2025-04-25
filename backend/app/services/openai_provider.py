
import os
from openai import OpenAI
from typing import Sequence, Any

from .ai_service import AIProvider, Character, Message


class OpenAIProvider:
    def __init__(self, api_key: str, model_name: str = 'gpt-4.5-turbo'):
        self.client = OpenAI(api_key=api_key)
        self.model_name = model_name

    def _format_history_for_openai(self, character: Character, history: Sequence[Message]) -> list[dict[str, str]]:
        openai_history = []
        if character.system_prompt:
            openai_history.append({"role": "system", "content": character.system_prompt})

        for message in history:
            role = 'user' if message.sender == 'user' else 'assistant'
            openai_history.append({"role": role, "content": message.content})

        return openai_history

    def get_completion(self, character: Character, history: Sequence[Message]) -> str:
        if not history:
            return "Error: No conversation history provided."
        messages = self._format_history_for_openai(character, history)

        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages
            )
            ai_response_text = response.choices[0].message.content

            if not ai_response_text:
                print("Warning: OpenAI API returned no text.")
                return "I cannot generate a response for that request."


            return ai_response_text

        except Exception as e:
            print(f"Error calling OpenAI API: {e}")
            return "Sorry, I encountered an erro."