from django.db import models
from django.conf import settings
from appointments.models import Visit

class Consultation(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('AWAITING_VERIFICATION', 'Awaiting Verification'),
        ('VERIFIED', 'Verified'),
        ('CORRECTION_REQUESTED', 'Correction Requested'),
    ]
    visit = models.OneToOneField(Visit, on_delete=models.CASCADE, related_name='consultation')
    chief_complaint = models.TextField()
    history_of_present_illness = models.TextField()
    examination_findings = models.TextField()
    diagnosis = models.TextField()
    treatment_plan = models.TextField()
    follow_up_instructions = models.TextField(blank=True)
    
    # Audit and Verification Fields
    entered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='entered_consultations')
    verified_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_consultations')
    verified_at = models.DateTimeField(null=True, blank=True)
    verification_status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='DRAFT')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Consultation for {self.visit.patient.full_name} on {self.created_at.date()}"

class VitalSigns(models.Model):
    consultation = models.OneToOneField(Consultation, on_delete=models.CASCADE, related_name='vital_signs')
    blood_pressure = models.CharField(max_length=20, blank=True)
    temperature = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    pulse = models.IntegerField(null=True, blank=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"Vitals for {self.consultation.visit.patient.full_name}"

class Prescription(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='prescriptions')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.consultation.visit.patient.full_name} on {self.created_at.date()}"

class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=255)
    dosage = models.CharField(max_length=100)
    frequency = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    instructions = models.TextField(blank=True)

    def __str__(self):
        return f"{self.medicine_name} ({self.dosage})"