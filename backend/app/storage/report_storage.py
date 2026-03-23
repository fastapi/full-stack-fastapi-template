import os
from abc import ABC, abstractmethod
from pathlib import Path


class ReportStorage(ABC):
    @abstractmethod
    def save(self, brand_id: str, week_start: str, pdf_bytes: bytes) -> str:
        """Save PDF and return the storage path/key."""

    @abstractmethod
    def get(self, path: str) -> bytes:
        """Load PDF bytes from the given path/key."""


class LocalReportStorage(ReportStorage):
    def __init__(self, base_path: str):
        self.base_path = Path(base_path)

    def save(self, brand_id: str, week_start: str, pdf_bytes: bytes) -> str:
        dest = self.base_path / brand_id / f"{week_start}.pdf"
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(pdf_bytes)
        return str(dest)

    def get(self, path: str) -> bytes:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Report not found: {path}")
        return p.read_bytes()


def get_report_storage(backend: str | None = None, path: str | None = None) -> ReportStorage:
    _backend = backend or os.getenv("REPORT_STORAGE_BACKEND", "local")
    _path = path or os.getenv("REPORT_STORAGE_PATH", "/app/storage/reports")
    if _backend == "local":
        return LocalReportStorage(base_path=_path)
    raise ValueError(f"Unknown REPORT_STORAGE_BACKEND: {_backend}")
