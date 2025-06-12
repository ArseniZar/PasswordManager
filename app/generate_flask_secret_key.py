import secrets

def generate_flask_secret_key(length=50):
    """Generate a secure random secret key for Flask apps."""
    return secrets.token_urlsafe(length)


if __name__ == "__main__":
    key = generate_flask_secret_key()
    print("Your new secret key is:", key)