# example_config.py

class Config(object):
    # Database connection URI (using SQLite in this example)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///passwordmanager.db'

    # Whether to track modifications of objects (set to False to reduce overhead)
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Secret key used by Flask for session signing, CSRF protection, etc.
    SECRET_KEY = 'your-secret-key-here'  # ← Replace with a strong, unique value

    # Caching configuration
    CACHE_TYPE = 'SimpleCache'  # Other options: RedisCache, MemcachedCache, etc.
    CACHE_DEFAULT_TIMEOUT = 300  # Cache timeout in seconds (5 minutes)

    # Mail server configuration (using Gmail's SMTP server here)
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    # Email login credentials (do not include real credentials here!)
    MAIL_USERNAME = "your-email@gmail.com"         # ← Replace with your email address
    MAIL_PASSWORD = "your-app-password-or-token"   # ← Use an app-specific password or token

    # Default sender for outgoing emails
    MAIL_DEFAULT_SENDER = ("Password Manager", "your-email@gmail.com")
    
    
    LOGIN_VIEW = "auth.login"
    LOGIN_MESSAGE = "You don't have permission"