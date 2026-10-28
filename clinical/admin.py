from django.contrib import admin
from .models import Consultation, VitalSigns, Prescription, PrescriptionItem

class PrescriptionItemInline(admin.TabularInline):
    model = PrescriptionItem
    extra = 1

class PrescriptionInline(admin.StackedInline):
    model = Prescription
    extra = 0

class VitalSignsInline(admin.StackedInline):
    model = VitalSigns
    extra = 0

@admin.register(Consultation)
class ConsultationAdmin(admin.ModelAdmin):
    list_display = ('visit', 'verification_status', 'entered_by', 'verified_by', 'created_at')
    list_filter = ('verification_status', 'created_at')
    search_fields = ('visit__patient__first_name', 'visit__patient__last_name', 'diagnosis')
    inlines = [VitalSignsInline, PrescriptionInline]
    readonly_fields = ('entered_by', 'verified_by', 'verified_at', 'created_at', 'updated_at')