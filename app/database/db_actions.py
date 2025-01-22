from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.db_init import Base
from app.logging_init import get_logger
from app.models.db_models import Transaction

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
    else:
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


# async def add_transaction(
#   db: AsyncSession, transaction_id: str, status: str, amount: float
# ) -> None:
#     try:
#         transaction = Transaction(
#             transaction_id=transaction_id,
#             status=status,
#             amount=amount,
#         )
#         db.add(transaction)
#         await db.commit()
#     except IntegrityError as e:
#         logger.error(f"Transaction {transaction_id} already exists: {e}")
#         await db.rollback()


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
