import base64
import datetime
import hashlib
import os
import uuid
from asyncio import sleep as asleep
from urllib.parse import unquote

import httpx
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Request, Depends

from app.db_middleware.db_actions import mark_email_sent, add_transaction
from app.db_middleware.db_dependency import get_db
from app.logging_init import logger
from app.models import ProcessedTransaction
from app.utils import send_email_success

load_dotenv()

router = APIRouter()

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session


@router.post("/payment-notification", include_in_schema=False)
async def payment_notification(request: Request, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    form_data = await request.form()
    parsed_data = {key: unquote(value) for key, value in form_data.items()}
    # print(parsed_data)

    transaction_id = parsed_data.get("TransactionId")
    status = parsed_data.get("Status")
    amount = parsed_data.get("Amount")
    email = parsed_data.get("Email")

    if not transaction_id or not amount or not email:
        logger.error(f"Did not receive transaction_id or amount or email")
        raise HTTPException(status_code=400, detail="Missing required fields")

    try:
        first_name = parsed_data.get("Name").split(' ')[0]
        last_name = parsed_data.get("Name").split(' ')[1]
    except Exception as e:
        logger.warning(f"Could not parse 'Name' so keeping it blank: {e}")
        first_name = last_name = parsed_data.get("Name")

    transaction = db.query(ProcessedTransaction).filter_by(transaction_id=transaction_id).first()

    if transaction:
        if transaction.email_sent:
            logger.info(f"Transaction {transaction_id} already processed")
            return {"code": 0}
    else:
        try:
            add_transaction(db, transaction_id, status, amount)
        except Exception as e:
            logger.error(f"Failed to add transaction {transaction_id}: {e}")
            raise HTTPException(status_code=500, detail="Failed to process transaction")

    try:
        current_time = int(datetime.datetime.now().timestamp())
        password_uuid = str(uuid.uuid4())[:10]
        k_base_string = f"3ykOQzkL2X647dWw8dDx7h5c{email}{current_time}"
        k_hash = hashlib.md5(k_base_string.encode()).hexdigest()

        generated_link = (f'https://lms.mip.institute/local/ilogin/rlogin.php?un={email}'
                          f'&pw={password_uuid}&ln={last_name}'
                          f'&fn={first_name}&mn='
                          f'&g=&e={email}&t={current_time}'
                          f'&k={k_hash}')

        background_tasks.add_task(confirm_payment, parsed_data['TransactionId'], parsed_data['Amount'],
                                  parsed_data['Email'], 'Your payment',
                                  f'Here is your link: {generated_link}', db)

    except Exception as e:
        logger.error(f"Failed to manage background task: {e}")
        raise HTTPException(status_code=500, detail="Failed to manage background task")

    if parsed_data.get("Status") not in ["Completed", "Authorized"]:
        logger.error(f"Unsupported payment status (Status is not in ['Completed', 'Authorized']")
        raise HTTPException(status_code=400, detail="Unsupported payment status")

    if float(parsed_data.get("Amount", 0)) != float(parsed_data.get("PaymentAmount", 0)):
        logger.error(f"Payment amount mismatch for transaction {transaction_id}: Amount: "
                     f"{float(parsed_data.get("Amount", 0))}, PaymentAmount: {float(parsed_data.get("Amount", 0))} ")
        raise HTTPException(status_code=400, detail="Payment amount mismatch")

    return {"code": 0}


async def get_transaction_status(transaction_id):
    auth_header = base64.b64encode(
        f"{os.getenv('CLOUDPAYMENTS_PUBLIC_ID')}:{os.getenv('CLOUDPAYMENTS_API_SECRET')}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/json",
    }
    url = "https://api.cloudpayments.ru/payments/get"
    data = {"TransactionId": transaction_id}

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        logger.error(f"Failed to fetch transaction status: {response.json()}")
        raise ValueError(f"Failed to fetch transaction status: {response.json()}")


async def confirm_payment(transaction_id, amount, to_email, subject, body, db):
    await asleep(5)
    transaction = await get_transaction_status(transaction_id)
    if not transaction.get("Success"):
        logger.error(f"Transaction was not successful: {transaction}")
        raise ValueError(f"Transaction fetch failed: {transaction}")

    transaction_data = transaction.get("Model", {})
    status = transaction_data.get("Status")

    if status == "Authorized":
        auth_header = base64.b64encode(
            f"{os.getenv('CLOUDPAYMENTS_PUBLIC_ID')}:{os.getenv('CLOUDPAYMENTS_API_SECRET')}".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Content-Type": "application/json",
        }
        url = "https://api.cloudpayments.ru/payments/confirm"
        data = {"TransactionId": transaction_id, "Amount": amount}

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data, headers=headers)

        if response.status_code == 200 and response.json().get("Success"):
            logger.info(f"Transaction was confirmed")
            mailed = await send_email_success(to_email, subject, body)
            if mailed:
                logger.info(f"Email sent successfully")
                mark_email_sent(db, transaction_id)
            else:
                logger.warning(f"Email was not sent")

            return response.json()
        else:
            logger.error(f"Transaction was NOT confirmed: {response.status_code}, {response.json()}")
    elif status == "Completed":
        logger.info(f"Transaction status is: COMPLETED")
    else:
        logger.info(f"Transaction is not authorized yet. Current status: {status}")
