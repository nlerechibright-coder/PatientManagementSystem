from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from users.models import CustomUser, DoctorProfile
from patients.models import PatientProfile
from appointments.models import Appointment, Visit
from django.db.models import Count, Q
from datetime import datetime, timedelta

@login_required
def dashboard(request):
    if request.user.role == 'ADMIN':
        return redirect('core:admin_dashboard')
    elif request.user.role == 'DOCTOR':
        return redirect('core:doctor_dashboard')
    elif request.user.role == 'PATIENT':
        return redirect('core:patient_dashboard')
    return redirect('users:login')

@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('core:dashboard')
    
    # Statistics
    total_patients = PatientProfile.objects.count()
    total_doctors = DoctorProfile.objects.count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='PENDING').count()
    today_visits = Visit.objects.filter(
        check_in_time__date=datetime.now().date()
    ).count()
    
    # Recent appointments
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:10]
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'today_visits': today_visits,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'core/admin_dashboard.html', context)

@login_required
def doctor_dashboard(request):
    if request.user.role != 'DOCTOR':
        return redirect('core:dashboard')
    
    # Get doctor's appointments and visits
    appointments = Appointment.objects.filter(doctor=request.user).order_by('-date', '-time')
    visits = Visit.objects.filter(doctor=request.user).order_by('-check_in_time')
    
    context = {
        'appointments': appointments,
        'visits': visits,
    }
    return render(request, 'core/doctor_dashboard.html', context)

@login_required
def patient_dashboard(request):
    if request.user.role != 'PATIENT':
        return redirect('core:dashboard')
    
    # Get patient's data
    try:
        patient_profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        patient_profile = None
    
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time')
    
    context = {
        'patient_profile': patient_profile,
        'appointments': appointments,
    }
    return render(request, 'core/patient_dashboard.html', context)