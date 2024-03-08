from django.contrib import admin
from .models import Doctor, Patient, Appointment, Prescription, Profile, HealthRecord, LabResult

admin.site.register(Doctor)
admin.site.register(Patient)
# admin.site.register(Appointment)
admin.site.register(Prescription)
admin.site.register(Profile)
admin.site.register(HealthRecord)
admin.site.register(LabResult)

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('doctor', 'patient', 'date_time', 'notes')
    list_filter = ('doctor', 'patient', 'date_time')
    search_fields = ('doctor__username', 'patient__username', 'notes')

admin.site.register(Appointment, AppointmentAdmin)

admin.site.site_header = "Vmedico Admin"
admin.site.site_title = "Vmedico Admin"
admin.site.index_title = "Admin"