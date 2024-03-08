from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Doctor
from .models import Patient
from .models import Appointment, Prescription
from .models import HealthRecord
from .models import LabResult

class DoctorSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            # Assuming the user is saved and you now want to save the Doctor profile
            doctor = Doctor.objects.create(user=user)
        return user

class PatientSignUpForm(UserCreationForm):
    # Additional fields can be added here

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['doctor', 'patient', 'date_time', 'notes']
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(AppointmentForm, self).__init__(*args, **kwargs)

        # Check if the user is associated with a Doctor instance
        if hasattr(user, 'doctor'):
            doctor_instance = user.doctor
            self.fields['doctor'].queryset = User.objects.filter(doctor__isnull=False)
            self.fields['patient'].queryset = User.objects.exclude(doctor__isnull=False)
            self.fields['doctor'].widget = forms.HiddenInput()
        else:
            self.fields['patient'].queryset = User.objects.filter(doctor__isnull=True)
            self.fields['patient'].initial = user
            self.fields['doctor'].queryset = User.objects.filter(doctor__isnull=False)
            self.fields['patient'].widget = forms.HiddenInput()



class PrescriptionForm(forms.ModelForm):
    class Meta:
        model = Prescription
        exclude = ['date_issued','doctor']  
        fields = ['doctor', 'patient', 'medication', 'dosage', 'instructions', 'date_issued']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PrescriptionForm, self).__init__(*args, **kwargs)
        self.fields['patient'].queryset = User.objects.exclude(doctor__isnull=False)


class HealthRecordForm(forms.ModelForm):
    class Meta:
        model = HealthRecord
        fields = ['weight', 'blood_pressure_systolic', 'blood_pressure_diastolic', 'glucose_levels', 'notes']

class LabResultForm(forms.ModelForm):
    class Meta:
        model = LabResult
        fields = ['patient', 'lab_name', 'test_name', 'result_value', 'unit', 'reference_range', 'date_of_test']
        widgets = {
            'date_of_test': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }