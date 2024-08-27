from users.managers import UserManager
from users.utils import (
    avatar_file_name,
    generate_code,
)
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField  # type: ignore
from users.tasks import (
    send_account_verification_mail,
    send_forgot_password_mail,
)
from users.utils import get_uuid
from users.choices import (
    SPECIALIZATION_CHOICES,
    GENDER_CHOICES,
    SMOKING_STATUS,
    ALCOHOL_CONSUMPTION,
    PREFERRED_LANGUAGE,
    GENOTYPES,
    BLOODGROUP,
)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    avatar = models.ImageField(
        upload_to=avatar_file_name, default="avatar.png"
    )
    date_of_birth = models.DateField(blank=True, null=True)
    phone_number = PhoneNumberField(
        _("phone number"),
        blank=True,
        null=True,
        unique=True,
        validators=[
            RegexValidator(
                regex=settings.PHONENUMBER_REGEX_PATTERN,
                message="The phone number entered is not valid",
                code="invalid_phone_number",
            ),
        ],
    )
    gender = models.CharField(
        max_length=1, choices=GENDER_CHOICES.choices, null=True, blank=True
    )
    # address = models.TextField()
    address_1 = models.CharField(max_length=500, null=True, blank=True)
    address_2 = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=254, null=True, blank=True)
    country = models.CharField(max_length=254, null=True, blank=True)
    is_email_verified = models.BooleanField(_("email verified"), default=False)
    is_phone_number_verified = models.BooleanField(
        _("phone number verified"), default=False
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    @property
    def full_name(self):
        return self.get_full_name()

    def send_verification_email(self):
        verification_code = generate_code()
        cache.set(self.email, verification_code)

        send_account_verification_mail.delay(
            self.first_name, self.email, verification_code
        )

    def check_verification_pin(self, verification_code) -> bool:
        return cache.get(self.email) == verification_code

    def verify_account(self, verification_code) -> bool:
        if self.check_verification_pin(verification_code):
            self.is_email_verified = True
            self.save()
            # TODO: send a welcome email here, if need be
            cache.delete(self.email)
            return True
        return False

    def send_reset_token_email(self):
        reset_token = generate_code()
        cache.set(reset_token, self.email)

        send_forgot_password_mail.delay(
            self.first_name, self.email, reset_token
        )


class Patient(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    allergies = models.CharField(max_length=255, null=True, blank=True)
    blood_group = models.CharField(
        max_length=2, null=True, blank=True, choices=BLOODGROUP.choices
    )
    genotype = models.CharField(
        max_length=2, null=True, blank=True, choices=GENOTYPES.choices
    )
    smoking_status = models.CharField(
        max_length=1, choices=SMOKING_STATUS.choices, default="N"
    )
    alcohol_consumption = models.CharField(
        max_length=1, choices=ALCOHOL_CONSUMPTION.choices, default="N"
    )
    height = models.FloatField(null=True, blank=True)
    weight = models.FloatField(null=True, blank=True)
    bmi = models.FloatField(null=True, blank=True)
    emergency_contact = models.TextField(null=True, blank=True)
    preferred_pharmacy = models.TextField(null=True, blank=True)
    preferred_language = models.CharField(
        max_length=20, choices=PREFERRED_LANGUAGE.choices, default="English"
    )

    def __str__(self) -> str:
        return f"Patient <> {self.user.username}"


# Define model for Medical History
class MedicalHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="medical_history"
    )
    medical_conditions = models.TextField(null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    immunization_history = models.TextField(null=True, blank=True)
    family_medical_history = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


# Define model for Vital Signs
class VitalSigns(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    blood_pressure = models.CharField(max_length=20, null=True, blank=True)
    heart_rate = models.CharField(max_length=20, null=True, blank=True)
    temperature = models.CharField(max_length=20, null=True, blank=True)
    respiratory_rate = models.CharField(max_length=20, null=True, blank=True)


"""
    Medical Professional Section
"""


class MedicalProfessional(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    # Professional Information
    medical_license_number = models.CharField(
        max_length=50, null=True, blank=True
    )
    specialization = models.CharField(
        max_length=100,
        choices=SPECIALIZATION_CHOICES.choices,
        null=True,
        blank=True,
    )
    education_and_qualifications = models.TextField(null=True, blank=True)
    work_history = models.TextField(null=True, blank=True)
    certifications = models.TextField(null=True, blank=True)

    # Clinical Practice Information
    department = models.CharField(max_length=100, null=True, blank=True)
