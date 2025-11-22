import shutil
import os
from pathlib import Path
from fastapi import UploadFile
from app.core.config import settings

class FileStorageService:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def save_file(self, file: UploadFile, filename: str) -> str:
        """
        Save an upload file to storage.
        Returns the relative path to the file.
        """
        file_path = self.storage_dir / filename
        
        # Ensure unique filename if needed, but for now we assume filename is unique (e.g. uuid)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return str(file_path)

    def get_file_path(self, relative_path: str) -> Path:
        """
        Get absolute path for a file.
        """
        return Path(relative_path).resolve()

    def delete_file(self, relative_path: str) -> bool:
        """
        Delete a file from storage.
        """
        path = Path(relative_path)
        if path.exists():
            path.unlink()
            return True
        return False

# Singleton instance
storage_service = FileStorageService()
