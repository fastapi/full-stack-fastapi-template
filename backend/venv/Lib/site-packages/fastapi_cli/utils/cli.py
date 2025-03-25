import logging
from typing import Any, Dict

from rich_toolkit import RichToolkit, RichToolkitTheme
from rich_toolkit.styles import TaggedStyle
from uvicorn.logging import DefaultFormatter


class CustomFormatter(DefaultFormatter):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.toolkit = get_rich_toolkit()

    def formatMessage(self, record: logging.LogRecord) -> str:
        return self.toolkit.print_as_string(record.getMessage(), tag=record.levelname)


def get_uvicorn_log_config() -> Dict[str, Any]:
    return {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": CustomFormatter,
                "fmt": "%(levelprefix)s %(message)s",
                "use_colors": None,
            },
            "access": {
                "()": CustomFormatter,
                "fmt": "%(levelprefix)s %(client_addr)s - '%(request_line)s' %(status_code)s",
            },
        },
        "handlers": {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
            "access": {
                "formatter": "access",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "uvicorn": {"handlers": ["default"], "level": "INFO"},
            "uvicorn.error": {"level": "INFO"},
            "uvicorn.access": {
                "handlers": ["access"],
                "level": "INFO",
                "propagate": False,
            },
        },
    }


logger = logging.getLogger(__name__)


def get_rich_toolkit() -> RichToolkit:
    theme = RichToolkitTheme(
        style=TaggedStyle(tag_width=11),
        theme={
            "tag.title": "white on #009485",
            "tag": "white on #007166",
            "placeholder": "grey85",
            "text": "white",
            "selected": "#007166",
            "result": "grey85",
            "progress": "on #007166",
            "error": "red",
            "log.info": "black on blue",
        },
    )

    return RichToolkit(theme=theme)
