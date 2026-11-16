import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import config
from app.errors import register_error_handlers
from app.routes.auth import router as auth_router
from app.routes.friends import router as friends_router
from app.routes.profile import router as profile_router

app = FastAPI()

register_error_handlers(app)

app.include_router(auth_router, prefix="/v1/auth")
app.include_router(profile_router, prefix="/v1")
app.include_router(friends_router, prefix="/v1/friends")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[config.FRONTEND_ORIGIN],
    allow_credentials=True,  # needed for the session cookie
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Run from the backend/ folder: python -m app.main
    uvicorn.run("app.main:app", host="localhost", port=8080, reload=True)
