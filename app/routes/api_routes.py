from fastapi import APIRouter

from app.routes.mail_routes import router as mail_router
from app.routes.transaction_routes import router as transaction_router

router = APIRouter()


router.include_router(
    transaction_router,
    prefix="/transactions",
    tags=["Transactions"],
    include_in_schema=True,
)

router.include_router(
    mail_router,
    prefix="/mails",
    tags=["Mail"],
    include_in_schema=True,
)
