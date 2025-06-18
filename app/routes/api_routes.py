from fastapi import APIRouter

from app.routes.admin_routes import router as admin_router
from app.routes.auth_routes import router as auth_router
from app.routes.mail_routes import router as mail_router
from app.routes.clients_routes import router as clients_router
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
    clients_router,
    prefix="/clients",
    tags=["Clients"],
    include_in_schema=True,
)

router.include_router(
    admin_router,
    prefix="/admin",
    tags=["Admin"],
    include_in_schema=True,
)
