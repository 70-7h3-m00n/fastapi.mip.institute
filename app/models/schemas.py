from pydantic import BaseModel


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
