from enum import Enum


class TransactionStatusEnum(str, Enum):
    AUTHORIZED = "Authorized"
    PENDING = "Pending"
    COMPLETED = "Completed"
