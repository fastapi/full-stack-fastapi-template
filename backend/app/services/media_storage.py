import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


def _safe_extension(filename: str) -> str:
    ext = Path(filename).suffix.lower().strip()
    if not ext:
        return ".bin"
    if len(ext) > 10:
        return ".bin"
    return ext


def get_media_storage_root() -> Path:
    root = Path(settings.MEDIA_UPLOAD_DIR)
    if not root.is_absolute():
        root = Path(__file__).resolve().parents[2] / root
    root.mkdir(parents=True, exist_ok=True)
    return root


def save_uploaded_media(
    *,
    file: UploadFile,
    content_type: str,
    content_id: uuid.UUID,
) -> tuple[str, str, int]:
    """Save file and return (stored_filename, relative_path, size_bytes)."""
    storage_root = get_media_storage_root()
    target_dir = storage_root / content_type / str(content_id)
    target_dir.mkdir(parents=True, exist_ok=True)

    ext = _safe_extension(file.filename or "")
    stored_filename = f"{uuid.uuid4().hex}{ext}"
    target_path = target_dir / stored_filename

    content = file.file.read()
    size_bytes = len(content)
    target_path.write_bytes(content)

    relative_path = str(target_path.relative_to(storage_root))
    return stored_filename, relative_path, size_bytes


def resolve_media_path(file_path: str) -> Path:
    storage_root = get_media_storage_root()
    return storage_root / file_path


def delete_media_file(file_path: str) -> None:
    target = resolve_media_path(file_path)
    if target.exists() and target.is_file():
        target.unlink()
