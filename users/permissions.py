from rest_framework.permissions import BasePermission


class IsAccountVerified(BasePermission):
    message = "You need to verify your account to access this page."

    def has_permission(self, request, view):
        return request.user.is_email_verified
