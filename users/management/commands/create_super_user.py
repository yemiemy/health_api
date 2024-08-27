import logging


from django.conf import settings
from django.core.management.base import BaseCommand

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Creates super user if no user is found"

    def handle(self, *args, **options):
        from users.models import User

        # check if admin doesn't exists
        if not User.objects.filter(is_staff=True).exists():
            logger.info(
                "Health-In-Palms admin does not exist. Creating admin..."
            )
            admin = User.objects.create_superuser(
                username=settings.DJANGO_SU_NAME,
                email=settings.DJANGO_SU_EMAIL,
                password=settings.DJANGO_SU_PASSWORD,
            )
            logger.info("Created Health-In-Palms admin {}".format(admin))
