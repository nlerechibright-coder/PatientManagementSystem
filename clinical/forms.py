from django import forms
from .models import Consultation, VitalSigns

class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['chief_complaint', 'history_of_present_illness', 'examination_findings', 'diagnosis', 'treatment_plan', 'follow_up_instructions']
        widgets = {
            'chief_complaint': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'}),
            'history_of_present_illness': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'}),
            'examination_findings': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'}),
            'treatment_plan': forms.Textarea(attrs={'rows': 4, 'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'}),
            'follow_up_instructions': forms.Textarea(attrs={'rows': 3, 'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900'}),
        }

class VitalSignsForm(forms.ModelForm):
    class Meta:
        model = VitalSigns
        fields = ['blood_pressure', 'temperature', 'pulse', 'weight']
        widgets = {
            'blood_pressure': forms.TextInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900', 'placeholder': 'e.g., 120/80'}),
            'temperature': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900', 'placeholder': 'e.g., 37.5'}),
            'pulse': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900', 'placeholder': 'e.g., 72'}),
            'weight': forms.NumberInput(attrs={'class': 'w-full px-4 py-3 rounded-lg border border-slate-300 focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all text-slate-900', 'placeholder': 'e.g., 70.5'}),
        }