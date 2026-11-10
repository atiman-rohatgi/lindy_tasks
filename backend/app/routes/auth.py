from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

from app.database import get_connection
from app.security import hash_password

router = APIRouter()


class RegisterRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


@router.post("/register", status_code=201)
def register(body: RegisterRequest):
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM users WHERE email = %s", (body.email,))
        existing_user = cursor.fetchone()

        if existing_user:
            cursor.close()
            conn.close()
            raise HTTPException(status_code=400, detail="Email already registered")

        cursor.execute(
            "INSERT INTO users (name, email, hashed_password) VALUES (%s, %s, %s)",
            (body.name, body.email, hash_password(body.password)),
        )

        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "User created"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
