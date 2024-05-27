from django.contrib import admin
from users.models import User, Patient, MedicalProfessional


class UserAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "first_name",
        "last_name",
        "gender",
        "is_email_verified",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "gender",
    )

    list_filter = (
        "gender",
        "is_email_verified",
    )

    class Meta:
        model = User


class PatientAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "blood_group",
        "genotype",
        "height",
        "weight",
        "bmi",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "blood_group",
        "genotype",
    )

    def email(self, obj: Patient):
        return obj.user.email

    class Meta:
        model = Patient


class MedicalProfessionalAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "medical_license_number",
        "specialization",
        "department",
    )

    search_fields = (
        "user__email",
        "user__first_name",
        "user__last_name",
    )

    list_filter = (
        "specialization",
        "department",
    )

    def email(self, obj: MedicalProfessional):
        return obj.user.email

    class Meta:
        model = MedicalProfessional


admin.site.register(User, UserAdmin)
admin.site.register(Patient, PatientAdmin)
admin.site.register(MedicalProfessional, MedicalProfessionalAdmin)
