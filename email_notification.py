import asyncio
import smtplib
from email.message import EmailMessage


async def send_email(email_to: str, title: str, content: str):

    msg = EmailMessage()
    msg["Subject"] = title
    msg["From"] = "devforge.sirius@gmail.com"
    msg["To"] = email_to
    msg.set_content(content)

    def send():
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login("devforge.sirius@gmail.com", "tudd hfto gmot alsk")
            smtp.sendmail(
                "devforge.sirius@gmail.com",
                email_to,
                msg.as_string()
            )

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, send)