from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel, EmailStr, Field, field_validator

from app.database import db_cursor
from app.security import clear_session_cookie, hash_password, set_session_cookie, verify_password

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=8)

    @field_validator("name")
    @classmethod
    def strip_name(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Name can't be blank")
        return value

    @field_validator("password")
    @classmethod
    def password_fits_bcrypt(cls, value: str) -> str:
        # bcrypt silently ignores everything past 72 bytes, and accented or
        # non-Latin characters take more than one byte each.
        if len(value.encode("utf-8")) > 72:
            raise ValueError("Password is too long")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
def register(body: RegisterRequest, response: Response):
    email = body.email.lower()

    with db_cursor() as cursor:
        # ON CONFLICT also covers two sign-ups with the same email at the same moment.
        cursor.execute(
            """
            INSERT INTO users (name, email, hashed_password)
            VALUES (%s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            RETURNING id
            """,
            (body.name, email, hash_password(body.password)),
        )
        row = cursor.fetchone()

    if row is None:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Registering also signs the user in; the frontend goes straight to /app.
    set_session_cookie(response, str(row[0]))
    return {"message": "User created"}


@router.post("/login")
def login(body: LoginRequest, response: Response):
    with db_cursor() as cursor:
        cursor.execute(
            "SELECT id, hashed_password FROM users WHERE email = %s",
            (body.email.lower(),),
        )
        row = cursor.fetchone()

    if not verify_password(body.password, row[1] if row else None):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    set_session_cookie(response, str(row[0]))
    return {"message": "Signed in"}


# No sign-in required: signing out when already signed out still succeeds.
@router.post("/logout")
def logout(response: Response):
    clear_session_cookie(response)
    return {"message": "Signed out"}
