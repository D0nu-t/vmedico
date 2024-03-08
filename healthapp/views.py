from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Doctor
from .forms import DoctorSignUpForm
from .forms import AppointmentForm, PrescriptionForm
from .forms import PatientSignUpForm
from .models import Appointment, Prescription
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.http import HttpResponseRedirect
from .models import Patient
from .tasks import send_appointment_reminder
from datetime import timedelta
from django import forms
from .forms import HealthRecordForm
from .models import HealthRecord

def register_doctor(request):
    if request.method == 'POST':
        form = DoctorSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            # Redirect to a new URL:
            return redirect('home')  
    else:
        form = DoctorSignUpForm()
    return render(request, 'healthapp/register_doctor.html', {'form': form})

def register_patient(request):
    if request.method == 'POST':
        form = PatientSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            Patient.objects.create(user=user)
            return redirect('home')  
    else:
        form = PatientSignUpForm()
    return render(request, 'healthapp/register_patient.html', {'form': form})

def home(request):
    return render(request, 'healthapp/home.html')

def patient_dashboard(request):
    if not request.user.is_authenticated or not hasattr(request.user, 'patient'):
        return redirect('patient_login')  # Ensure you have a login view and URL configured

    #appointments = Appointment.objects.filter(patient=request.user.patient)
    appointments = Appointment.objects.filter(patient=request.user)
    prescriptions = Prescription.objects.filter(patient=request.user)
    #prescriptions = Prescription.objects.filter(patient=request.user.patient)

    context = {
        'appointments': appointments,
        'prescriptions': prescriptions,
    }
    return render(request, 'healthapp/patient_dashboard.html', context)

def doctor_dashboard(request):
    # Ensure the user is authenticated and is a doctor
    if not request.user.is_authenticated or not hasattr(request.user, 'doctor'):
        # Redirect to login or another appropriate page
        return redirect('doctor_login')

    # Query for appointments and prescriptions associated with this doctor
    appointments = Appointment.objects.filter(doctor=request.user)
    prescriptions = Prescription.objects.filter(doctor=request.user)

    context = {
        'appointments': appointments,
        'prescriptions': prescriptions,
    }
    return render(request, 'healthapp/doctor_dashboard.html', context)

def doctor_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect to doctor's dashboard or homepage
                return redirect('doctor_dashboard')  # Adjust the redirect as needed
    else:
        form = AuthenticationForm()
    return render(request, 'healthapp/doctor_login.html', {'form': form})

def patient_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and hasattr(user, 'patient'):  # Ensure the user has a patient profile
                login(request, user)
                # Redirect to patient's dashboard or homepage
                return redirect('patient_dashboard')  # Adjust the redirect as needed
            
    else:
        form = AuthenticationForm()
    return render(request, 'healthapp/patient_login.html', {'form': form})




# def add_appointment(request):
#     if request.method == 'POST':
#         form = AppointmentForm(request.POST)
#         if form.is_valid():
#             appointment = form.save()
#             # schedule_appointment_reminder(appointment)
#             return redirect('home') 
#     else:
#         form = AppointmentForm()
    
#     return render(request, 'healthapp/add_appointment.html', {'form': form})

def add_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST, user=request.user)
        if form.is_valid():
            appointment = form.save(commit=False)
            # Check if the user is associated with a doctor profile
            if hasattr(request.user, 'doctor'):
                # Make sure to assign the User instance, not the Doctor instance
                appointment.doctor = request.user
                appointment.save()
                # Redirect to the doctor's dashboard view
                return redirect('doctor_dashboard')  # Adjust with your actual view or URL name
            else:
                # For patients, assign the patient and save the appointment
                appointment.patient = request.user
                appointment.save()
                # Redirect to the patient's dashboard view
                return redirect('patient_dashboard')  # Adjust with your actual view or URL name
    else:
        form = AppointmentForm(user=request.user)
        if hasattr(request.user, 'doctor'):
            # If the user is a doctor, hide the doctor field and set initial value
            form.fields['doctor'].widget = forms.HiddenInput()
            form.initial['doctor'] = request.user
        else:
            # If the user is a patient, hide the patient field and set initial value
            form.fields['patient'].widget = forms.HiddenInput()
            form.initial['patient'] = request.user

    # Render the form with the context
    return render(request, 'healthapp/add_appointment.html', {'form': form})


def add_prescription(request):
    if request.method == 'POST':
        form = PrescriptionForm(request.POST, user=request.user)
    
        if form.is_valid():
            prescription = form.save(commit=False)
            prescription.doctor = request.user   # Set the doctor to the current user
            prescription.save()
            return redirect('doctor_dashboard')  # Redirect to the doctor dashboard
    else:
        form = PrescriptionForm(user=request.user)

    return render(request, 'healthapp/add_prescription.html', {'form': form})


def health_records_list(request):
    records = HealthRecord.objects.filter(user=request.user).order_by('-date_recorded')
    return render(request, 'healthapp/health_records_list.html', {'records': records})

def add_health_record(request):
    if request.method == "POST":
        form = HealthRecordForm(request.POST)
        if form.is_valid():
            health_record = form.save(commit=False)
            health_record.user = request.user
            health_record.save()
            return redirect('health_records_list')
    else:
        form = HealthRecordForm()
    return render(request, 'healthapp/add_health_record.html', {'form': form})

from django.views.generic import TemplateView
from chartjs.views.lines import BaseLineChartView
from .models import HealthRecord
import json

def health_stats_view(request):
    # Assuming each HealthRecord entry has weight, blood_pressure_systolic, blood_pressure_diastolic, and glucose_levels
    records = HealthRecord.objects.filter(user=request.user).order_by('date_recorded')
    dates = [record.date_recorded.strftime("%Y-%m-%d") for record in records]
    weights = [float(record.weight) for record in records]
    blood_pressures = [[float(record.blood_pressure_systolic), float(record.blood_pressure_diastolic)] for record in records]
    glucose_levels = [float(record.glucose_levels) for record in records]

    context = {
        'dates': json.dumps(dates),
        'weights': json.dumps(weights),
        'blood_pressures': json.dumps(blood_pressures),
        'glucose_levels': json.dumps(glucose_levels),
    }
    return render(request, 'healthapp/health_stats.html', context)

from .models import LabResult

def lab_results(request):
    if hasattr(request.user, 'doctor'):  # If the user is associated with a doctor profile
        results = LabResult.objects.filter(doctor=request.user.doctor).order_by('-date_of_test')
    elif hasattr(request.user, 'patient'):  # If the user is associated with a patient profile
        results = LabResult.objects.filter(patient=request.user.patient).order_by('-date_of_test')
    else:
        results = []  # Empty query set if the user is neither a doctor nor a patient
    
    return render(request, 'healthapp/lab_results.html', {'results': results})
from .forms import LabResultForm

def add_lab_result(request):
    if request.method == 'POST':
        form = LabResultForm(request.POST)
        if form.is_valid():
            lab_result = form.save(commit=False)
            
            # Retrieve the Doctor object associated with the logged-in user
            try:
                doctor_user = Doctor.objects.get(user=request.user)
                lab_result.doctor = doctor_user
            except Doctor.DoesNotExist:
                
                return redirect('home')  
            
            lab_result.save()
            return redirect('doctor_dashboard')
    else:
        form = LabResultForm()
    return render(request, 'healthapp/add_lab_result.html', {'form': form})

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_appointment_reminder(request, appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)
    patient = appointment.patient
    doctor = appointment.doctor.username

    subject = 'Appointment Reminder'
    html_message = render_to_string('healthapp/appointment_reminder_email.html', {
        'patient': patient,
        'appointment': appointment,
    })
    plain_message = strip_tags(html_message)
    from_email = 'vmedico.test@gmail.com'
    to_email = patient.email

    send_mail(subject, plain_message, from_email, [to_email], html_message=html_message)

    # You can add a success message or redirect to a success page
    return redirect('doctor_dashboard')