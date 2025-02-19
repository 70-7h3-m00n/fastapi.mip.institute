from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.config import config
from app.routes.api_routes import router as api_router

app = FastAPI(
    title=config.application.title,
    version=config.application.version,
    description=config.application.description,
    docs_url=config.application.docs_url,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.application.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=config.application.api_prefix)
