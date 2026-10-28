from django.db import models
from users.models import CustomUser
from patients.models import PatientProfile

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    )
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_appointments', limit_choices_to={'role': 'DOCTOR'})
    date = models.DateField()
    time = models.TimeField()
    reason = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'time']

    def __str__(self):
        return f"Appt: {self.patient.first_name} {self.patient.last_name} with Dr. {self.doctor.username} on {self.date}"

class Visit(models.Model):
    STATUS_CHOICES = (
        ('OPEN', 'Open'),
        ('COMPLETED', 'Completed'),
    )
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='visits')
    doctor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='doctor_visits', limit_choices_to={'role': 'DOCTOR'})
    appointment = models.OneToOneField(Appointment, on_delete=models.SET_NULL, null=True, blank=True, related_name='visit')
    check_in_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='OPEN')

    def __str__(self):
        return f"Visit: {self.patient.first_name} {self.patient.last_name} with Dr. {self.doctor.username} ({self.status})"