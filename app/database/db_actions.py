from typing import Any
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.database.db_init import Base
from app.logging_init import get_logger
from app.models.db_models import Transaction, User
from app.models.enums import UserRoleEnum
from app.services.auth_services import get_password_hash

logger = get_logger()


async def get_one_or_create(
    db: AsyncSession,
    model: Base,
    create_method: str = "",
    create_method_kwargs: Any = None,
    **kwargs,
) -> tuple[Base, bool]:
    result = await db.execute(select(model).filter_by(**kwargs))
    obj = result.scalars().first()
    if obj:
        return obj, False
    kwargs.update(create_method_kwargs or {})
    created = getattr(model, create_method, model)(**kwargs)
    try:
        db.add(created)
        await db.flush()
        await db.refresh(created)
        return created, True
    except IntegrityError:
        await db.rollback()
        result = await db.execute(select(model).filter_by(**kwargs))
        return result.scalars().first(), False


async def set_transaction_status(
    db: AsyncSession, transaction_id: str, status: str
) -> None:
    transaction_select = await db.execute(
        select(Transaction).filter_by(transaction_id=transaction_id)
    )
    transaction = transaction_select.scalar()
    if transaction:
        transaction.status = status
        await db.commit()
    else:
        logger.error(f"Transaction {transaction_id} was not found")


async def mark_email_sent(db: AsyncSession, transaction_id: str) -> None:
    transaction_select = await db.execute(
        select(Transaction).filter_by(transaction_id=transaction_id)
    )
    transaction = transaction_select.scalar()
    if transaction:
        transaction.email_sent = True
        await db.commit()
    else:
        logger.error(f"Transaction {transaction_id} was not found")


async def init_admin(db: AsyncSession) -> None:
    """
    Initialize admin user if it doesn't exist.
    """
    try:
        admin_email = config.auth.admin_email
        admin_password = config.auth.admin_password
        result = await db.execute(
            select(User).where(User.email == admin_email)
        )
        admin = result.scalars().first()

        if not admin:
            hashed_password = get_password_hash(admin_password)
            admin = User(
                email=admin_email,
                password=hashed_password,
                role=UserRoleEnum.ADMIN,
                created_at=datetime.now(timezone.utc),
                first_name="MIP",
                last_name="Admin",
            )
            db.add(admin)
            await db.commit()
            logger.info("Admin user created successfully")
        else:
            logger.info("Admin user already exists")

    except Exception as e:
        logger.error(f"Error initializing admin user: {str(e)}")
        await db.rollback()
        raise
