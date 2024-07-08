from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.password_validation import (
    validate_password as django_validate_password,
)
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

from users.models import (
    User,
    Patient,
    MedicalProfessional,
    MedicalHistory,
)
from users.utils import check_verification_pin

import logging

logger = logging.getLogger(__name__)


user_fields = [
    "id",
    "first_name",
    "last_name",
    "avatar",
    "gender",
    "date_of_birth",
    "phone_number",
    "address_1",
    "address_2",
    "state",
    "country",
    "email",
    "is_email_verified",
    "is_phone_number_verified",
    "is_medical_professional",
    "is_staff",
]


class UserBaseSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        write_only=True, required=True, allow_blank=False, allow_null=False
    )
    is_medical_professional = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    full_address = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = user_fields + [
            "date_joined",
            "full_address",
            "full_name",
            "password",
            "confirm_password",
        ]
        read_only_fields = (
            "id",
            "full_name",
            "is_email_verified",
            "is_phone_number_verified",
            "is_medical_professional",
            "is_staff",
        )
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "first_name": {"required": True},
            "last_name": {"required": True},
        }

    def get_full_name(self, obj: User):
        return obj.full_name

    def get_full_address(self, obj: User):
        return ", ".join(
            [
                obj.address_1 or "",
                obj.address_2 or "",
                obj.state or "",
                obj.country or "",
            ]
        )

    def get_is_medical_professional(self, obj: User):
        try:
            return obj.is_staff or bool(obj.medicalprofessional)
        except BaseException:
            return False

    def validate_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate_email(self, value):
        user_qs = User.objects.filter(email__iexact=value)
        if user_qs.exists():
            raise serializers.ValidationError(
                "User with this email address already exists."
            )
        else:
            return value

    def validate(self, data):
        password = data.get("password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": _("Passwords do not match.")}
            )
        data.pop("confirm_password")
        return data

    def create(self, validated_data):
        with transaction.atomic():
            # first_name = validated_data["first_name"]
            # last_name = validated_data["last_name"]
            # validated_data["avatar"] = generate_avatar(
            #     first_name[0] + last_name[0], 300
            # )
            user = User.objects.create_user(**validated_data)
            Patient.objects.get_or_create(user=user)

            Token.objects.get_or_create(user=user)
            user.send_verification_email()
            return user


class UserAccountUpdateSerializer(serializers.ModelSerializer):
    is_medical_professional = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = user_fields
        read_only_fields = (
            "id",
            "is_email_verified",
            "is_phone_number_verified",
            "is_medical_professional",
            "is_staff",
        )
        extra_kwargs = {
            "email": {"required": False},
            "avatar": {"read_only": True},
        }

    def get_is_medical_professional(self, obj: User):
        try:
            return obj.is_staff or bool(obj.medicalprofessional)
        except BaseException:
            return False


class UserAvatarUpdateSerializer(UserAccountUpdateSerializer):

    class Meta(UserAccountUpdateSerializer.Meta):
        extra_kwargs = {
            "email": {"required": False},
        }


class UserAccountVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    verification_code = serializers.IntegerField(
        max_value=999999, min_value=100000, required=True
    )

    def validate(self, attrs):
        verification_code = attrs["verification_code"]
        email = attrs["email"]
        if not check_verification_pin(email, verification_code):
            raise serializers.ValidationError(
                {"verification_code": _("Invalid verification code.")}
            )
        return attrs

    def validate_email(self, email):
        user = User.objects.get_user_by_email(email)
        if not user:
            raise serializers.ValidationError(
                ("User account: {}, not found.".format(email))
            )
        if user.is_email_verified:
            raise serializers.ValidationError(
                "User account: {}, is already verified.".format(user.email)
            )
        return user

    def create(self, validated_data):
        verified = validated_data["email"].verify_account(
            validated_data["verification_code"]
        )
        if not verified:
            raise serializers.ValidationError(
                {
                    "detail": _(
                        "Verification code expired. Resend verification email \
                            to get new verification code."
                    )
                }
            )
        return verified


class RegenerateVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        user = User.objects.get_user_by_email(email)
        if not user:
            raise serializers.ValidationError(
                ("User account: {}, not found.".format(email))
            )
        if user.is_email_verified:
            raise serializers.ValidationError(
                "User account: {}, is already verified.".format(user.email)
            )
        return user

    def create(self, validated_data):
        validated_data["email"].send_verification_email()
        return {
            "detail": _(
                "Verification code has been successfully sent to email "
                "{}.".format(validated_data["email"].email)
            )
        }


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        if not User.objects.user_exists_by_email(value):
            raise serializers.ValidationError(
                _("Account with provided email address does not exist.")
            )
        return value

    def create(self, validated_data):
        email_addr = validated_data["email"]
        user = User.objects.get_user_by_email(validated_data["email"])
        user.send_reset_token_email()
        return email_addr


class ResetUserAccountPasswordSerializer(serializers.Serializer):
    reset_token = serializers.IntegerField(
        write_only=True, required=True, max_value=999999, min_value=100000
    )
    new_password = serializers.CharField(write_only=True, required=True)

    def validate_reset_token(self, value):
        if value in cache:
            return value
        raise serializers.ValidationError(_("Token is expired or invalid."))

    def validate_new_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def update(self, instance, validated_data):
        token = validated_data["reset_token"]
        email = cache.get(token)

        instance = User.objects.get_user_by_email(email)
        instance.set_password(validated_data["new_password"])
        instance.save()

        cache.delete(token)
        return instance


class ChangeUserAccountPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True)
    confirm_password = serializers.CharField(
        write_only=True, required=True, allow_blank=False, allow_null=False
    )

    def validate(self, data):
        password = data.get("new_password")
        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": _("Passwords do not match.")}
            )
        data.pop("confirm_password")
        return data

    def validate_old_password(self, password):
        username = self.context["request"].user.username
        if username and password:
            user = authenticate(
                request=self.context.get("request"),
                username=username,
                password=password,
            )

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _("Invalid old password.")
                raise serializers.ValidationError(msg)
            return password
        raise serializers.ValidationError(_("Invalid."))

    def validate_new_password(self, value):
        try:
            django_validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance


class UpdateUserAccountEmailSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        user_qs = User.objects.filter(email__iexact=email)
        if user_qs.exists():
            raise serializers.ValidationError(
                "User with this email address already exists."
            )
        else:
            return email

    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        instance.username = validated_data["email"]
        instance.is_email_verified = False
        instance.send_verification_email()
        instance.save()
        return instance


class UpdateUserAccountNameSerializer(serializers.Serializer):
    first_name = serializers.CharField(
        allow_blank=True, max_length=254, required=False
    )
    last_name = serializers.CharField(
        allow_blank=True, max_length=254, required=False
    )

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get(
            "first_name", instance.first_name
        )
        instance.last_name = validated_data.get(
            "last_name", instance.last_name
        )
        instance.save()
        return instance


class AccountDeletionSerializer(serializers.Serializer):
    hard = serializers.BooleanField(
        write_only=True, required=False, default=False
    )

    def create(self, validated_data):
        hard_delete = validated_data["hard"]
        user = self.context["request"].user

        if hard_delete:
            user.delete()
        else:
            user.is_active = False
            user.save()
        return True


class MedicalHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = MedicalHistory
        fields = (
            "id",
            "patient",
            "medical_conditions",
            "allergies",
            "medications",
            "immunization_history",
            "family_medical_history",
            "created_at",
        )
        read_only_fields = (
            "id",
            "patient",
            "created_at",
        )


class PatientSerializer(serializers.ModelSerializer):
    user = UserBaseSerializer(read_only=True)
    medical_history = MedicalHistorySerializer(read_only=True, many=True)

    class Meta:
        model = Patient
        fields = (
            "id",
            "user",
            "allergies",
            "blood_group",
            "genotype",
            "smoking_status",
            "alcohol_consumption",
            "height",
            "weight",
            "bmi",
            "emergency_contact",
            "preferred_pharmacy",
            "preferred_language",
            "medical_history",
        )
        read_only_fields = (
            "id",
            "user",
            "bmi",
            "medical_history",
        )

    def _calc_bmi(self, validated_data):
        if type(validated_data["weight"]) in (float, int) and type(
            validated_data["height"]
        ) in (float, int):
            validated_data["bmi"] = round(
                (
                    (validated_data["weight"] / validated_data["height"])
                    / validated_data["height"]
                )
                * 10000,
                2,
            )
        return validated_data

    def create(self, validated_data):
        if hasattr(validated_data, "height") and hasattr(
            validated_data, "weight"
        ):
            self._calc_bmi(validated_data)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if "height" in validated_data and "weight" in validated_data:
            self._calc_bmi(validated_data)
        return super().update(instance, validated_data)


class MedicalProfessionalSerializer(serializers.ModelSerializer):
    user = UserBaseSerializer(read_only=True)

    class Meta:
        model = MedicalProfessional
        fields = (
            "id",
            "user",
            "medical_license_number",
            "specialization",
            "education_and_qualifications",
            "work_history",
            "certifications",
            "department",
        )
        read_only_fields = (
            "id",
            "user",
        )
