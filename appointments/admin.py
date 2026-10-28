from django.contrib import admin
from .models import Appointment, Visit

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'date', 'time', 'status')
    list_filter = ('status', 'date')
    search_fields = ('patient__username', 'doctor__username')

@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'check_in_time', 'status')
    list_filter = ('status',)
    search_fields = ('patient__username', 'doctor__username')