from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.utils.translation import gettext_lazy as _

from users.serializers import (
    UserBaseSerializer,
    UserAccountUpdateSerializer,
    UserAvatarUpdateSerializer,
    UserAccountVerificationSerializer,
    RegenerateVerificationCodeSerializer,
    ForgotPasswordSerializer,
    ResetUserAccountPasswordSerializer,
    AccountDeletionSerializer,
    ChangeUserAccountPasswordSerializer,
    UpdateUserAccountEmailSerializer,
    UpdateUserAccountNameSerializer,
    PatientSerializer,
    MedicalProfessionalSerializer,
    MedicalHistorySerializer,
)
from users.models import (
    User,
    Patient,
    MedicalProfessional,
    MedicalHistory,
)
from users.permissions import IsAccountVerified
from appointments.serilaizers import AppointmentSerializer
from appointments.models import Appointment
from appointments.choices import BOOKING_STATUS


class AccountRegistrationView(CreateAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserBaseSerializer
    queryset = User.objects.all()


class AccountVerificationView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = UserAccountVerificationSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Account has been successfully verified.")}
        )


class RegenerateVerificationCode(APIView):
    permission_classes = (AllowAny,)
    serializer_class = RegenerateVerificationCodeSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegenerateVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.save()
        return Response(data)


class AccountRetrieveUpdateAPIView(APIView):
    serializer_class = UserBaseSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def get(self, request, *args, **kwargs):
        serializer = self.get_serializer(instance=request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserAccountUpdateSerializer(
            instance=self.request.user, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class UserAvatarUpdateAPIVIew(APIView):

    def put(self, request):
        serializer = UserAvatarUpdateSerializer(
            instance=self.request.user, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.save()
        return Response(
            {
                "detail": _(
                    f"Your password reset token was sent to email '{email}' "
                    "successfully."
                )
            }
        )


class ResetAccountPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetUserAccountPasswordSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Your password has been reseted successfully.")}
        )


class ChangeAccountPasswordView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsAccountVerified,
    )
    serializer_class = ChangeUserAccountPasswordSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {"detail": _("Your password has been changed successfully.")}
        )


class UpdateUserAccountEmailView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserAccountEmailSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = UserBaseSerializer(obj).data
        return Response(data)


class UpdateUserAccountNameView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateUserAccountNameSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=request.user, data=request.data
        )
        serializer.is_valid(raise_exception=True)
        obj = serializer.save()
        data = UserBaseSerializer(obj).data
        return Response(data)


class AccountDeleteView(APIView):
    serializer_class = AccountDeletionSerializer

    def get_serializer_context(self):
        return {"request": self.request}

    def get_serializer(self, *args, **kwargs):
        kwargs["context"] = self.get_serializer_context()
        return self.serializer_class(*args, **kwargs)

    def delete(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


"""
    Patient Section
"""


class PatientRetrieveUpdateView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PatientSerializer

    def get(self, *args, **kwargs):
        patient_info = Patient.objects.filter(user=self.request.user).first()
        if patient_info:
            serializer = PatientSerializer(instance=patient_info)
            return Response(serializer.data)
        return Response(
            {"detail": "No patient data found for this user."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def put(self, *args, **kwargs):
        patient_info = Patient.objects.filter(user=self.request.user).first()
        serializer = PatientSerializer(
            instance=patient_info, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data)


"""
    Medical Section
"""


class MedicalProfessionalListAPIView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = MedicalProfessionalSerializer
    queryset = MedicalProfessional.objects.all()


class MedicalProfessionalView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
    serializer_class = MedicalProfessionalSerializer

    def get(self, *args, **kwargs):
        obj = MedicalProfessional.objects.filter(
            user=self.request.user
        ).first()
        if obj:
            serializer = MedicalProfessionalSerializer(instance=obj)
            return Response(serializer.data)
        return Response(
            {"detail": "No staff data found for this user."},
            status=status.HTTP_404_NOT_FOUND,
        )

    def put(self, *args, **kwargs):
        obj = MedicalProfessional.objects.filter(
            user=self.request.user
        ).first()
        serializer = MedicalProfessionalSerializer(
            instance=obj, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data)

    def post(self, *args, **kwargs):
        serializer = MedicalProfessionalSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MedicalProfessionalPatientsListAPIView(ListAPIView):
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
    serializer_class = AppointmentSerializer

    def get_queryset(self):
        patients = Appointment.objects.filter(
            medical_professional=self.request.user.medicalprofessional,
            status__in=[
                BOOKING_STATUS.ACCEPTED,
                BOOKING_STATUS.COMPLETED,
                BOOKING_STATUS.PENDING,
                BOOKING_STATUS.CANCELLED,
            ],
        )
        return patients


class PatientGetView(APIView):
    permission_classes = (
        IsAuthenticated,
        IsAdminUser,
    )
    serializer_class = PatientSerializer

    def get(self, request, *args, **kwargs):
        patient_id = self.request.query_params.get("patient_id")
        patient = Patient.objects.filter(id=patient_id).first()
        if not patient:
            return Response(
                {"detail": "No patient found for that id"},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = PatientSerializer(patient)
        return Response(serializer.data)


class MedicalHistoryAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        patient_id = self.request.query_params.get("patient_id")
        patient = Patient.objects.filter(id=patient_id).first()
        serializer = MedicalHistorySerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(patient=patient)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request):
        medical_history_id = self.request.query_params.get(
            "medical_history_id"
        )
        medical_history = MedicalHistory.objects.filter(
            id=medical_history_id
        ).first()

        if not medical_history:
            return Response(
                {
                    "detail": (
                        f"No medical history found for id {medical_history_id}"
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = MedicalHistorySerializer(
            instance=medical_history, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request):
        medical_history_id = self.request.query_params.get(
            "medical_history_id"
        )
        medical_history = MedicalHistory.objects.filter(
            id=medical_history_id
        ).first()

        if not medical_history:
            return Response(
                {
                    "detail": (
                        f"No medical history found for id {medical_history_id}"
                    )
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        medical_history.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
