"""AI service: embeddings (OpenAI) and LLM features (Anthropic)."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import anthropic
from openai import AsyncOpenAI

from app.core.config import settings

if TYPE_CHECKING:
    from app.models import Race, UserProfile

logger = logging.getLogger(__name__)

_openai_client: AsyncOpenAI | None = None
_anthropic_client: anthropic.AsyncAnthropic | None = None


def _openai() -> AsyncOpenAI:
    global _openai_client
    if _openai_client is None:
        _openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    return _openai_client


def _anthropic() -> anthropic.AsyncAnthropic:
    global _anthropic_client
    if _anthropic_client is None:
        _anthropic_client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
    return _anthropic_client


async def embed_text(text: str) -> list[float]:
    """Return an embedding vector for an arbitrary text string."""
    response = await _openai().embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text[:8191],  # max token limit guard
        dimensions=settings.EMBEDDING_DIMENSIONS,
    )
    return response.data[0].embedding


async def embed_race(race: "Race") -> list[float]:
    """Build a rich text representation of a race and embed it."""
    parts: list[str] = [race.name]
    if race.description:
        parts.append(race.description)
    if race.location:
        parts.append(f"Location: {race.location}")
    if race.terrain_type:
        parts.append(f"Terrain: {race.terrain_type.value}")
    if race.difficulty_level:
        parts.append(f"Difficulty: {race.difficulty_level.value}")
    if race.elevation_gain_m:
        parts.append(f"Elevation gain: {race.elevation_gain_m}m")
    text = " | ".join(parts)
    return await embed_text(text)


def _race_summary_block(race: "Race") -> str:
    lines = [f"Race: {race.name}"]
    if race.description:
        lines.append(f"Description: {race.description[:500]}")
    if race.location:
        lines.append(f"Location: {race.location}")
    if race.terrain_type:
        lines.append(f"Terrain: {race.terrain_type.value}")
    if race.difficulty_level:
        lines.append(f"Difficulty: {race.difficulty_level.value}")
    if race.elevation_gain_m:
        lines.append(f"Elevation gain: {race.elevation_gain_m}m")
    return "\n".join(lines)


async def generate_race_recommendation_explanation(
    race: "Race",
    profile: "UserProfile | None",
) -> str:
    """Return a 1-2 sentence explanation of why this race matches the user."""
    race_block = _race_summary_block(race)

    profile_lines: list[str] = []
    if profile:
        if profile.fitness_level:
            profile_lines.append(f"Fitness level: {profile.fitness_level.value}")
        if profile.distance_preference:
            profile_lines.append(f"Distance preference: {profile.distance_preference.value}")
        if profile.terrain_preference:
            profile_lines.append(f"Terrain preference: {profile.terrain_preference.value}")
    profile_block = "\n".join(profile_lines) if profile_lines else "No profile available."

    # System block is cacheable; user block contains dynamic profile.
    system_prompt = (
        "You are a race recommendation assistant for Vietnamese running events. "
        "Given a race's details and a runner's profile, write 1-2 sentences "
        "explaining why this race is a good match. Be specific and encouraging. "
        "Output only the explanation, no preamble."
    )

    response = await _anthropic().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=150,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Race details:\n{race_block}\n\n"
                    f"Runner profile:\n{profile_block}\n\n"
                    "Why is this race a good match?"
                ),
            }
        ],
    )
    block = response.content[0]
    return block.text if hasattr(block, "text") else ""


async def enhance_race_description(race: "Race") -> str:
    """Suggest an improved description for a race (does not save)."""
    system_prompt = (
        "You are a copywriter for Vietnamese running event listings. "
        "Given a race's current details, write an engaging 2-3 paragraph description "
        "that highlights the unique experience, terrain, and challenge. "
        "Output only the description text."
    )

    response = await _anthropic().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=400,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": _race_summary_block(race),
            }
        ],
    )
    block = response.content[0]
    return block.text if hasattr(block, "text") else ""


async def suggest_race_tags(race: "Race") -> list[str]:
    """Return a list of suggested tag slugs for a race (does not save)."""
    system_prompt = (
        "You are a race categorization assistant. Given race details, "
        "suggest 3-7 short lowercase tag slugs (hyphenated, no spaces) "
        "that best describe this race. Examples: trail-running, mountainous, "
        "beginner-friendly, ultra-distance, night-race, scenic. "
        "Return only a JSON array of strings, nothing else."
    )

    response = await _anthropic().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": _race_summary_block(race),
            }
        ],
    )
    import json

    block = response.content[0]
    text = block.text if hasattr(block, "text") else "[]"
    try:
        tags = json.loads(text)
        return [str(t) for t in tags if isinstance(t, str)]
    except json.JSONDecodeError:
        logger.warning("suggest_race_tags: failed to parse JSON response: %s", text)
        return []


async def answer_race_question(race: "Race", question: str) -> str:
    """Answer a runner's question about a specific race."""
    race_block = _race_summary_block(race)

    system_prompt = (
        "You are a helpful assistant for Vietnamese running events. "
        "Answer the runner's question about the race using only the provided race details. "
        "If the answer is not in the race details, say so honestly. "
        "Be concise and friendly."
    )

    response = await _anthropic().messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=300,
        system=[
            {
                "type": "text",
                "text": system_prompt,
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[
            {
                "role": "user",
                "content": (
                    f"Race details:\n{race_block}\n\n"
                    f"Question: {question}"
                ),
            }
        ],
    )
    block = response.content[0]
    return block.text if hasattr(block, "text") else ""
