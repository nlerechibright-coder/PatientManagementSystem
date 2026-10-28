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
def start_consultation(request, pk):
    """Doctor attends a scheduled patient immediately, before the scheduled time."""
    if request.user.role != 'DOCTOR':
        messages.error(request, "Access denied. Only doctors can start consultations.")
        return redirect('users:dashboard')

    appt = get_object_or_404(Appointment, pk=pk)

    if appt.doctor != request.user:
        messages.error(request, "Access denied. This appointment is assigned to another doctor.")
        return redirect('users:doctor_dashboard')

    if appt.status not in ['PENDING', 'CONFIRMED']:
        messages.warning(request, "This appointment cannot be attended (it is already completed or cancelled).")
        return redirect('users:doctor_dashboard')

    existing_visit = Visit.objects.filter(appointment=appt).first()
    if existing_visit:
        return redirect('clinical:record_consultation', visit_pk=existing_visit.pk)

    visit = Visit.objects.create(
        patient=appt.patient,
        doctor=appt.doctor,
        appointment=appt,
        status='OPEN'
    )
    appt.status = 'COMPLETED'
    appt.save()
    messages.success(request, f"Visit opened for {appt.patient.full_name}. Record the consultation now.")
    return redirect('clinical:record_consultation', visit_pk=visit.pk)

@login_required
def open_emergency_visit(request, patient_pk):
    """
    Doctor-initiated emergency walk-in visit for a patient with NO appointment.
    Creates an OPEN visit (appointment = None) and jumps straight to the consultation form.
    """
    if request.user.role != 'DOCTOR':
        messages.error(request, "Access denied. Only doctors can open emergency visits.")
        return redirect('users:dashboard')

    patient = get_object_or_404(PatientProfile, pk=patient_pk)

    if request.method == 'POST':
        existing_open = Visit.objects.filter(patient=patient, status='OPEN').select_related('doctor').first()
        if existing_open:
            if existing_open.doctor == request.user:
                messages.info(request, f"{patient.full_name} already has an open visit under your care. Continuing to it.")
                return redirect('clinical:record_consultation', visit_pk=existing_open.pk)
            messages.warning(request, f"{patient.full_name} already has an open visit under Dr. {existing_open.doctor.username}.")
            return redirect('appointments:visit_detail', pk=existing_open.pk)

        visit = Visit.objects.create(
            patient=patient,
            doctor=request.user,
            appointment=None,
            status='OPEN'
        )
        messages.success(request, f"EMERGENCY visit opened for {patient.full_name}. Record the consultation now.")
        return redirect('clinical:record_consultation', visit_pk=visit.pk)

    messages.error(request, "Invalid request.")
    return redirect('patients:patient_detail', pk=patient.pk)

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
        existing_visit = Visit.objects.filter(appointment=appt).first()
        if existing_visit:
            messages.warning(request, "This appointment already has an open visit.")
            return redirect('appointments:visit_detail', pk=existing_visit.pk)

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