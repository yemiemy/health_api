from django.db import models
from appointments.choices import (
    BOOKING_STATUS,
)
from users.utils import get_uuid
from users.models import MedicalProfessional, Patient
from users.utils import (
    medical_upload_file_name,
)


# Create your models here.
class Availability(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    medical_professional = models.ForeignKey(
        MedicalProfessional,
        on_delete=models.CASCADE,
        related_name="availabilities",
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_booked = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = "Availabilities"


class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    patient = models.ForeignKey(
        Patient, on_delete=models.CASCADE, related_name="appointments"
    )
    medical_professional = models.ForeignKey(
        MedicalProfessional,
        on_delete=models.CASCADE,
        related_name="appointments",
    )
    note = models.TextField(null=True, blank=True)
    status = models.CharField(
        max_length=50,
        choices=BOOKING_STATUS.choices,
        default=BOOKING_STATUS.PENDING,
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


# Define model for Visit History
class VisitHistory(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    appointment = models.OneToOneField(
        Appointment, on_delete=models.SET_NULL, null=True
    )
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    medical_professional = models.ForeignKey(
        MedicalProfessional,
        on_delete=models.CASCADE,
        related_name="encounters",
    )
    visit_date = models.DateField(null=True, blank=True)
    reason_for_visit = models.TextField(null=True, blank=True)
    treatments_received = models.TextField(null=True, blank=True)
    physician_notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return (
            f"{self.patient} - {self.medical_professional} - {self.visit_date}"
        )


# Define model for Laboratory and Diagnostic Test Results
class TestResult(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    visit_history = models.ForeignKey(VisitHistory, on_delete=models.CASCADE)
    blood_tests = models.TextField()
    imaging_studies = models.TextField()
    electrocardiogram = models.TextField()
    other_tests = models.TextField()


class MedicalUpload(models.Model):
    id = models.UUIDField(primary_key=True, default=get_uuid, editable=False)
    visit_history = models.ForeignKey(
        VisitHistory, on_delete=models.CASCADE, related_name="test_results"
    )
    upload = models.FileField(
        upload_to=medical_upload_file_name, max_length=500
    )
