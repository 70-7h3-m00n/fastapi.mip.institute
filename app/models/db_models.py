from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.db_init import Base
from app.models.enums import TransactionStatusEnum


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    password: Mapped[str] = mapped_column(String, nullable=True)
    role: Mapped[str] = mapped_column(String, nullable=False, default="user")

    transactions: Mapped[list["Transaction"]] = relationship(back_populates="user")


class Promo(Base):
    __tablename__ = "promos"

    id: Mapped[int] = mapped_column(Integer, autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    promo_code: Mapped[str] = mapped_column(String, nullable=False)
    redirect_url: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer, autoincrement=True, primary_key=True, index=True
    )
    transaction_id: Mapped[str] = mapped_column(
        String, unique=True, nullable=False, index=True
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default=TransactionStatusEnum.PENDING
    )
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(User.id, ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    email_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user: Mapped["User"] = relationship(back_populates="transactions")
