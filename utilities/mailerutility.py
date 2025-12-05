import logging
import requests
import os
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)

POSTMARK_ENDPOINT = "https://api.postmarkapp.com/email/withTemplate"


def send_confirmation_mail(to_email: str, template_model: dict) -> bool:
    api_token = os.getenv("POSTMARK_API_TOKEN")
    template_id = os.getenv("POSTMARK_BOOKING_CONFIRMATION_TEMPLATE_ID")
    from_email = os.getenv("POSTMARK_FROM")

    if not all([api_token, template_id, from_email]):
        logger.error("Configuratiefout: Een of meer environment variables ontbreken.")
        return False

    headers = {
        "X-Postmark-Server-Token": api_token,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "From": from_email,
        "To": to_email,
        "TemplateId": int(template_id) if str(template_id).isdigit() else template_id,
        "TemplateModel": template_model,
    }

    try:
        resp = requests.post(POSTMARK_ENDPOINT, json=payload, headers=headers, timeout=10)

        if 200 <= resp.status_code < 300:
            logger.info("Postmark confirmation email sent to %s", to_email)
            return True

        logger.error("Postmark send failed (%s): %s", resp.status_code, resp.text)
        return False
    except Exception as e:
        logger.exception("Postmark send exception: %s", e)
        return False


def send_cancellation_mail(to_email: str, template_model: dict) -> bool:
    """
    Send a cancellation email using Postmark's sendWithTemplate API.

    Env vars required:
      - POSTMARK_API_TOKEN
      - POSTMARK_BOOKING_CANCELLATION_TEMPLATE_ID
      - POSTMARK_FROM

    Returns True on success, False otherwise. Errors are logged.
    """
    api_token = os.getenv("POSTMARK_API_TOKEN")
    template_id = os.getenv("POSTMARK_BOOKING_CANCELLATION_TEMPLATE_ID")
    from_email = os.getenv("POSTMARK_FROM")

    if not all([api_token, template_id, from_email]):
        logger.error("Configuratiefout: Een of meer environment variables ontbreken voor cancellation mail.")
        return False

    headers = {
        "X-Postmark-Server-Token": api_token,
        "Accept": "application/json",
        "Content-Type": "application/json",
    }

    payload = {
        "From": from_email,
        "To": to_email,
        "TemplateId": int(template_id) if str(template_id).isdigit() else template_id,
        "TemplateModel": template_model,
    }

    try:
        resp = requests.post(POSTMARK_ENDPOINT, json=payload, headers=headers, timeout=10)
        if 200 <= resp.status_code < 300:
            logger.info("Postmark cancellation email sent to %s", to_email)
            return True
        logger.error("Postmark cancellation send failed (%s): %s", resp.status_code, resp.text)
        return False
    except Exception as e:
        logger.exception("Postmark cancellation send exception: %s", e)
        return False
