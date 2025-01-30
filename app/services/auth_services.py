from fastapi import Depends, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from http import HTTPStatus

from app.config import config

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if (
            credentials.username != config.application.auth_username or
            credentials.password != config.application.auth_password
    ):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail="Invalid credentials",
            headers={
                "WWW-Authenticate": "Basic"},
        )
