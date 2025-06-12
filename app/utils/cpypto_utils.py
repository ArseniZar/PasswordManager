from cryptography.fernet import Fernet ,InvalidToken

def encrypt_data(data: str, key: str) -> str:
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()


def decrypt_data(encrypted_data: str, key: str) -> str:
    f = Fernet(key)
    return f.decrypt(encrypted_data.encode()).decode()
    