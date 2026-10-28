from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Appointment, Visit
from .forms import AppointmentForm
from patients.models import PatientProfile

@login_required
def create_appointment(request, patient_pk=None):
    if request.user.role not in ['ADMIN', 'RECEPTIONIST']:
        messages.error(request, "Access denied. Only authorized staff can schedule appointments.")
        return redirect('users:dashboard')

    initial_data = {}
    if patient_pk:
        patient = get_object_or_404(PatientProfile, pk=patient_pk)
        initial_data['patient'] = patient

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save()
            messages.success(request, f"Appointment scheduled for {appt.patient.full_name} with Dr. {appt.doctor.username}.")
            return redirect('appointments:appointment_detail', pk=appt.pk)
    else:
        form = AppointmentForm(initial=initial_data)

    return render(request, 'appointments/appointment_form.html', {'form': form})

@login_required
def appointment_detail(request, pk):
    appt = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': appt})

@login_required
def accept_appointment(request, pk):
    if request.user.role != 'DOCTOR':
        messages.error(request, "Access denied. Only doctors can accept appointments.")
        return redirect('users:dashboard')

    appt = get_object_or_404(Appointment, pk=pk)

    if appt.doctor != request.user:
        messages.error(request, "Access denied. This appointment is assigned to another doctor.")
        return redirect('users:doctor_dashboard')

    if request.method == 'POST':
        if appt.status == 'PENDING':
            appt.status = 'CONFIRMED'
            appt.save()
            messages.success(request, f"Appointment for {appt.patient.full_name} on {appt.date} at {appt.time} CONFIRMED.")
        else:
            messages.warning(request, "Only pending appointments can be accepted.")
    return redirect('users:doctor_dashboard')

@login_required
def reject_appointment(request, pk):
    if request.user.role != 'DOCTOR':
        messages.error(request, "Access denied. Only doctors can reject appointments.")
        return redirect('users:dashboard')

    appt = get_object_or_404(Appointment, pk=pk)

    if appt.doctor != request.user:
        messages.error(request, "Access denied. This appointment is assigned to another doctor.")
        return redirect('users:doctor_dashboard')

    if request.method == 'POST':
        if appt.status == 'PENDING':
            appt.status = 'CANCELLED'
            appt.save()
            messages.warning(request, f"Appointment for {appt.patient.full_name} on {appt.date} REJECTED/CANCELLED.")
        else:
            messages.warning(request, "Only pending appointments can be rejected.")
    return redirect('users:doctor_dashboard')

@login_required
def check_in(request, pk):
    if request.user.role not in ['ADMIN', 'RECEPTIONIST']:
        messages.error(request, "Access denied.")
        return redirect('users:dashboard')

    appt = get_object_or_404(Appointment, pk=pk)
    if appt.status == 'CANCELLED':
        messages.error(request, "Cannot check in a cancelled appointment.")
        return redirect('appointments:appointment_detail', pk=appt.pk)

    if request.method == 'POST':
        visit = Visit.objects.create(
            patient=appt.patient,
            doctor=appt.doctor,
            appointment=appt,
            status='OPEN'
        )
        appt.status = 'COMPLETED'
        appt.save()
        messages.success(request, f"Patient {appt.patient.full_name} checked in successfully. Visit #{visit.pk} is now OPEN.")
        return redirect('appointments:visit_detail', pk=visit.pk)

    return render(request, 'appointments/check_in.html', {'appointment': appt})

@login_required
def visit_detail(request, pk):
    visit = get_object_or_404(
        Visit.objects.select_related(
            'patient', 'doctor', 'consultation',
            'consultation__entered_by', 'consultation__verified_by'
        ).prefetch_related(
            'consultation__vital_signs',
            'consultation__prescriptions',
            'consultation__prescriptions__items'
        ),
        pk=pk
    )
    return render(request, 'appointments/visit_detail.html', {'visit': visit})

@login_required
def print_prescription(request, visit_pk):
    visit = get_object_or_404(
        Visit.objects.select_related('patient', 'doctor', 'consultation').prefetch_related(
            'consultation__prescriptions', 'consultation__prescriptions__items'
        ),
        pk=visit_pk
    )
    if not hasattr(visit, 'consultation'):
        messages.error(request, "No consultation recorded for this visit.")
        return redirect('appointments:visit_detail', pk=visit.pk)
    return render(request, 'clinical/print_prescription.html', {'visit': visit})