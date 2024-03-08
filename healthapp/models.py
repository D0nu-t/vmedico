from django.db import models
from django.contrib.auth.models import User

class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_doctor = models.BooleanField(default=True)

    def __str__(self):
        return self.user.username
    

class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Appointment(models.Model):
    doctor = models.ForeignKey(User, related_name='doctor_appointments', on_delete=models.CASCADE)
    patient = models.ForeignKey(User, related_name='patient_appointments', on_delete=models.CASCADE)
    date_time = models.DateTimeField()
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Appointment with {self.patient.username} on {self.date_time.strftime('%Y-%m-%d %H:%M')}"

class Prescription(models.Model):
    doctor = models.ForeignKey(User, related_name='prescriptions_given', on_delete=models.CASCADE)
    patient = models.ForeignKey(User, related_name='prescriptions_received', on_delete=models.CASCADE)
    medication = models.CharField(max_length=255)
    dosage = models.CharField(max_length=255)
    instructions = models.TextField()
    date_issued = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Prescription for {self.patient.username} - {self.medication}"
    
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    is_doctor = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class HealthRecord(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='health_records')
    date_recorded = models.DateField(auto_now_add=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    blood_pressure_systolic = models.IntegerField(null=True, blank=True)
    blood_pressure_diastolic = models.IntegerField(null=True, blank=True)
    glucose_levels = models.IntegerField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s health record for {self.date_recorded}"
    
class LabResult(models.Model):
    # patient = models.ForeignKey(User, related_name='lab_results', on_delete=models.CASCADE)
    # doctor = models.ForeignKey(User, related_name='uploaded_lab_results', on_delete=models.CASCADE)
    doctor = models.ForeignKey(Doctor, null=True, on_delete=models.CASCADE)
    patient = models.ForeignKey(Patient, null=True, on_delete=models.CASCADE)
    lab_name = models.CharField(max_length=255)
    test_name = models.CharField(max_length=255)
    result_value = models.CharField(max_length=255)
    unit = models.CharField(max_length=50)
    reference_range = models.CharField(max_length=100)
    date_of_test = models.DateTimeField()
    # uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.test_name} for {self.patient.username} by {self.doctor.username}"