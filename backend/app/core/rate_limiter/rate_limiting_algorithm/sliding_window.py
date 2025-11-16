import time
import logging
from pathlib import Path
from typing import Optional, Tuple

import redis.asyncio as redis

from app.core.rate_limiter.rate_limiting_algorithm.base import BaseRateLimiter

logger = logging.getLogger(__name__)

SCRIPT_PATH = Path(__file__).parent /".."/".."/".."/"alembic"/ "rate_limiting_algorithms" / "sliding_window.lua"


class SlidingWindowRateLimiter(BaseRateLimiter):
    def __init__(self, redis_client: redis.Redis, fail_open: bool):
        self.redis = redis_client
        self.lua_script = None
        self.fail_open = fail_open

    async def load_script(self):
        if self.lua_script is None:
            script_text = SCRIPT_PATH.read_text()
            # LOAD script into redis → returns SHA
            self.lua_script = await self.redis.script_load(script_text)
        return self.lua_script

    async def allow_request(
        self,
        key: str,
        limit: int,
        window_seconds: int,
        member_id: Optional[str] = None
    ) -> Tuple[bool, Optional[int]]:

        now_ms = int(time.time() * 1000)
        window_ms = window_seconds * 1000
        member = member_id or f"{now_ms}"

        try:
            sha = await self.load_script()
            res = await self.redis.evalsha(
                sha,
                1,
                key,
                now_ms,
                window_ms,
                limit,
                member
            )
        except Exception:
            logger.exception("Redis error; failing open")
            return True, None

        cnt, oldest_ts = int(res[0]), int(res[1] or 0)

        if cnt <= limit:
            return True, None

        retry_after_ms = (oldest_ts + window_ms) - now_ms
        retry_after_s = max(0, retry_after_ms // 1000)

        return False, retry_after_s

    def get_fail_open(self):
        return self.fail_open
