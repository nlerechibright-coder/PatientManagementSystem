from django.urls import path
from . import views

app_name = 'appointments'

urlpatterns = [
    path('create/', views.create_appointment, name='create_appointment'),
    path('create/<int:patient_pk>/', views.create_appointment, name='create_appointment_for_patient'),
    path('<int:pk>/', views.appointment_detail, name='appointment_detail'),
    path('<int:pk>/accept/', views.accept_appointment, name='accept_appointment'),
    path('<int:pk>/reject/', views.reject_appointment, name='reject_appointment'),
    path('<int:pk>/start-consultation/', views.start_consultation, name='start_consultation'),
    path('<int:pk>/check-in/', views.check_in, name='check_in'),
    path('visit/<int:pk>/', views.visit_detail, name='visit_detail'),
    path('visit/<int:visit_pk>/print/', views.print_prescription, name='print_prescription'),
]