from fastapi import APIRouter

from app.routes.auth_routes import router as auth_router
from app.routes.mail_routes import router as mail_router
from app.routes.promo_routes import router as promo_router
from app.routes.transaction_routes import router as transaction_router

router = APIRouter()

router.include_router(
    auth_router,
    prefix="/auth",
    tags=["Auth"],
    include_in_schema=True,
)

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

router.include_router(
    promo_router,
    prefix="/promo",
    tags=["Promo"],
    include_in_schema=True,
)
