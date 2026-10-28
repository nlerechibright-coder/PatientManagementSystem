from django.contrib import admin
from .models import PatientProfile

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'patient_id', 'phone_number', 'gender')
    search_fields = ('first_name', 'last_name', 'patient_id', 'phone_number')
    list_filter = ('gender', 'blood_group')
    readonly_fields = ('patient_id', 'created_at')
    
    fieldsets = (
        ('Identification', {
            'fields': ('patient_id', 'first_name', 'last_name')
        }),
        ('Demographics', {
            'fields': ('date_of_birth', 'gender', 'blood_group')
        }),
        ('Contact Information', {
            'fields': ('phone_number', 'address')
        }),
        ('System', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        })
    )