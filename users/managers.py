from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from rest_framework import exceptions

# App specific imports


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError("The given email must be set")
        email = self.normalize_email(email)
        extra_fields["username"] = email
        user = self.model(email=email, **extra_fields)
        try:
            validate_password(password, user)
        except ValidationError as e:
            raise exceptions.ValidationError({"password": e.messages})
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(email, password, **extra_fields)

    def _get_active_api_user_queryset(self):
        return self.filter(is_staff=False, is_active=True)

    def get_user(self, user_id):
        """Get active user by ID"""
        qs = self._get_active_api_user_queryset()
        return qs.filter(id=user_id).first()

    def get_user_by_email(self, email: str):
        """Get active user by email"""
        qs = self._get_active_api_user_queryset()
        return qs.filter(email__iexact=email).first()

    def user_exists(self, user_id):
        """Checks if an active user by ID exists"""
        qs = self._get_active_api_user_queryset()
        return qs.filter(id=user_id).exists()

    def user_exists_by_email(self, email):
        """Checks if an active user by email exists"""
        qs = self._get_active_api_user_queryset()
        return qs.filter(email__iexact=email).exists()
