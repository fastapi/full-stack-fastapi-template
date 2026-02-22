import logging
import logging.config

from app.core.config import settings


def setup_logging() -> None:
    level = settings.LOG_LEVEL.upper()

    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": ("%(asctime)s | %(levelname)s | %(name)s | %(message)s")
                }
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                    "level": level,
                }
            },
            "root": {"handlers": ["default"], "level": level},
            "loggers": {
                "uvicorn.error": {"level": level},
                "uvicorn.access": {"level": "INFO"},
                "httpx": {"level": "WARNING"},
            },
        }
    )
