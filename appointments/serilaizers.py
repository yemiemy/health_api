from django.db import transaction
from rest_framework import serializers
from appointments.models import (
    Availability,
    Appointment,
    VisitHistory,
    TestResult,
)
from datetime import timedelta
from appointments.choices import BOOKING_STATUS
from users.serializers import PatientSerializer, MedicalProfessionalSerializer
from users.models import MedicalProfessional
from users.tasks import (
    send_appointment_booking_mail,
    send_appointment_update_mail,
)


class AvailabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Availability
        fields = (
            "id",
            "medical_professional",
            "start_time",
            "end_time",
            "is_booked",
        )
        read_only_fields = (
            "id",
            "medical_professional",
            "is_booked",
        )


class AppointmentSerializer(serializers.ModelSerializer):
    patient = PatientSerializer(read_only=True)
    medical_professional = MedicalProfessionalSerializer(read_only=True)
    medical_professional_id = serializers.UUIDField(
        required=True, write_only=True
    )
    is_status_update = serializers.BooleanField(
        default=False, required=False, write_only=True
    )

    class Meta:
        model = Appointment
        fields = (
            "id",
            "patient",
            "medical_professional",
            "medical_professional_id",
            "is_status_update",
            "note",
            "status",
            "start_time",
            "end_time",
            "created_at",
        )
        read_only_fields = (
            "id",
            "patient",
            "medical_professional",
            "created_at",
        )
        extra_kwargs = {
            "medical_professional_id": {"write_only": True},
            "is_status_update": {"write_only": True},
        }

    def validate(self, attrs):
        medical_professional_id = attrs["medical_professional_id"]
        medical_professional = MedicalProfessional.objects.filter(
            id=medical_professional_id
        ).first()
        if not medical_professional:
            raise serializers.ValidationError(
                {"detail": "No medical professional found for that id."}
            )
        start_time = attrs["start_time"]
        end_time = attrs["end_time"]

        is_status_update = bool(attrs.get("is_status_update"))
        if not is_status_update:
            if start_time > end_time:
                raise serializers.ValidationError(
                    "start datetime must always be less than end datetime."
                )

            availability_qs = Availability.objects.filter(
                medical_professional=medical_professional,
                start_time__lte=start_time,
                end_time__gte=end_time,
                is_booked=False,
            )
            if not availability_qs.exists():
                raise serializers.ValidationError(
                    "No suitable availability found for the appointment duration."
                )

            attrs["availability"] = availability_qs.first()
        attrs["medical_professional_id"] = medical_professional
        return super().validate(attrs)

    def create(self, validated_data):
        user = self.context["request"].user
        medical_professional = validated_data["medical_professional_id"]
        appointment_start_time = validated_data["start_time"]
        appointment_end_time = validated_data["end_time"]
        availability: Availability = validated_data["availability"]

        with transaction.atomic():
            # Calculate the difference in days between the appointment and
            # the availability
            appointment_duration = (
                appointment_end_time - appointment_start_time
            ).days
            availability_duration = (
                availability.end_time - availability.start_time
            ).days

            # If the appointment covers the entire availability period,
            # mark it as booked
            if appointment_duration == availability_duration:
                availability.is_booked = True
                availability.save()
            else:
                # check if there are free days prior to user appointment
                # start date
                if (appointment_start_time - availability.start_time).days > 0:
                    prev_day = appointment_start_time - timedelta(days=1)
                    Availability.objects.create(
                        medical_professional=medical_professional,
                        start_time=availability.start_time,
                        end_time=prev_day.replace(
                            hour=22, minute=59, second=0, microsecond=0
                        ),
                    )

                # Create a new availability for the remaining days after
                if (
                    appointment_end_time + timedelta(days=1)
                    <= availability.end_time
                ):
                    next_day = appointment_end_time + timedelta(days=1)
                    Availability.objects.create(
                        medical_professional=medical_professional,
                        start_time=next_day.replace(
                            hour=0, minute=0, second=0, microsecond=0
                        ),
                        end_time=availability.end_time,
                    )
                availability.start_time = appointment_start_time
                availability.end_time = appointment_end_time
                availability.is_booked = True
                availability.save()

            # create appointment
            appointment = Appointment.objects.create(
                patient=user.patient,
                medical_professional=medical_professional,
                status=BOOKING_STATUS.PENDING,
                start_time=appointment_start_time,
                end_time=appointment_end_time,
                note=validated_data.get("note"),
            )
            # email to patient.
            send_appointment_booking_mail.delay(
                user.full_name,
                medical_professional.user.full_name,
                user.email,
                appointment.start_time.date(),
                (appointment.start_time + timedelta(hours=1)).time(),
            )

            # mail to doctor
            send_appointment_booking_mail.delay(
                medical_professional.user.full_name,
                user.full_name,
                user.email,
                appointment.start_time.date(),
                (appointment.start_time + timedelta(hours=1)).time(),
            )
            return appointment

    def update(self, instance: Appointment, validated_data):
        instance.status = validated_data.get("status", instance.status)
        if (
            validated_data.get("medical_professional_id").id
            != instance.medical_professional.id
        ):
            instance.status = BOOKING_STATUS.PENDING
        instance.medical_professional = validated_data.get(
            "medical_professional_id", instance.medical_professional
        )
        instance.start_time = validated_data.get(
            "start_time", instance.start_time
        )
        instance.end_time = validated_data.get("end_time", instance.end_time)
        instance.note = validated_data.get("note", instance.note)
        instance.save()

        vh, _ = VisitHistory.objects.get_or_create(
            appointment=instance,
            medical_professional=instance.medical_professional,
            patient=instance.patient,
        )
        vh.visit_date = instance.start_time
        vh.save()

        # email to patient.
        send_appointment_update_mail.delay(
            instance.patient.user.full_name,
            instance.medical_professional.user.full_name,
            instance.patient.user.email,
            instance.start_time.date(),
            (instance.start_time + timedelta(hours=1)).time(),
            instance.status,
        )

        return instance


class TestResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestResult
        fields = (
            "id",
            "patient",
            "visit_history",
            "blood_tests",
            "imaging_studies",
            "electrocardiogram",
            "other_tests",
        )


class VisitHistorySerializer(serializers.ModelSerializer):
    test_results = TestResultSerializer(many=True, read_only=True)
    # patient_id = serializers.UUIDField(write_only=True)
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = VisitHistory
        fields = (
            "id",
            "appointment",
            # "patient_id",
            "patient",
            "medical_professional",
            "visit_date",
            "reason_for_visit",
            "treatments_received",
            "physician_notes",
            "test_results",
        )
