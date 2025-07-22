from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query
from http import HTTPStatus
from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps import get_current_admin_user
from app.database.db_init import get_db
from app.models.schemas import PromoResponse, PromoBase, PaginationResponse
from app.models.db_models import Promo, User

router = APIRouter()


@router.post(
    "/promo/create",
    summary="Create promo",
    description="Create promo. Uses Bearer token for authentication.",
    status_code=HTTPStatus.OK,
)
async def create_promo(
    promo_data: PromoBase,
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> PromoResponse:
    promo = Promo(
        name=promo_data.name,
        promo_code=promo_data.promo_code,
        redirect_url=promo_data.redirect_url,
        is_active=promo_data.is_active,
        show_sticky_bottom=promo_data.show_sticky_bottom,
    )
    session.add(promo)
    await session.commit()
    return promo


@router.put(
    "/promo/update/{promo_id}",
    summary="Update promo",
    description="Update promo. Uses Bearer token for authentication.",
    status_code=HTTPStatus.OK,
)
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
    promo.show_sticky_bottom = promo_data.show_sticky_bottom
    promo.is_active = promo_data.is_active
    promo.updated_at = datetime.now(timezone.utc)
    await session.commit()
    return promo


@router.delete(
    "/promo/delete/{promo_id}",
    summary="Delete promo",
    description="Delete promo. Uses Bearer token for authentication.",
    status_code=HTTPStatus.OK,
)
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


@router.put(
    "/promo/activate/{promo_id}",
    summary="Activate/deactivate promo",
    description="Activate/deactivate promo. Uses Bearer token for authentication.",
    status_code=HTTPStatus.OK,
)
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


@router.get(
    "/promo/promos",
    summary="Get promos",
    description="Get promos list for admin. Uses Bearer token for authentication.",
    status_code=HTTPStatus.OK,
)
async def get_promos(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1),
    search: str = Query(None),
    current_user: User = Depends(get_current_admin_user),
    session: AsyncSession = Depends(get_db),
) -> PaginationResponse[PromoResponse]:
    query = select(Promo).order_by(Promo.created_at.desc())
    if search:
        query = query.where(
            or_(
                Promo.name.ilike(f"%{search}%"),
                Promo.promo_code.ilike(f"%{search}%")
            )
        )
    promos_select = await session.execute(
        query.offset((page - 1) * per_page).limit(per_page)
    )
    promos = promos_select.scalars().all()
    count_select = await session.execute(select(func.count(Promo.id)))
    count = count_select.scalar_one()
    return PaginationResponse(
        items=[PromoResponse.model_validate(promo) for promo in promos],
        count=count,
        page=page,
        per_page=per_page
    )
