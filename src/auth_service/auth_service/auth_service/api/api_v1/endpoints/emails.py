from typing import Any

from fastapi import APIRouter, Depends, Body
from fastapi.params import Param
from fastapi_mail import MessageSchema
from pydantic import EmailStr
from starlette import status
from starlette.responses import Response

from auth_service import models
from auth_service.api.deps import auth
from auth_service.api.deps.auth import RoleChecker
from auth_service.services.email import Email

router = APIRouter()


@router.post(
    "/send",
    dependencies=[Depends(RoleChecker(["admin", "manager"]))],
)
async def send_email_asynchronous(
    subject: str,
    recipients: str = Param(..., description="delimiter: `,`"),
    body: Any = Body(..., media_type="text/base"),
    current_user: models.User = Depends(auth.get_active_current_user),
):
    email = Email(EmailStr(current_user.email))
    recipients = [
        EmailStr(x)
        for x in tuple(
            recipients.strip(" ").split(","),
        )
        if x != ""
    ]
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype="html",
    )
    await email.send_message(message)
    return Response(status_code=status.HTTP_200_OK)
