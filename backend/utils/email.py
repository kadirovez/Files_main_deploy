
import httpx
import resend
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import ssl
from email.utils import formataddr
from fastapi import HTTPException
from starlette import status

from backend.core.settings import settings

resend.api_key = settings.resend_api_key

async def send_email(
        receiver_email: str,
        subject: str,
        body: str
) -> None:
    """Send email via Brevo API."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.brevo.com/v3/smtp/email",
            headers={
                "api-key": settings.brevo_api_key,
                "Content-Type": "application/json"
            },
            json={
                "sender": {
                    "name": settings.smtp_sender_name,
                    "email": settings.smtp_sender_email
                },
                "to": [{"email": receiver_email}],
                "subject": subject,
                "htmlContent": body
            }
        )
        if response.status_code != 201:
            raise Exception(f"Failed to send email: {response.text}")

# async def send_email(
#         receiver_email: str,
#         subject: str,
#         body: str
# ) -> None:
#     """Send email via SMTP. Native async using aiosmtplib."""
#     try:
#             resend.Emails.send({
#                     "from": "SuperChat <onboarding@resend.dev>",
#         "to": receiver_email,
#         "subject": subject,
#         "html": body
#             })
        # msg = MIMEMultipart()
        # msg["Reply-To"] = settings.smtp_sender_email
        # msg["From"] = formataddr((settings.smtp_sender_name, settings.smtp_sender_email))
        # msg["To"] = receiver_email
        # msg["Subject"] = subject
        # msg.attach(MIMEText(body, "html"))

        # ssl_context = ssl.create_default_context()
        # ssl_context.check_hostname = False
        # ssl_context.verify_mode = ssl.CERT_NONE

        # await aiosmtplib.send(
        #     msg,
        #     hostname=settings.smtp_server,
        #     port=settings.smtp_port,
        #     username=settings.smtp_user,
        #     password=settings.smtp_password,
        #     start_tls=True,
        #     tls_context=ssl_context,
        # )


    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email: {str(e)}"
        )

# async def send_email(generated_otp):
#     print(generated_otp)
#     return generated_otp
