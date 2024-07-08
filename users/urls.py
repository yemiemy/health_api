from django.urls import path

from users import views

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path(
        "register/",
        views.AccountRegistrationView.as_view(),
        name="create_account",
    ),
    path("login/", views.TokenLoginView.as_view(), name="token_login"),
    path("logout/", views.TokenLogoutView.as_view(), name="token_logout"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path(
        "verify/",
        views.AccountVerificationView.as_view(),
        name="account_verify",
    ),
    path(
        "verification-code/regenerate/",
        views.RegenerateVerificationCode.as_view(),
        name="regenerate_verifiction_code",
    ),
    path(
        "forgot-password/",
        views.ForgotPasswordView.as_view(),
        name="forgot_password",
    ),
    path(
        "reset-password/",
        views.ResetAccountPasswordView.as_view(),
        name="reset_password",
    ),
    path(
        "change-password/",
        views.ChangeAccountPasswordView.as_view(),
        name="change_password",
    ),
    path(
        "update-email/",
        views.UpdateUserAccountEmailView.as_view(),
        name="update_email",
    ),
    path(
        "update-name/",
        views.UpdateUserAccountNameView.as_view(),
        name="update_name",
    ),
    path("delete/", views.AccountDeleteView.as_view(), name="account_delete"),
    path(
        "details/",
        views.AccountRetrieveUpdateAPIView.as_view(),
        name="account_details",
    ),
    path(
        "update-avatar/",
        views.UserAvatarUpdateAPIVIew.as_view(),
        name="update_avatar",
    ),
    path(
        "patient/",
        views.PatientRetrieveUpdateView.as_view(),
        name="patient_info",
    ),
    path("staff/patient/", views.PatientGetView.as_view(), name="get_patient"),
    path(
        "staff/patient/medical-history/", views.MedicalHistoryAPIView.as_view()
    ),
    path("staff/", views.MedicalProfessionalView.as_view(), name="staff_info"),
    path("doctors/", views.MedicalProfessionalListAPIView.as_view()),
]
