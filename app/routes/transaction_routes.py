import datetime
import hashlib
import uuid
from http import HTTPStatus
from urllib.parse import unquote

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import config
from app.database.db_actions import get_one_or_create
from app.database.db_init import get_db
from app.logging_init import get_logger
from app.models.db_models import Transaction, User
from app.models.enums import TransactionStatusEnum
from app.services.transaction_services import confirm_payment

logger = get_logger()
router = APIRouter()


@router.post("/payment-notification", status_code=HTTPStatus.OK)
async def payment_notification(  # noqa: C901
    request: Request,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
) -> dict[str, int]:
    form_data = await request.form()
    parsed_data = {key: unquote(value) for key, value in form_data.items()}

    transaction_id = parsed_data.get("TransactionId")
    status = parsed_data.get("Status")
    amount = float(parsed_data.get("Amount"))
    email = parsed_data.get("Email")

    if not transaction_id or not amount or not email:
        logger.error("Did not receive transaction_id or amount or email")
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Missing required fields"
        )

    if status not in [
        TransactionStatusEnum.COMPLETED,
        TransactionStatusEnum.AUTHORIZED,
    ]:
        logger.error(
            "Unsupported payment status (Status is not in ['Completed', 'Authorized']"
        )
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST, detail="Unsupported payment status"
        )

    if amount != float(parsed_data.get("PaymentAmount", 0)):
        logger.error(
            f"Payment amount mismatch for transaction {transaction_id}: Amount: "
            f"{amount}, PaymentAmount: {float(parsed_data.get('PaymentAmount', 0))} "
        )
        return {"code": 12}

    first_name, last_name = None, None

    user, _ = await get_one_or_create(
        db=db, model=User, email=email, first_name=first_name, last_name=last_name
    )

    transaction, created = await get_one_or_create(
        db=db,
        model=Transaction,
        transaction_id=transaction_id,
        user_id=user.id,
        status=status,
        amount=amount,
    )
    await db.commit()

    if transaction and not created:
        if transaction.email_sent:
            logger.info(f"Transaction {transaction_id} already processed")
            return {"code": 0}

    try:
        current_time = int(datetime.datetime.now().timestamp())
        password_uuid = str(uuid.uuid4())[:10]
        k_base_string = f"3ykOQzkL2X647dWw8dDx7h5c{email}{current_time}"
        k_hash = hashlib.md5(k_base_string.encode()).hexdigest()

        generated_link = (
            f"{config.frontend.users_login_url}?un={email}"
            f"&pw={password_uuid}&ln={last_name}"
            f"&fn={first_name}&mn="
            f"&g=&e={email}&t={current_time}"
            f"&k={k_hash}"
        )

        background_tasks.add_task(
            confirm_payment,
            transaction_id,
            amount,
            email,
            "Your payment",
            f"Here is your link: {generated_link}",
            db,
        )

    except Exception as e:
        logger.error(f"Failed to manage background task: {e}")
        raise HTTPException(
            status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
            detail="Failed to manage background task",
        )

    return {"code": 0}
