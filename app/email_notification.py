import smtplib

async def send_email(email_to: str, message: str):
    with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
        smtp.starttls()
        smtp.login("devforge.sirius@gmail.com", "tudd hfto gmot alsk")
        await smtp.sendmail("devforge.sirius@gmail.com", email_to, message)