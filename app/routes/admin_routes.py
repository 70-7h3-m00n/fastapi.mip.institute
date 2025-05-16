from fastapi import APIRouter, Depends, HTTPException
from http import HTTPStatus
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_admin_user
from app.database.db_init import get_db
from app.models.schemas import PromoResponse, PromoBase
from app.models.db_models import Promo, User

router = APIRouter()


@router.post("/promo/create", status_code=HTTPStatus.OK)
async def create_promo(
    promo_data: PromoBase,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> PromoResponse:
    promo = Promo(
        name=promo_data.name,
        promo_code=promo_data.promo_code,
        redirect_url=promo_data.redirect_url,
        is_active=True,
    )
    session.add(promo)
    await session.commit()
    return promo


@router.put("/promo/update/{promo_id}", status_code=HTTPStatus.OK)
async def update_promo(
    promo_id: int,
    promo_data: PromoBase,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> PromoResponse:
    promo = await session.execute(select(Promo).where(Promo.id == promo_id))
    promo = promo.scalar_one_or_none()
    if promo is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Promo not found")
    promo.name = promo_data.name
    promo.promo_code = promo_data.promo_code
    promo.redirect_url = promo_data.redirect_url
    await session.commit()
    return promo


@router.delete("/promo/delete/{promo_id}", status_code=HTTPStatus.OK)
async def delete_promo(
    promo_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    promo = await session.execute(select(Promo).where(Promo.id == promo_id))
    promo = promo.scalar_one_or_none()
    if promo is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Promo not found")
    await session.delete(promo)
    await session.commit()
    return None


@router.put("/promo/activate/{promo_id}", status_code=HTTPStatus.OK)
async def activate_promo(
    promo_id: int,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> None:
    promo = await session.execute(select(Promo).where(Promo.id == promo_id))
    promo = promo.scalar_one_or_none()
    if promo is None:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Promo not found")
    promo.is_active = not promo.is_active
    await session.commit()

    return None


@router.get("/promo/promos", status_code=HTTPStatus.OK)
async def get_promos(
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> list[PromoResponse]:
    promos = await session.execute(select(Promo))
    return promos.scalars().all()
