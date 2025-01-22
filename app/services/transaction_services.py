from base64 import b64encode
from http import HTTPStatus
from typing import Any

from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.database.db_actions import mark_email_sent, set_transaction_status
from app.logging_init import get_logger
from app.models.enums import TransactionStatusEnum
from app.services.email_services import send_email_success

logger = get_logger()


async def get_transaction_status(transaction_id: str) -> dict[str, Any]:
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
        logger.error(f"Failed to fetch transaction status: {response.json()}")
        raise ValueError(f"Failed to fetch transaction status: {response.json()}")


async def confirm_payment(
    transaction_id: str,
    amount: float,
    to_email: str,
    subject: str,
    body: str,
    db: AsyncSession,
):
    received_transaction = await get_transaction_status(transaction_id)
    if not received_transaction.get("Success"):
        logger.error(
            f"Transaction with id: {transaction_id} was not successful: {received_transaction}"  # noqa: E501
        )
        raise ValueError(f"Transaction fetch failed: {received_transaction}")

    transaction_data = received_transaction.get("Model", {})
    status = transaction_data.get("Status")

    if status == TransactionStatusEnum.AUTHORIZED:
        auth_header = b64encode(
            f"{config.cloudpayments.public_id}:{config.cloudpayments.api_secret}".encode()  # noqa: E501
        ).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json",
        }
        url = config.cloudpayments.confirmation_url
        data = {"TransactionId": transaction_id, "Amount": amount}

        async with AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)

        if response.status_code == HTTPStatus.OK and response.json().get("Success"):
            logger.info("Transaction was confirmed")
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
    elif status == TransactionStatusEnum.COMPLETED:
        logger.info("Transaction status is: COMPLETED")
        await set_transaction_status(
            db, transaction_id, TransactionStatusEnum.COMPLETED
        )
    else:
        logger.info(f"Transaction is not authorized yet. Current status: {status}")
