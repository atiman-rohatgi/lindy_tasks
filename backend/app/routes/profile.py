from fastapi import APIRouter, Depends

from app.deps import CurrentUser, get_current_user

router = APIRouter()


@router.get("/profile")
def get_profile(user: CurrentUser = Depends(get_current_user)):
    return {"id": user.id, "name": user.name, "email": user.email}
