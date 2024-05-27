from django.urls import path, include, reverse_lazy
from django.views.generic.base import RedirectView
from django.contrib import admin

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("admin:index"))),
    path("admin/", admin.site.urls),
    path("api/v1/accounts/", include("users.urls")),
]
