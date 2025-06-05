from typing import Generic, Literal, TypeVar
from datetime import datetime

from pydantic import BaseModel, EmailStr, ConfigDict

from app.models.enums import UserRoleEnum

T = TypeVar("T")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None


class EmailRequest(BaseModel):
    mail_type: Literal["hr", "info"]
    name: str
    email: EmailStr
    phone: str
    message: str


class PaymentNotification(BaseModel):
    TransactionId: int
    Amount: float
    Currency: str | None = None
    PaymentAmount: float
    PaymentCurrency: str | None = None
    OperationType: str | None = None
    InvoiceId: str | None = None
    AccountId: str | None = None
    SubscriptionId: str | None = None
    Name: str | None = None
    Email: str | None = None
    DateTime: str | None = None
    IpAddress: str | None = None
    IpCountry: str | None = None
    IpCity: str | None = None
    IpRegion: str | None = None
    IpDistrict: str | None = None
    IpLatitude: float | None = None
    IpLongitude: float | None = None
    CardId: str | None = None
    CardFirstSix: str | None = None
    CardLastFour: str | None = None
    CardType: str | None = None
    CardExpDate: str | None = None
    Issuer: str | None = None
    IssuerBankCountry: str | None = None
    Description: str | None = None
    AuthCode: str | None = None
    TestMode: int | None = None
    Status: str | None = None
    GatewayName: str | None = None
    Data: str | None = None
    TotalFee: float | None = None
    CardProduct: str | None = None
    PaymentMethod: str | None = None
    CustomFields: str | None = None


class PromoBase(BaseModel):
    name: str
    promo_code: str
    redirect_url: str
    is_active: bool


class PromoResponse(PromoBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    role: UserRoleEnum
    created_at: datetime
    first_name: str | None = None
    last_name: str | None = None


class PaginationResponse(BaseModel, Generic[T]):
    items: list[T]
    count: int
    page: int
    per_page: int

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        from_attributes=True
    )
