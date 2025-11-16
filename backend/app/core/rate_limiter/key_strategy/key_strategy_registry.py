from app.core.rate_limiter.key_strategy.header_key_strategy import HeaderKeyStrategy
from app.core.rate_limiter.key_strategy.ip_key_strategy import IPKeyStrategy
from app.core.rate_limiter.key_strategy.key_strategy import KeyStrategy
from app.core.rate_limiter.key_strategy.key_strategy_enum import KeyStrategyName


def get_key_strategy(
    name: KeyStrategyName, header_name: str | None = None
) -> KeyStrategy:
    if name == KeyStrategyName.IP:
        return IPKeyStrategy()

    if name == KeyStrategyName.HEADER:
        return HeaderKeyStrategy(header_name=header_name or "X-Client-ID")

    raise ValueError(f"Unsupported key strategy: {name}")
