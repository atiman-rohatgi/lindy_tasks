import os

from dotenv import load_dotenv

load_dotenv()


def _require(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required environment variable {name} (see .env.example)")
    return value


DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "lindy_tasks")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

# Secret used to sign session tokens. Generate one with:
#   python -c "import secrets; print(secrets.token_urlsafe(32))"
JWT_SECRET = _require("JWT_SECRET")
JWT_ALGORITHM = "HS256"
SESSION_COOKIE_NAME = "session"
SESSION_TTL_DAYS = 7

FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")
