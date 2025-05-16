from fastapi import APIRouter, Depends
from fastapi.security import HTTPBasicCredentials
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_init import get_db
from app.models.schemas import PromoResponse
from app.models.db_models import Promo
from app.services.auth_services import verify_credentials

router = APIRouter()


@router.get(
    "/promos",
    summary="Get public promos",
    description="Get public promos. Uses Basic authentication.",
    status_code=HTTPStatus.OK,
)
async def get_public_promos(
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
    session: AsyncSession = Depends(get_db),
) -> list[PromoResponse]:
    promos = await session.execute(select(Promo).where(Promo.is_active.is_(True)))
    return promos.scalars().all()
