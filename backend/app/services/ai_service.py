# Placeholder for AI service integration logic 

import uuid
from typing import Sequence

from app.models import Character, Message


def get_ai_response(
    *, character: Character, history: Sequence[Message]
) -> str:
    """
    Placeholder function to simulate getting a response from an AI model.

    Args:
        character: The character the user is talking to.
        history: A sequence of recent messages in the conversation.

    Returns:
        A string containing the AI's response.
    """
    last_user_message = next((msg.content for msg in reversed(history) if msg.sender == "user"), None)

    response = (
        f"Okay, you said: '{last_user_message}'. As {character.name}, I'm still under development!"
        if last_user_message
        else f"Hi! I'm {character.name}. Thanks for starting a chat!"
    )
    print(f"---> AI Service called for Character: {character.name}")
    print(f"---> History: {[(msg.sender, msg.content) for msg in history]}")
    print(f"---> AI Response: {response}")

    return response 