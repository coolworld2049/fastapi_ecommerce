from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr

from auth_service.core.config import get_app_settings


class Email(FastMail):
    def __init__(self, sender: EmailStr):
        config = ConnectionConfig(
            MAIL_USERNAME=get_app_settings().SMTP_USERNAME,
            MAIL_PASSWORD=get_app_settings().SMTP_PASSWORD,
            MAIL_FROM=sender,
            MAIL_PORT=get_app_settings().SMTP_PORT,
            MAIL_SERVER=get_app_settings().SMTP_HOST,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
        )
        super().__init__(config)

    async def send_verification_code(
        self,
        subject: str,
        recipients: list[EmailStr],
        data: dict,
    ):
        template = get_app_settings().jinja_templates.get_template(
            f"/verif_email/verification.html"
        )
        body = template.render(**data)
        message = MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            subtype="html",
        )
        await self.send_message(message)
