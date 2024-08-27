from django.db.models import TextChoices


class BOOKING_STATUS(TextChoices):
    CANCELLED = "Cancelled"
    PENDING = "Pending"
    ACCEPTED = "Accepted"
    ACTIVE = "Active"
    COMPLETED = "Completed"
