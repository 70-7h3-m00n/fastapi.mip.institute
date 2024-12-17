from typing import Optional

from pydantic import BaseModel


class PaymentNotification(BaseModel):
    TransactionId: int
    Amount: float
    Currency: Optional[str] = None
    PaymentAmount: float
    PaymentCurrency: Optional[str] = None
    OperationType: Optional[str] = None
    InvoiceId: Optional[str] = None
    AccountId: Optional[str] = None
    SubscriptionId: Optional[str] = None
    Name: Optional[str] = None
    Email: Optional[str] = None
    DateTime: Optional[str] = None
    IpAddress: Optional[str] = None
    IpCountry: Optional[str] = None
    IpCity: Optional[str] = None
    IpRegion: Optional[str] = None
    IpDistrict: Optional[str] = None
    IpLatitude: Optional[float] = None
    IpLongitude: Optional[float] = None
    CardId: Optional[str] = None
    CardFirstSix: Optional[str] = None
    CardLastFour: Optional[str] = None
    CardType: Optional[str] = None
    CardExpDate: Optional[str] = None
    Issuer: Optional[str] = None
    IssuerBankCountry: Optional[str] = None
    Description: Optional[str] = None
    AuthCode: Optional[str] = None
    TestMode: Optional[int] = None
    Status: Optional[str] = None
    GatewayName: Optional[str] = None
    Data: Optional[str] = None
    TotalFee: Optional[float] = None
    CardProduct: Optional[str] = None
    PaymentMethod: Optional[str] = None
    CustomFields: Optional[str] = None
