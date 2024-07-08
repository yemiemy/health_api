from django.contrib import admin
from appointments.models import Appointment, VisitHistory


# Register your models here.
class AppointmentAdmin(admin.ModelAdmin):
    list_display = (
        "patient_name",
        "doctor_name",
        "status",
        "start_time",
        "end_time",
    )

    search_fields = (
        "patient__user__email",
        "medical_professional__user__email",
        "patient__user__first_name",
        "patient__user__last_name",
        "medical_professional__user__first_name",
        "medical_professional__user__last_name",
        "note",
    )

    list_filter = ("status",)

    def patient_name(self, obj: Appointment):
        return obj.patient.user.full_name

    def doctor_name(self, obj: Appointment):
        return obj.medical_professional.user.full_name

    class Meta:
        model = Appointment


admin.site.register(Appointment, AppointmentAdmin)
admin.site.register(VisitHistory)
