from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from appointments.models import Visit
from .models import Consultation, VitalSigns
from .forms import ConsultationForm, VitalSignsForm

@login_required
def record_consultation(request, visit_pk):
    if request.user.role != 'DOCTOR':
        messages.error(request, "Access denied. Only doctors can record consultations directly.")
        return redirect('users:dashboard')

    visit = get_object_or_404(Visit, pk=visit_pk, doctor=request.user)
    
    if hasattr(visit, 'consultation') and visit.consultation.verification_status == 'VERIFIED':
        messages.error(request, "This visit already has a verified consultation. Use the correction workflow if needed.")
        return redirect('appointments:visit_detail', pk=visit.pk)

    consultation, created = Consultation.objects.get_or_create(visit=visit)
    vital_signs, _ = VitalSigns.objects.get_or_create(consultation=consultation)

    if request.method == 'POST':
        c_form = ConsultationForm(request.POST, instance=consultation)
        v_form = VitalSignsForm(request.POST, instance=vital_signs)
        
        if c_form.is_valid() and v_form.is_valid():
            consultation = c_form.save(commit=False)
            consultation.entered_by = request.user
            consultation.verified_by = request.user
            consultation.verified_at = timezone.now()
            consultation.verification_status = 'VERIFIED'
            consultation.save()
            v_form.save()
            messages.success(request, "Consultation recorded and verified successfully.")
            return redirect('appointments:visit_detail', pk=visit.pk)
    else:
        c_form = ConsultationForm(instance=consultation)
        v_form = VitalSignsForm(instance=vital_signs)

    return render(request, 'clinical/record_consultation.html', {
        'c_form': c_form, 'v_form': v_form, 'visit': visit, 'is_doctor': True
    })

@login_required
def transcribe_consultation(request, visit_pk):
    if request.user.role not in ['ADMIN', 'RECEPTIONIST']:
        messages.error(request, "Access denied. Only authorized staff can transcribe notes.")
        return redirect('users:dashboard')

    visit = get_object_or_404(Visit, pk=visit_pk)
    
    if hasattr(visit, 'consultation') and visit.consultation.verification_status == 'VERIFIED':
        messages.error(request, "This visit already has a verified consultation. Transcription is not allowed.")
        return redirect('appointments:visit_detail', pk=visit.pk)

    consultation, created = Consultation.objects.get_or_create(visit=visit)
    vital_signs, _ = VitalSigns.objects.get_or_create(consultation=consultation)

    if not created and consultation.entered_by and consultation.entered_by != request.user and consultation.verification_status != 'DRAFT':
        messages.error(request, "You cannot modify this clinical record.")
        return redirect('appointments:visit_detail', pk=visit.pk)

    if request.method == 'POST':
        c_form = ConsultationForm(request.POST, instance=consultation)
        v_form = VitalSignsForm(request.POST, instance=vital_signs)
        
        if c_form.is_valid() and v_form.is_valid():
            consultation = c_form.save(commit=False)
            consultation.entered_by = request.user
            consultation.verification_status = 'AWAITING_VERIFICATION'
            consultation.verified_by = None
            consultation.verified_at = None
            consultation.save()
            v_form.save()
            messages.success(request, "Notes transcribed successfully. Awaiting doctor verification.")
            return redirect('appointments:visit_detail', pk=visit.pk)
    else:
        c_form = ConsultationForm(instance=consultation)
        v_form = VitalSignsForm(instance=vital_signs)

    return render(request, 'clinical/transcribe_consultation.html', {
        'c_form': c_form, 'v_form': v_form, 'visit': visit
    })

@login_required
def verify_consultation(request, consultation_pk):
    if request.user.role != 'DOCTOR':
        messages.error(request, "Access denied.")
        return redirect('users:dashboard')

    consultation = get_object_or_404(Consultation, pk=consultation_pk, visit__doctor=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'verify':
            consultation.verified_by = request.user
            consultation.verified_at = timezone.now()
            consultation.verification_status = 'VERIFIED'
            consultation.save()
            messages.success(request, "Consultation verified successfully.")
        elif action == 'request_correction':
            consultation.verification_status = 'CORRECTION_REQUESTED'
            consultation.save()
            messages.warning(request, "Correction requested. The receptionist has been notified.")
        return redirect('appointments:visit_detail', pk=consultation.visit.pk)

    return render(request, 'clinical/verify_consultation.html', {'consultation': consultation})