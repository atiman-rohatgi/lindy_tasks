from datetime import datetime, timedelta, timezone

from fastapi import Response
from jose import JWTError, jwt
from passlib.context import CryptContext

from app import config

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Checked against when the email doesn't exist, so a failed login takes the
# same time whether or not the account exists.
_DUMMY_HASH = pwd_context.hash("not-a-real-password")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str | None) -> bool:
    if hashed_password is None:
        pwd_context.verify(plain_password, _DUMMY_HASH)
        return False
    return pwd_context.verify(plain_password, hashed_password)


def create_session_token(user_id: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(days=config.SESSION_TTL_DAYS)
    return jwt.encode({"sub": user_id, "exp": expires}, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)


def read_session_token(token: str) -> str | None:
    """Return the user id in a valid token, or None if it's invalid or expired."""
    try:
        payload = jwt.decode(token, config.JWT_SECRET, algorithms=[config.JWT_ALGORITHM])
    except JWTError:
        return None
    return payload.get("sub")


def set_session_cookie(response: Response, user_id: str) -> None:
    response.set_cookie(
        key=config.SESSION_COOKIE_NAME,
        value=create_session_token(user_id),
        max_age=config.SESSION_TTL_DAYS * 24 * 60 * 60,
        httponly=True,
        samesite="lax",  # localhost:3000 and localhost:8080 count as the same site
        secure=False,  # set True when served over HTTPS
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    # Must use the same attributes as set_session_cookie, or the browser keeps the cookie.
    response.delete_cookie(
        key=config.SESSION_COOKIE_NAME,
        httponly=True,
        samesite="lax",
        secure=False,
        path="/",
    )
