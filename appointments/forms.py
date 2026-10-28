from django import forms
from django.core.exceptions import ObjectDoesNotExist
from .models import Appointment
from users.models import CustomUser
from patients.models import PatientProfile

class DoctorAvailabilityChoiceField(forms.ModelChoiceField):
    """Shows each doctor's Active/Passive status directly in the dropdown."""
    def label_from_instance(self, obj):
        try:
            spec = obj.doctor_profile.specialization
            status = "On Duty" if obj.doctor_profile.is_available else "OFF DUTY - Passive"
        except ObjectDoesNotExist:
            spec = "General"
            status = "On Duty"
        return f"Dr. {obj.username} ({spec}) [{status}]"

class AppointmentForm(forms.ModelForm):
    doctor = DoctorAvailabilityChoiceField(
        queryset=CustomUser.objects.filter(role='DOCTOR').order_by('username'),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900 bg-white'
        }),
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'reason']
        widgets = {
            'patient': forms.Select(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900 bg-white'
            }),
            'date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'
            }),
            'time': forms.TimeInput(attrs={
                'type': 'time',
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900',
                'placeholder': 'e.g., Routine checkup, Fever, Follow-up'
            }),
        }

    def clean_doctor(self):
        doctor = self.cleaned_data.get('doctor')
        if doctor:
            try:
                if not doctor.doctor_profile.is_available:
                    raise forms.ValidationError(
                        f"Dr. {doctor.username} is currently PASSIVE (Off Duty) and cannot receive new appointments. Please select an Active doctor."
                    )
            except ObjectDoesNotExist:
                raise forms.ValidationError("The selected doctor has no clinical profile.")
        return doctor