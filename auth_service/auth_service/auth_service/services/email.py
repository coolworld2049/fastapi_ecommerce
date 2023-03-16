from typing import List, Any

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr, BaseModel
from starlette.background import BackgroundTasks

from auth_service.core.config import get_app_settings


class EmailSchema(BaseModel):
    email: List[EmailStr]


class Email:
    def __init__(
        self,
        sender: EmailStr,
    ):
        self.sender = sender
        self.templates = get_app_settings().templates
        self.conf = ConnectionConfig(
            MAIL_USERNAME=get_app_settings().EMAIL_USERNAME,
            MAIL_PASSWORD=get_app_settings().EMAIL_PASSWORD,
            MAIL_FROM=get_app_settings().EMAIL_USERNAME,
            MAIL_PORT=get_app_settings().EMAIL_PORT,
            MAIL_SERVER=get_app_settings().EMAIL_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )

    async def send_email(
        self,
        subject: str,
        recipients: list[EmailStr] | tuple[EmailStr],
        body: dict | Any,
        use_background_task=False,
        background_tasks: BackgroundTasks = None,
    ):
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="base",
        )
        fast_mail = FastMail(self.conf)
        if not use_background_task:
            await fast_mail.send_message(
                message, template_name="/email/email.base"
            )
        if use_background_task:
            background_tasks.add_task(
                fast_mail.send_message,
                message,
                template_name="/email/email.base",
            )

    async def send_verification_code(
        self,
        subject,
        recipient: EmailStr,
        verify_token_url,
        full_name,
        token,
        **kwargs,
    ):
        template = self.templates.get_template(
            f"/verif_email/verification.base"
        )
        html = template.render(
            url=f"{verify_token_url}/{token}", full_name=full_name, **kwargs
        )
        await self.send_email(subject, recipients=[recipient], body=html)
