from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import HTTPBasicCredentials
from http import HTTPStatus

from app.models.schemas import EmailRequest
from app.services.auth_services import verify_credentials
from app.services.email_services import prepare_info_message, send_email

router = APIRouter()


@router.post("/send", status_code=HTTPStatus.OK)
async def send_mail(
    request: EmailRequest,
    credentials: HTTPBasicCredentials = Depends(verify_credentials),
) -> Response:
    try:
        recipient, subject, body = await prepare_info_message(
            request.mail_type, request.email, request.name, request.phone, request.message
        )

        success = await send_email(
            recipient=recipient,
            subject=subject,
            body=body
        )

        if success:
            return Response(content="Email sent successfully")
        else:
            raise HTTPException(status_code=500, detail="Failed to send email")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
