from health_api.settings.base import *

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_HOST_USER = "info@healthnpalms.com"


DEBUG = True

ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = ["https://*.eu.ngrok.io"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config.get("RDS_NAME"),
        "HOST": config.get("RDS_HOST"),
        "PORT": config.get("RDS_PORT"),
        "USER": config.get("RDS_USER"),
        "PASSWORD": config.get("RDS_PASSWORD"),
    }
}


GOOGLE_CLIENT_ID = config.get("GOOGLE_CLIENT_ID")

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

BASE_URL = "https://a785-102-89-33-37.eu.ngrok.io"

LOGGING["root"]["level"] = "DEBUG"  # noqa

DEFAULT_CHARSET = "utf-8"

FRONTEND_BASE_URL = "http://localhost:3000"


# TODO: setup aws s3 bucket storage
STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3.S3Storage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

AWS_ACCESS_KEY_ID = config.get("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config.get("AWS_SECRET_ACCESS_KEY")
AWS_STORAGE_BUCKET_NAME = config.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_REGION_NAME = config.get("AWS_S3_REGION_NAME")
AWS_S3_SIGNATURE_VERSION = config.get("AWS_S3_SIGNATURE_VERSION")
AWS_S3_VERIFY = bool(config.get("AWS_S3_VERIFY", ""))
AWS_QUERYSTRING_AUTH = bool(config.get("AWS_QUERYSTRING_AUTH", ""))

# TODO: update keys below
PAYSTACK_PUBLIC_KEY = config.get("PAYSTACK_PUBLIC_KEY")
PAYSTACK_SECRET_KEY = config.get("PAYSTACK_SECRET_KEY")

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("127.0.0.1", 6379)],
        },
    },
}
