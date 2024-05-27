import uuid
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.exceptions import APIException
import random
import hashlib

from PIL import Image, ImageDraw, ImageFont
import io
from django.core.files.base import ContentFile
from django.core.cache import cache


def check_verification_pin(email, verification_code) -> bool:
    return cache.get(email) == verification_code


def generate_avatar(initials, size=256, text_color=(0, 0, 0), font_path=None):
    # Generate random background color
    background_color = generate_background_color(text_color)

    # Create a square image
    image = Image.new("RGB", (size, size), background_color)
    draw = ImageDraw.Draw(image)

    # Load font
    if font_path is None:
        font_path = ImageFont.load_default()
    else:
        font_path = ImageFont.truetype(font_path, size=size // 2)

    # Calculate text size and position
    # text_width, text_height = draw.textsize(initials, font=font_path)
    text_x = size - 20
    text_y = size - 20

    # Draw text on the image
    draw.text(
        (text_x, text_y),
        initials,
        align="center",
        stroke_width=4,
        fill=text_color,
        font=font_path,
    )

    # Create an in-memory binary stream
    img_byte_array = io.BytesIO()

    # Save the image to the in-memory stream
    image.save(img_byte_array, format="PNG")

    # Create a Django ContentFile object
    image_file = ContentFile(img_byte_array.getvalue(), "avatar.png")

    print(
        "Loook!!!!",
        image_file.name,
        image_file.size,
        img_byte_array.getvalue(),
    )
    return image_file


def generate_background_color(text_color):
    # Ensure high contrast between text color and background color
    while True:
        background_color = (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255),
        )
        # Calculate luminance using relative luminance formula
        luminance = (
            0.2126 * background_color[0]
            + 0.7152 * background_color[1]
            + 0.0722 * background_color[2]
        ) / 255
        text_luminance = (
            0.2126 * text_color[0]
            + 0.7152 * text_color[1]
            + 0.0722 * text_color[2]
        ) / 255
        # Ensure luminance difference is greater than 0.5 for high contrast
        if abs(luminance - text_luminance) > 0.5:
            break
    return background_color


def get_order_by(order_by, order_dir):
    return f"{'-' if order_dir == 'dsc' else ''}{order_by}"


def get_uuid():
    return uuid.uuid4().hex


def get_uuid_hex(uuid_value):
    return (
        uuid.UUID(uuid_value).hex
        if type(uuid_value) is str
        else uuid_value.hex
    )


def generate_code():
    return random.SystemRandom().randrange(100000, 999999)


def generate_hash(val):
    return hashlib.sha256(get_uuid().encode() + val.encode()).hexdigest()


def avatar_file_name(instance, filename):
    return "/".join(
        [
            "images",
            "avatars",
            "{}_{}_{}".format(instance.username, get_uuid(), filename).lower(),
        ]
    )


def medical_upload_file_name(instance, filename):
    return "/".join(
        [
            "files",
            "medical-uploads",
            "{}_{}_{}".format(instance.username, get_uuid(), filename).lower(),
        ]
    )


def custom_exception_handler(exc, context):
    """Handle Django ValidationError as an accepted exception
    Must be set in settings:
    # ...
    'EXCEPTION_HANDLER': 'mtp.apps.common.drf.exception_handler',
    # ...
    For the parameters, see ``exception_handler``
    """

    if (
        isinstance(exc, DjangoValidationError)
        or isinstance(exc, IntegrityError)
        or isinstance(exc, ObjectDoesNotExist)
    ):
        if hasattr(exc, "message_dict"):
            exc = DRFValidationError(detail=exc.message_dict)
        elif hasattr(exc, "message"):
            exc = DRFValidationError(
                detail={"non_field_errors": [exc.message]}
            )
        elif hasattr(exc, "messages"):
            exc = DRFValidationError(detail={"non_field_errors": exc.messages})
        else:
            exc = DRFValidationError(detail={"non_field_errors": [str(exc)]})
    elif type(exc) is Exception:
        exc = APIException(detail={"detail": exc.message})

    return drf_exception_handler(exc, context)


def send_template_email(template, email, subject, **context):
    if not isinstance(email, list):
        email = [email]
    # context["instagram_url"] = settings.SOCIAL_MEDIA_INSTAGRAM_URL
    # context["facebook_url"] = settings.SOCIAL_MEDIA_FACEBOOK_URL
    # context["linkedin_url"] = settings.SOCIAL_MEDIA_LINKEDIN_URL
    # context["twitter_url"] = settings.SOCIAL_MEDIA_TWITTER_URL
    context["email"] = "".join(email)
    html_message = render_to_string(template, context)
    plain_message = strip_tags(html_message)

    send_mail(
        subject,
        plain_message,
        "DashLyft <{}>".format(settings.EMAIL_HOST_USER),
        email,
        html_message=html_message,
    )
