from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrator'),
        ('RECEPTIONIST', 'Receptionist'),
        ('DOCTOR', 'Doctor'),
    )
    role = models.CharField(max_length=15, choices=ROLE_CHOICES, default='RECEPTIONIST')

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

class DoctorProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='doctor_profile', limit_choices_to={'role': 'DOCTOR'})
    specialization = models.CharField(max_length=100)
    license_number = models.CharField(max_length=50, unique=True)
    bio = models.TextField(blank=True)
    is_available = models.BooleanField(default=True, verbose_name="Active (On Duty)")

    def __str__(self):
        status = "On Duty" if self.is_available else "Off Duty"
        return f"Dr. {self.user.username} - {self.specialization} [{status}]"