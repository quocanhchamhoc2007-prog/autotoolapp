import base64
from cryptography.fernet import Fernet
from config.settings import settings

def _get_fernet() -> Fernet:
    key_bytes = settings.SECRET_KEY.encode()
    # Đảm bảo key đủ độ dài cho Fernet (32 url-safe base64-encoded bytes)
    padded = key_bytes.ljust(32, b'0')[:32]
    encoded_key = base64.urlsafe_b64encode(padded)
    return Fernet(encoded_key)

def encrypt_token(token: str) -> str:
    if not token:
        return ""
    f = _get_fernet()
    return f.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    if not encrypted_token:
        return ""
    try:
        f = _get_fernet()
        return f.decrypt(encrypted_token.encode()).decode()
    except Exception:
        return ""