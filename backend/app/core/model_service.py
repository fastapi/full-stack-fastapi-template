"""Shared HTTP plumbing for the model services.

Each model runs in its own container (see services/). This module is the one
place that knows how to talk to them — timeouts, chunking, and the
still-loading contract — so the per-model clients stay a few lines each.

The 503 handling matters: a model service that is cold or restarting is a
retryable condition, not a failure. Routes translate this into 503 +
Retry-After so a batch worker backs off instead of giving up.
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


class ModelServiceUnavailable(RuntimeError):
    """A model service is unreachable, still loading, or timed out."""

    def __init__(self, service: str, detail: str) -> None:
        self.service = service
        super().__init__(f"{service} unavailable: {detail}")


@dataclass(frozen=True)
class ModelService:
    """Connection details for one model container."""

    name: str
    base_url: str
    connect_timeout: float
    read_timeout: float
    # Kept under the service's own per-request cap so large jobs are chunked
    # here rather than rejected there.
    chunk_size: int

    def _timeout(self) -> httpx.Timeout:
        # Connect fast so a dead service fails quickly; read slow because a
        # large batch legitimately takes minutes.
        return httpx.Timeout(self.read_timeout, connect=self.connect_timeout)

    def client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(base_url=self.base_url, timeout=self._timeout())

    async def post(
        self, client: httpx.AsyncClient, path: str, payload: dict
    ) -> dict:
        try:
            response = await client.post(path, json=payload)
        except httpx.HTTPError as exc:
            raise ModelServiceUnavailable(self.name, f"unreachable: {exc}") from exc

        if response.status_code == 503:
            raise ModelServiceUnavailable(self.name, f"not ready: {response.text}")

        response.raise_for_status()
        return response.json()

    async def post_chunked_scores(
        self, path: str, key: str, items: list
    ) -> tuple[list[float], float]:
        """POST `items` under `key` in chunks, concatenating the scores."""
        if not items:
            return [], 0.0

        scores: list[float] = []
        async with self.client() as client:
            for start in range(0, len(items), self.chunk_size):
                payload = await self.post(
                    client, path, {key: items[start : start + self.chunk_size]}
                )
                scores.extend(payload["scores"])

        # Recomputed over all scores — a mean of per-chunk means would be wrong
        # whenever the last chunk is short.
        return scores, sum(scores) / len(scores)
