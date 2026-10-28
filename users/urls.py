from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('create-doctor/', views.create_doctor, name='create_doctor'),
    path('create-receptionist/', views.create_receptionist, name='create_receptionist'),
    path('receptionist-dashboard/', views.receptionist_dashboard, name='receptionist_dashboard'),
    path('doctor-dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient-dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('export/patients/', views.export_patients_csv, name='export_patients_csv'),
    path('export/appointments/', views.export_appointments_csv, name='export_appointments_csv'),
]