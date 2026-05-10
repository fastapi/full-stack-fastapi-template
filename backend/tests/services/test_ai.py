"""Tests for AI service functions using pytest-mock to avoid real API calls."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.services.ai import (
    answer_race_question,
    embed_race,
    embed_text,
    enhance_race_description,
    generate_race_recommendation_explanation,
    suggest_race_tags,
)


def _mock_race(
    name: str = "Test Race",
    description: str = "A challenging trail race",
    location: str = "Hanoi, Vietnam",
    terrain_type: str | None = "trail",
    difficulty_level: str | None = "hard",
    elevation_gain_m: int | None = 1200,
) -> MagicMock:
    race = MagicMock()
    race.id = uuid.uuid4()
    race.name = name
    race.description = description
    race.location = location

    if terrain_type:
        terrain = MagicMock()
        terrain.value = terrain_type
        race.terrain_type = terrain
    else:
        race.terrain_type = None

    if difficulty_level:
        difficulty = MagicMock()
        difficulty.value = difficulty_level
        race.difficulty_level = difficulty
    else:
        race.difficulty_level = None

    race.elevation_gain_m = elevation_gain_m
    return race


def _mock_profile(
    fitness_level: str = "advanced",
    distance_preference: str = "ultra",
    terrain_preference: str = "trail",
) -> MagicMock:
    profile = MagicMock()
    fl = MagicMock()
    fl.value = fitness_level
    profile.fitness_level = fl
    dp = MagicMock()
    dp.value = distance_preference
    profile.distance_preference = dp
    tp = MagicMock()
    tp.value = terrain_preference
    profile.terrain_preference = tp
    return profile


@pytest.mark.asyncio
async def test_embed_text_returns_vector() -> None:
    fake_embedding = [0.1] * 1536
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=fake_embedding)]

    with patch("app.services.ai._openai") as mock_openai_fn:
        mock_client = AsyncMock()
        mock_openai_fn.return_value = mock_client
        mock_client.embeddings.create = AsyncMock(return_value=mock_response)

        result = await embed_text("hello world")

    assert result == fake_embedding
    mock_client.embeddings.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_embed_race_builds_text_and_embeds() -> None:
    race = _mock_race()
    fake_embedding = [0.2] * 1536

    with patch("app.services.ai.embed_text", new_callable=AsyncMock) as mock_embed:
        mock_embed.return_value = fake_embedding
        result = await embed_race(race)

    assert result == fake_embedding
    call_text: str = mock_embed.call_args[0][0]
    assert "Test Race" in call_text
    assert "trail" in call_text


@pytest.mark.asyncio
async def test_generate_recommendation_explanation() -> None:
    race = _mock_race()
    profile = _mock_profile()
    fake_text = "This race is perfect for your trail running goals!"

    mock_block = MagicMock()
    mock_block.text = fake_text
    mock_response = MagicMock()
    mock_response.content = [mock_block]

    with patch("app.services.ai._anthropic") as mock_anthropic_fn:
        mock_client = AsyncMock()
        mock_anthropic_fn.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await generate_race_recommendation_explanation(race, profile)

    assert result == fake_text
    mock_client.messages.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_recommendation_explanation_no_profile() -> None:
    race = _mock_race()
    fake_text = "A great race for any runner."

    mock_block = MagicMock()
    mock_block.text = fake_text
    mock_response = MagicMock()
    mock_response.content = [mock_block]

    with patch("app.services.ai._anthropic") as mock_anthropic_fn:
        mock_client = AsyncMock()
        mock_anthropic_fn.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await generate_race_recommendation_explanation(race, None)

    assert result == fake_text


@pytest.mark.asyncio
async def test_enhance_race_description() -> None:
    race = _mock_race()
    enhanced = "Experience the breathtaking trails of northern Vietnam..."

    mock_block = MagicMock()
    mock_block.text = enhanced
    mock_response = MagicMock()
    mock_response.content = [mock_block]

    with patch("app.services.ai._anthropic") as mock_anthropic_fn:
        mock_client = AsyncMock()
        mock_anthropic_fn.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await enhance_race_description(race)

    assert result == enhanced


@pytest.mark.asyncio
async def test_suggest_race_tags_returns_list() -> None:
    race = _mock_race()

    mock_block = MagicMock()
    mock_block.text = '["trail-running", "mountainous", "ultra-distance"]'
    mock_response = MagicMock()
    mock_response.content = [mock_block]

    with patch("app.services.ai._anthropic") as mock_anthropic_fn:
        mock_client = AsyncMock()
        mock_anthropic_fn.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await suggest_race_tags(race)

    assert result == ["trail-running", "mountainous", "ultra-distance"]


@pytest.mark.asyncio
async def test_suggest_race_tags_invalid_json_returns_empty() -> None:
    race = _mock_race()

    mock_block = MagicMock()
    mock_block.text = "not valid json"
    mock_response = MagicMock()
    mock_response.content = [mock_block]

    with patch("app.services.ai._anthropic") as mock_anthropic_fn:
        mock_client = AsyncMock()
        mock_anthropic_fn.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await suggest_race_tags(race)

    assert result == []


@pytest.mark.asyncio
async def test_answer_race_question() -> None:
    race = _mock_race()
    question = "Is this race beginner-friendly?"
    expected_answer = "This race is rated hard and is better suited for advanced runners."

    mock_block = MagicMock()
    mock_block.text = expected_answer
    mock_response = MagicMock()
    mock_response.content = [mock_block]

    with patch("app.services.ai._anthropic") as mock_anthropic_fn:
        mock_client = AsyncMock()
        mock_anthropic_fn.return_value = mock_client
        mock_client.messages.create = AsyncMock(return_value=mock_response)

        result = await answer_race_question(race=race, question=question)

    assert result == expected_answer
    call_kwargs = mock_client.messages.create.call_args[1]
    user_content = call_kwargs["messages"][0]["content"]
    assert question in user_content
