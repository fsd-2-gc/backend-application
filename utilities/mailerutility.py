import logging
import os
import sys
import json
import boto3
from botocore.exceptions import ClientError

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logger = logging.getLogger(__name__)


def _get_ses_client():
    """
    Retrieves the SES client using explicit credentials from environment variables.
    """
    region = os.getenv("AWS_REGION")
    aws_access_key = os.getenv("AWS_ACCESS_KEY_ID")
    aws_secret_key = os.getenv("AWS_SECRET_ACCESS_KEY")

    if not aws_access_key or not aws_secret_key:
        logger.error("Missing AWS credentials in environment variables.")
        return None

    return boto3.client(
        "ses",
        region_name=region,
        aws_access_key_id=aws_access_key,
        aws_secret_access_key=aws_secret_key
    )


def _send_ses_email(to_email: str, template_name: str, template_data: dict, source_email: str) -> bool:
    client = _get_ses_client()

    try:
        serialized_data = json.dumps(template_data)

        response = client.send_templated_email(
            Source=source_email,
            Destination={
                "ToAddresses": [to_email]
            },
            Template=template_name,
            TemplateData=serialized_data
        )

        logger.info("SES email sent to %s. MessageId: %s", to_email, response.get("MessageId"))
        return True

    except ClientError as e:
        logger.error("SES send failed to %s: %s", to_email, e.response['Error']['Message'])
        return False
    except Exception as e:
        logger.exception("Unexpected error sending SES email: %s", e)
        return False


def send_confirmation_mail(to_email: str, template_model: dict) -> bool:
    """
    Sends booking confirmation via AWS SES.
    Requires env: AWS_SES_SENDER, AWS_SES_CONFIRMATION_TEMPLATE
    """
    sender = os.getenv("AWS_SES_SENDER")
    template_name = os.getenv("AWS_SES_CONFIRMATION_TEMPLATE")

    if not all([sender, template_name]):
        logger.error("Configuration error: AWS_SES_SENDER or AWS_SES_CONFIRMATION_TEMPLATE is missing.")
        return False

    return _send_ses_email(to_email, template_name, template_model, sender)


def send_cancellation_mail(to_email: str, template_model: dict) -> bool:
    """
    Sends cancellation email via AWS SES.
    Requires env: AWS_SES_SENDER, AWS_SES_CANCELLATION_TEMPLATE
    """
    sender = os.getenv("AWS_SES_SENDER")
    template_name = os.getenv("AWS_SES_CANCELLATION_TEMPLATE")

    if not all([sender, template_name]):
        logger.error("Configuration error: AWS_SES_SENDER or AWS_SES_CANCELLATION_TEMPLATE is missing.")
        return False

    return _send_ses_email(to_email, template_name, template_model, sender)
