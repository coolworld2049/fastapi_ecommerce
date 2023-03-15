from typing import Any

from fastapi import APIRouter, Depends, Body
from fastapi.params import Param
from pydantic import EmailStr
from starlette import status
from starlette.background import BackgroundTasks
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
    background_tasks: BackgroundTasks,
    subject: str,
    recipients: str = Param(..., description="delimiter: `,`"),
    body: Any = Body(..., media_type="text/base"),
    use_background_task: bool = Param(True),
    current_user: models.User = Depends(auth.get_current_user),
):
    email = Email(EmailStr(current_user.email))
    recipients = [
        EmailStr(x)
        for x in tuple(
            recipients.strip(" ").split(","),
        )
        if x != ""
    ]
    await email.send_email(
        subject=subject,
        recipients=recipients,
        body=body,
        use_background_task=use_background_task,
        background_tasks=background_tasks,
    )
    return Response(status_code=status.HTTP_200_OK)
