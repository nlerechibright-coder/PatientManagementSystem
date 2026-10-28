from django.urls import path
from . import views

app_name = 'clinical'

urlpatterns = [
    path('visit/<int:visit_pk>/record/', views.record_consultation, name='record_consultation'),
    path('visit/<int:visit_pk>/transcribe/', views.transcribe_consultation, name='transcribe_consultation'),
    path('consultation/<int:consultation_pk>/verify/', views.verify_consultation, name='verify_consultation'),
]