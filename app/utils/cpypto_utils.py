from cryptography.fernet import Fernet ,InvalidToken

def encrypt_data(data, key):
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str, key: str) -> str:
    try:
        f = Fernet(key)
        return f.decrypt(encrypted_data.encode()).decode()
    except (InvalidToken, Exception):
        return "[decryption error]"
    