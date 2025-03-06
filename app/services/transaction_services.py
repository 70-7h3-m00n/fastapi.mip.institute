import asyncio
from base64 import b64encode
from http import HTTPStatus
from httpx import AsyncClient
from json import JSONDecodeError
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Any

from app.config import config
from app.database.db_actions import mark_email_sent
from app.logging_init import get_logger
from app.services.email_services import send_email_success

logger = get_logger()


async def get_transaction_status(transaction_id: str) -> dict[str, Any]:
    public_id = config.cloudpayments.public_id
    api_secret = config.cloudpayments.api_secret
    logger.info(f"Using Public ID: {public_id} and API Secret: {api_secret}")
    auth_header = b64encode(
        f"{config.cloudpayments.public_id}:{config.cloudpayments.api_secret}".encode()
    ).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
    }
    url = config.cloudpayments.status_url
    data = {"TransactionId": transaction_id}

    async with AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)
        if response.status_code == HTTPStatus.OK:
            return response.json()
        try:
            error_details = response.json()  # Attempt to parse the response JSON
        except JSONDecodeError:
            error_details = response.text  # Fallback to raw text if JSON parsing fails

        raise ValueError(f"Failed to fetch transaction status: {error_details}")


async def confirm_payment(
    transaction_id: str,
    amount: float,
    to_email: str,
    subject: str,
    body: str,
    db: AsyncSession,
):
    await asyncio.sleep(5)
    auth_header = b64encode(
        f"{config.cloudpayments.public_id}:{config.cloudpayments.api_secret}".encode()  # noqa: E501
    ).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
    }
    url = config.cloudpayments.customer_receipt_url
    data = {
        "inn": config.cloudpayments.inn,
        "Type": "Income",
        "CustomerReceipt": {
            "Items": [
                {
                    "label": "Образовательная услуга",  # наименование товара
                    "price": amount,  # цена
                    "quantity": 1.00,  # количество
                    "amount": amount,  # сумма
                    "vat": "null",  # ставка НДС
                    "method": 1,  # тег-1214 признак способа расчета
                    "object": 4,  # тег-1212 признак предмета товара, работы, услуги
                    "measurementUnit": "шт",  # единица измерения
                },
            ],
            "calculationPlace": "mip.institute",  # место осуществления расчёта
            "taxationSystem": 0,  # система налогообложения; необязательный
            "email": to_email,  # e-mail покупателя, если нужно отправить письмо с чеком
            "amounts": {
                "electronic": amount,  # Сумма оплаты электронными деньгами
            }
        }
    }

    async with AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

    if response.status_code == HTTPStatus.OK and response.json().get("Success"):
        logger.info("Customer receipt was created")
        mailed = await send_email_success(to_email, subject, body)
        if mailed:
            logger.info("Email sent successfully")
            await mark_email_sent(db, transaction_id)
        else:
            logger.warning("Email was not sent")
        return response.json()
    else:
        logger.error(
            f"Transaction was NOT confirmed: {response.status_code}, {response.json()}"  # noqa: E501
        )
