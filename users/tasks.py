import logging

from health_api.celery import app as celery_app
from django.conf import settings
from datetime import datetime

# from furl import furl

from users.utils import send_template_email

logger = logging.getLogger(__name__)


# SITE_BASE_URL = furl(settings.FRONTEND_BASE_URL)


def get_expiration_time():
    return int(settings.CACHES["default"]["TIMEOUT"] / 60)


@celery_app.task(name="send_account_verification_mail")
def send_account_verification_mail(
    first_name: str, email: str, verification_code: int
):
    logger.info(
        "Sending account verification email for user: {}".format(email)
    )

    send_template_email(
        "account_verification.html",
        email,
        "Account Verification",
        **{
            "account_name": first_name,
            "verification_code": verification_code,
            "expiration_time": get_expiration_time(),
        },
    )

    logger.info("Verfication email sent to user: {}".format(email))


@celery_app.task(name="send_forgot_password_mail")
def send_forgot_password_mail(first_name: str, email: str, reset_token: int):
    logger.info("Sending forgot password email for user: {}".format(email))

    send_template_email(
        "forgot_password.html",
        email,
        "Account Password Reset",
        **{
            "name": first_name,
            "reset_token": reset_token,
            "email_addr": email,
            "expiration_time": get_expiration_time(),
        },
    )

    logger.info("Forgot password email sent to user: {}".format(email))


@celery_app.task(name="send_appointment_booking_mail")
def send_appointment_booking_mail(
    full_name: str,
    recipient_name: str,
    email: str,
    appointment_date,
    appointment_time,
):
    logger.info(
        "Sending Appointment booking email to patient: {}".format(email)
    )

    message = f"We would like to notify you of your upcoming appointment with \
        {recipient_name}. Please find the details below:"

    send_template_email(
        "appointment_notify.html",
        email,
        "Appointment Booking Notification",
        **{
            "full_name": full_name,
            "message": message,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "hospital_address": settings.HOSPITAL_ADDRESS,
            "year": datetime.now().year,
        },
    )

    logger.info("Appointment booking email sent to patient: {}".format(email))


@celery_app.task(name="send_appointment_update_mail")
def send_appointment_update_mail(
    full_name: str,
    recipient_name: str,
    email: str,
    appointment_date,
    appointment_time,
    status: str,
):
    logger.info(
        "Sending Appointment status update email to patient: {}".format(email)
    )

    send_template_email(
        "appointment_status_update.html",
        email,
        "Appointment Booking Notification",
        **{
            "full_name": full_name,
            "doctor_name": recipient_name,
            "appointment_date": appointment_date,
            "appointment_time": appointment_time,
            "status": status,
            "hospital_address": settings.HOSPITAL_ADDRESS,
            "year": datetime.now().year,
        },
    )

    logger.info(
        "Appointment status update email sent to patient: {}".format(email)
    )
