from fastapi import APIRouter

from app.routes.transaction_routes import router as transaction_router

router = APIRouter()


router.include_router(
    transaction_router,
    prefix="/transactions",
    tags=["Transactions"],
    include_in_schema=True,
)
