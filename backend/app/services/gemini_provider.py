
import os
import google.generativeai as genai
from typing import Sequence, Any

from .ai_service import AIProvider, Character, Message


class GeminiAIProvider:
    def __init__(self, api_key: str, model_name: str = 'gemini-2.5-flash'):
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name

    def _format_history_for_gemini(self, history: Sequence[Message]) -> list[dict[str, Any]]:
        gemini_history = []
        for message in history:
            role = 'user' if message.sender == 'user' else 'model'
            gemini_history.append({'role': role, 'parts': [message.content]})
        return gemini_history

    def get_completion(self, character: Character, history: Sequence[Message]) -> str:
        if not history:
            return "Error: No conversation history."

        last_message = history[-1]

        if last_message.sender != 'user':
             print(f"Warning: Gemini provider expects last message from user, but got {last_message.sender}.")
             last_user_message_content = None
             context_history_for_api = []
             found_last_user = False

             for msg in reversed(history):
                  if msg.sender == 'user' and not found_last_user:
                       last_user_message_content = msg.content
                       found_last_user = True
                  elif found_last_user:
                       role = 'user' if msg.sender == 'user' else 'model'
                       context_history_for_api.append({'role': role, 'parts': [msg.content]})

             if not found_last_user or last_user_message_content is None:
                 return "Error: No user message found in history for Gemini."

             context_history_for_api.reverse()

             formatted_context_history = context_history_for_api
             current_user_prompt = last_user_message_content

        else:
            formatted_context_history = self._format_history_for_gemini(history[:-1])
            current_user_prompt = last_message.content


        system_instruction = character.system_prompt

        try:
            chat = self.model.start_chat(history=formatted_context_history,
                                         system_instruction=system_instruction)
            response = chat.send_message(current_user_prompt)
            ai_response_text = response.text

            if not ai_response_text:
                 print("Warning: Gemini API returned no text.")
                 return "I cannot generate a response for that request."

            return ai_response_text

        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return "Sorry, I encountered an error with the AI service."