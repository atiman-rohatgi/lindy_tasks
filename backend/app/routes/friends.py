from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from app.database import db_cursor
from app.deps import CurrentUser, get_current_user

router = APIRouter()

DEGREE_LABELS = {1: "1st", 2: "2nd", 3: "3rd"}

# Walk out one degree at a time. DISTINCT keeps each step to at most one row
# per user, even in a tightly connected network. 2nd degree always contains
# the user themself and 3rd degree contains their direct friends again, so
# MIN(degree) keeps each person at their closest degree and the WHERE clause
# drops the user.
NETWORK_QUERY = """
WITH d1 AS (
    SELECT friend_id AS id FROM friendships WHERE user_id = %(me)s
),
d2 AS (
    SELECT DISTINCT f.friend_id AS id FROM friendships f JOIN d1 ON f.user_id = d1.id
),
d3 AS (
    SELECT DISTINCT f.friend_id AS id FROM friendships f JOIN d2 ON f.user_id = d2.id
),
all_degrees AS (
    SELECT id, 1 AS degree FROM d1
    UNION ALL SELECT id, 2 FROM d2
    UNION ALL SELECT id, 3 FROM d3
)
SELECT u.name, u.email, MIN(a.degree) AS degree
FROM all_degrees a
JOIN users u ON u.id = a.id
WHERE a.id <> %(me)s
GROUP BY u.id, u.name, u.email
ORDER BY degree, u.name
"""


class AddFriendRequest(BaseModel):
    friendEmail: EmailStr


# "" rather than "/": with "/" the URL would be /v1/friends/ and a request to
# /v1/friends would be redirected first.
@router.get("")
def list_friends(user: CurrentUser = Depends(get_current_user)):
    with db_cursor() as cursor:
        cursor.execute(NETWORK_QUERY, {"me": user.id})
        rows = cursor.fetchall()

    return [{"name": name, "email": email, "degree": DEGREE_LABELS[degree]} for name, email, degree in rows]


@router.post("/add")
def add_friend(body: AddFriendRequest, user: CurrentUser = Depends(get_current_user)):
    with db_cursor() as cursor:
        cursor.execute("SELECT id FROM users WHERE email = %s", (body.friendEmail.lower(),))
        row = cursor.fetchone()

        if row is None:
            raise HTTPException(status_code=404, detail="No user with that email")

        friend_id = str(row[0])
        # Compare ids, not emails, so a differently-cased email is still caught.
        if friend_id == user.id:
            raise HTTPException(status_code=400, detail="You can't add yourself")

        # Both directions in one statement. ON CONFLICT makes re-adding an
        # existing friend (from either side) a no-op that still succeeds.
        cursor.execute(
            """
            INSERT INTO friendships (user_id, friend_id)
            VALUES (%s, %s), (%s, %s)
            ON CONFLICT DO NOTHING
            """,
            (user.id, friend_id, friend_id, user.id),
        )

    return {"message": "Friend added"}
