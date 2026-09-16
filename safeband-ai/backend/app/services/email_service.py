import os
from email.message import EmailMessage

import aiosmtplib
from dotenv import load_dotenv


load_dotenv()

import os
from dotenv import load_dotenv

load_dotenv()

print("SMTP HOST:", os.getenv("SMTP_HOST"))
print("SMTP PORT:", os.getenv("SMTP_PORT"))
print("SMTP USERNAME:", os.getenv("SMTP_USERNAME"))
print(
    "SMTP PASSWORD LENGTH:",
    len(os.getenv("SMTP_PASSWORD", "").replace(" ", ""))
)
print("CAREGIVER EMAIL:", os.getenv("CAREGIVER_EMAIL"))


SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
CAREGIVER_EMAIL = os.getenv("CAREGIVER_EMAIL")


async def send_emergency_email(
    user_id: str,
    message: str,
    severity: str,
    risk_score: int,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict:
    if not SMTP_USERNAME:
        raise RuntimeError("SMTP_USERNAME is missing in .env")

    if not SMTP_PASSWORD:
        raise RuntimeError("SMTP_PASSWORD is missing in .env")

    if not CAREGIVER_EMAIL:
        raise RuntimeError("CAREGIVER_EMAIL is missing in .env")

    email = EmailMessage()

    email["From"] = SMTP_USERNAME
    email["To"] = CAREGIVER_EMAIL
    email["Subject"] = (
        f"SafeBand AI Emergency Alert - "
        f"{severity.upper()} Risk"
    )

    location_text = "Unavailable"

    if latitude is not None and longitude is not None:
        location_text = (
            f"Latitude: {latitude}\n"
            f"Longitude: {longitude}"
        )

    email.set_content(
        f"""SafeBand AI Emergency Alert

User ID: {user_id}
Severity: {severity}
Risk Score: {risk_score}/100

Message:
{message}

Location:
{location_text}

This is an automated prototype notification.
"""
    )

    await aiosmtplib.send(
        email,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        start_tls=True,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
    )

    return {
        "success": True,
        "status": "email_sent",
        "recipient": CAREGIVER_EMAIL,
    }