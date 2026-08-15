import os
import uuid
from typing import Optional, Tuple
from fastapi import UploadFile


class StorageService:
    """Storage service for persisting evidence files and knowledge base documents locally or to MinIO/S3."""

    def __init__(self, base_upload_dir: str = "storage/uploads"):
        self.base_upload_dir = base_upload_dir
        os.makedirs(self.base_upload_dir, exist_ok=True)

    async def save_upload_file(self, upload_file: UploadFile) -> Tuple[str, int, str]:
        """Saves an UploadFile to disk and returns (file_url, file_size, mime_type)."""
        file_ext = os.path.splitext(upload_file.filename or "")[1]
        unique_name = f"{uuid.uuid4().hex}{file_ext}"
        destination_path = os.path.join(self.base_upload_dir, unique_name)

        content = await upload_file.read()
        file_size = len(content)

        with open(destination_path, "wb") as f:
            f.write(content)

        file_url = f"/static/uploads/{unique_name}"
        mime_type = upload_file.content_type or "application/octet-stream"

        return file_url, file_size, mime_type

    def save_raw_text_snippet(self, content: str, extension: str = ".txt") -> Tuple[str, int, str]:
        """Saves a raw text snippet to disk and returns (file_url, file_size, mime_type)."""
        unique_name = f"{uuid.uuid4().hex}{extension}"
        destination_path = os.path.join(self.base_upload_dir, unique_name)

        encoded_bytes = content.encode("utf-8")
        file_size = len(encoded_bytes)

        with open(destination_path, "wb") as f:
            f.write(encoded_bytes)

        file_url = f"/static/uploads/{unique_name}"
        mime_type = "text/plain"

        return file_url, file_size, mime_type


storage_service = StorageService()
