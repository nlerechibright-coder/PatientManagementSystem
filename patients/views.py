from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import PatientProfile
from .forms import PatientProfileForm

@login_required
def register_patient(request):
    if request.user.role not in ['ADMIN', 'RECEPTIONIST']:
        messages.error(request, "Access denied. Only authorized staff can register patients.")
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = PatientProfileForm(request.POST)
        if form.is_valid():
            # Duplicate check: Same first name, last name, and phone number
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone = form.cleaned_data['phone_number']
            
            existing_patient = PatientProfile.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name,
                phone_number=phone
            ).first()

            if existing_patient:
                messages.warning(request, f"A patient with this name and phone number already exists (ID: {existing_patient.patient_id}). Please search for them instead.")
                return redirect('patients:patient_detail', pk=existing_patient.pk)
            
            patient = form.save()
            messages.success(request, f"Patient '{patient.first_name} {patient.last_name}' registered successfully with ID: {patient.patient_id}")
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            # This will print the exact reason the form failed to your terminal
            print("REGISTRATION FORM ERRORS:", form.errors)
            messages.error(request, "Please correct the errors highlighted in the form.")
    else:
        form = PatientProfileForm()

    return render(request, 'patients/register_patient.html', {'form': form})

@login_required
def patient_list(request):
    if request.user.role not in ['ADMIN', 'RECEPTIONIST', 'DOCTOR']:
        messages.error(request, "Access denied.")
        return redirect('users:dashboard')

    query = request.GET.get('q', '')
    patients = PatientProfile.objects.all().order_by('-created_at')
    
    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(patient_id__icontains=query) |
            Q(phone_number__icontains=query)
        )

    return render(request, 'patients/patient_list.html', {'patients': patients, 'query': query})

@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(PatientProfile, pk=pk)
    return render(request, 'patients/patient_detail.html', {'patient': patient})