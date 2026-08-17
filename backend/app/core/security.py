import base64
import hashlib
import logging
from typing import Optional
from cryptography.fernet import Fernet
from app.core.config import settings

logger = logging.getLogger("traceback.core.security")


def _get_fernet() -> Fernet:
    """Generates a deterministic 32-byte Fernet key based on server TRACEBACK_ENCRYPTION_KEY / SECRET_KEY."""
    raw_secret = getattr(settings, "TRACEBACK_ENCRYPTION_KEY", "") or getattr(settings, "SECRET_KEY", "traceback-default-key")
    key_bytes = hashlib.sha256(raw_secret.encode("utf-8")).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def encrypt_api_key(raw_key: str) -> str:
    """Encrypts a sensitive API key using Fernet symmetric encryption."""
    if not raw_key or not raw_key.strip():
        return ""
    try:
        fernet = _get_fernet()
        return fernet.encrypt(raw_key.strip().encode("utf-8")).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to encrypt API key: {e}")
        raise ValueError("Encryption error occurred while securing API key.") from e


def decrypt_api_key(encrypted_key: Optional[str]) -> Optional[str]:
    """Decrypts an encrypted API key back to plaintext string in memory."""
    if not encrypted_key or not encrypted_key.strip():
        return None
    try:
        fernet = _get_fernet()
        return fernet.decrypt(encrypted_key.strip().encode("utf-8")).decode("utf-8")
    except Exception as e:
        logger.error(f"Failed to decrypt API key: {e}")
        return None


def mask_api_key(encrypted_key: Optional[str]) -> Optional[str]:
    """Returns a masked representation of the API key for safe frontend UI response."""
    if not encrypted_key or not encrypted_key.strip():
        return None
    return "••••••••••••••••"
