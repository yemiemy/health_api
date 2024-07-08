from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from users.permissions import IsAccountVerified
from rest_framework.views import APIView
from rest_framework.generics import (
    CreateAPIView,
    ListAPIView,
    RetrieveAPIView,
    RetrieveUpdateDestroyAPIView,
)
from appointments.models import Availability, Appointment, VisitHistory
from appointments.serilaizers import (
    AvailabilitySerializer,
    AppointmentSerializer,
    VisitHistorySerializer,
)


class AvailabilityListAPIView(ListAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAccountVerified,
    )
    serializer_class = AvailabilitySerializer

    def get_queryset(self):
        medical_professional_id = self.request.query_params.get(
            "medical_professional_id"
        )
        return Availability.objects.filter(
            medical_professional=(
                medical_professional_id
                if medical_professional_id
                else self.request.user.medicalprofessional
            ),
            is_booked=False,
        )


class BookAppointmentAPIView(CreateAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAccountVerified,
    )
    serializer_class = AppointmentSerializer


class AdminUpdateAppointmentAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(
            medical_professional=self.request.user.medicalprofessional
        )


class AdminListAppointmentAPIView(ListAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(
            medical_professional=self.request.user.medicalprofessional
        )


class PatientAppointmentListAPIView(ListAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAccountVerified,
    )
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user.patient,
        )


class PatientAppointmentUpdateAPIView(RetrieveUpdateDestroyAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAccountVerified,
    )
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        return Appointment.objects.filter(
            patient=self.request.user.patient,
        )


class VisitHistoryListAPIView(ListAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAccountVerified,
    )
    serializer_class = VisitHistorySerializer

    def get_queryset(self):
        patient = self.request.user.patient
        return VisitHistory.objects.filter(patient=patient)


class VisitHistoryRetrieveAPIView(RetrieveAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAccountVerified,
    )
    serializer_class = VisitHistorySerializer

    def get_queryset(self):
        patient = self.request.user.patient
        return VisitHistory.objects.filter(patient=patient)


class AdminVisitHistoryView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )

    def get(self, request):
        doctor = self.request.user.medicalprofessional
        appointment_id = self.request.query_params.get("appointment_id")
        print(appointment_id, "HHHHHHHHHHHH")
        vh = VisitHistory.objects.filter(
            medical_professional=doctor, appointment=appointment_id
        ).first()
        serializer = VisitHistorySerializer(vh)

        return Response(serializer.data)

    def put(self, request):
        doctor = self.request.user.medicalprofessional
        appointment_id = self.request.query_params.get("appointment_id")
        vh = VisitHistory.objects.filter(
            medical_professional=doctor, appointment=appointment_id
        ).first()
        serializer = VisitHistorySerializer(vh, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
