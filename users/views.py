import csv
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm, DoctorCreationForm, ReceptionistCreationForm
from users.models import CustomUser, DoctorProfile
from patients.models import PatientProfile
from appointments.models import Appointment, Visit
from clinical.models import Consultation
from datetime import datetime

def login_view(request):
    if request.user.is_authenticated:
        return redirect('users:dashboard')
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('users:dashboard')
            else:
                messages.error(request, 'Invalid username or password')
        else:
            messages.error(request, 'Invalid username or password')
    form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('users:login')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}')
            return redirect('users:dashboard')
        else:
            messages.error(request, 'Unsuccessful registration. Invalid information.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def dashboard(request):
    if request.user.role == 'ADMIN':
        return redirect('users:admin_dashboard')
    elif request.user.role == 'RECEPTIONIST':
        return redirect('users:receptionist_dashboard')
    elif request.user.role == 'DOCTOR':
        return redirect('users:doctor_dashboard')
    return redirect('users:login')

@login_required
def admin_dashboard(request):
    if request.user.role != 'ADMIN':
        return redirect('users:dashboard')
    
    total_patients = PatientProfile.objects.count()
    total_doctors = DoctorProfile.objects.count()
    total_receptionists = CustomUser.objects.filter(role='RECEPTIONIST').count()
    total_appointments = Appointment.objects.count()
    pending_appointments = Appointment.objects.filter(status='PENDING').count()
    today_visits = Visit.objects.filter(check_in_time__date=datetime.now().date()).count()
    recent_appointments = Appointment.objects.select_related('patient', 'doctor').order_by('-created_at')[:10]
    
    context = {
        'total_patients': total_patients,
        'total_doctors': total_doctors,
        'total_receptionists': total_receptionists,
        'total_appointments': total_appointments,
        'pending_appointments': pending_appointments,
        'today_visits': today_visits,
        'recent_appointments': recent_appointments,
    }
    return render(request, 'users/admin_dashboard.html', context)

@login_required
def create_doctor(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied. Only Administrators can create doctor accounts.")
        return redirect('users:dashboard')
    if request.method == 'POST':
        form = DoctorCreationForm(request.POST)
        if form.is_valid():
            doctor = form.save()
            messages.success(request, f"Dr. {doctor.username} created successfully with specialization: {doctor.doctor_profile.specialization}")
            return redirect('users:admin_dashboard')
    else:
        form = DoctorCreationForm()
    return render(request, 'users/create_doctor.html', {'form': form})

@login_required
def create_receptionist(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied. Only Administrators can create receptionist accounts.")
        return redirect('users:dashboard')
    if request.method == 'POST':
        form = ReceptionistCreationForm(request.POST)
        if form.is_valid():
            receptionist = form.save()
            messages.success(request, f"Receptionist '{receptionist.first_name} {receptionist.last_name}' created successfully.")
            return redirect('users:admin_dashboard')
    else:
        form = ReceptionistCreationForm()
    return render(request, 'users/create_receptionist.html', {'form': form})

@login_required
def receptionist_dashboard(request):
    if request.user.role not in ['ADMIN', 'RECEPTIONIST']:
        return redirect('users:dashboard')
    recent_patients = PatientProfile.objects.order_by('-created_at')[:10]
    return render(request, 'users/receptionist_dashboard.html', {'recent_patients': recent_patients})

@login_required
def doctor_dashboard(request):
    if request.user.role != 'DOCTOR':
        return redirect('users:dashboard')
    
    appointments = Appointment.objects.filter(
        doctor=request.user,
        date__gte=datetime.now().date()
    ).order_by('date', 'time')
    
    visits = Visit.objects.filter(doctor=request.user).order_by('-check_in_time')
    pending_verifications = Consultation.objects.filter(
        visit__doctor=request.user, 
        verification_status='AWAITING_VERIFICATION'
    ).select_related('visit__patient', 'entered_by')
    
    return render(request, 'users/doctor_dashboard.html', {
        'appointments': appointments, 
        'visits': visits,
        'pending_verifications': pending_verifications
    })

@login_required
def toggle_availability(request):
    if request.user.role != 'DOCTOR':
        messages.error(request, "Access denied. Only doctors can change their availability.")
        return redirect('users:dashboard')
    if request.method == 'POST':
        profile = request.user.doctor_profile
        profile.is_available = not profile.is_available
        profile.save()
        if profile.is_available:
            messages.success(request, "You are now ACTIVE (On Duty). Receptionists can schedule new appointments with you.")
        else:
            messages.warning(request, "You are now PASSIVE (Off Duty). Receptionists cannot schedule new appointments with you. Existing appointments are unaffected.")
        return redirect('users:doctor_dashboard')
    messages.error(request, "Invalid request.")
    return redirect('users:doctor_dashboard')

@login_required
def patient_dashboard(request):
    if request.user.role != 'PATIENT':
        return redirect('users:dashboard')
    try:
        patient_profile = request.user.patient_profile
    except PatientProfile.DoesNotExist:
        patient_profile = None
    appointments = Appointment.objects.filter(patient=request.user).order_by('-date', '-time')
    return render(request, 'users/patient_dashboard.html', {'patient_profile': patient_profile, 'appointments': appointments})

@login_required
def export_patients_csv(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('users:dashboard')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="patients_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Patient ID', 'First Name', 'Last Name', 'Gender', 'Blood Group', 'Phone Number', 'Date of Birth'])
    for patient in PatientProfile.objects.all():
        writer.writerow([patient.patient_id, patient.first_name, patient.last_name, patient.get_gender_display(), patient.blood_group, patient.phone_number, patient.date_of_birth])
    return response

@login_required
def export_appointments_csv(request):
    if request.user.role != 'ADMIN':
        messages.error(request, "Access denied.")
        return redirect('users:dashboard')
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="appointments_export.csv"'
    writer = csv.writer(response)
    writer.writerow(['Appointment ID', 'Patient Name', 'Doctor', 'Date', 'Time', 'Status', 'Reason'])
    for appt in Appointment.objects.select_related('patient', 'doctor').all():
        writer.writerow([appt.pk, appt.patient.full_name, appt.doctor.username, appt.date, appt.time, appt.status, appt.reason])
    return response