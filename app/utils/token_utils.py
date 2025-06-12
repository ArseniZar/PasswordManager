
import base64
import hashlib


def generate_reset_token_from_forgot_password(user_id: int) -> str:
    from ..exstesions import serializer
    return serializer.dumps({"user_id": user_id})


def verify_reset_token_from_forgot_password(token: str, expires_sec: int = 3600) -> int:
    from ..exstesions import serializer
    user_id = serializer.loads(token, max_age=expires_sec)["user_id"]
    return user_id


def create_token_from_password(password: str, salt: bytes, iterations: int = 100_000, dklen: int = 32) -> str:
    token_bytes = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt,
        iterations,
        dklen
    )
    return base64.urlsafe_b64encode(token_bytes).decode('utf-8')