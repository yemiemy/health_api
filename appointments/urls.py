from django.urls import path
from appointments import views


urlpatterns = [
    path("availabilities/", views.AvailabilityListAPIView.as_view()),
    path("book/", views.BookAppointmentAPIView.as_view()),
    path("staff/visit-history/", views.AdminVisitHistoryView.as_view()),
    path("staff/", views.AdminListAppointmentAPIView.as_view()),
    path("staff/<str:pk>/", views.AdminUpdateAppointmentAPIView.as_view()),
    path("visit-history/", views.VisitHistoryListAPIView.as_view()),
    path(
        "visit-history/<str:pk>/", views.VisitHistoryRetrieveAPIView.as_view()
    ),
    path("", views.PatientAppointmentListAPIView.as_view()),
    path("<str:pk>/", views.PatientAppointmentUpdateAPIView.as_view()),
]
