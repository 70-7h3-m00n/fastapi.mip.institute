from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models import init_db
from app.routes import router as payment_router
from fastapi.middleware.cors import CORSMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    print("Database initialized.")
    yield
    print("Application shutting down.")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://front.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payment_router)


# uvicorn main:app --reload --port 8001
# ngrok http http://localhost:8001
