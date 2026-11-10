import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import router as auth_router

load_dotenv()

app = FastAPI()

app.include_router(auth_router, prefix="/v1/auth")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    # Run from the backend/ folder: python -m app.main
    uvicorn.run("app.main:app", host="localhost", port=8080, reload=True)
