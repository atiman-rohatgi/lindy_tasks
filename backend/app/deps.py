from dataclasses import dataclass

from fastapi import Cookie, HTTPException

from app import config
from app.database import db_cursor
from app.security import read_session_token


@dataclass
class CurrentUser:
    id: str
    name: str
    email: str


def get_current_user(
    session: str | None = Cookie(default=None, alias=config.SESSION_COOKIE_NAME),
) -> CurrentUser:
    user_id = read_session_token(session) if session else None
    if not user_id:
        raise HTTPException(status_code=401, detail="Not signed in")

    with db_cursor() as cursor:
        cursor.execute("SELECT id, name, email FROM users WHERE id = %s", (user_id,))
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=401, detail="Not signed in")

    return CurrentUser(id=str(row[0]), name=row[1], email=row[2])
