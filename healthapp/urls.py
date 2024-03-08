from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import health_stats_view

urlpatterns = [
    # Your app's URLs
    path('', views.home, name='home'),
    path('register_doctor/', views.register_doctor, name='register_doctor'),
    path('register_patient/', views.register_patient, name='register_patient'),
    path('doctor_login/', views.doctor_login, name='doctor_login'),
    path('patient_login/', views.patient_login, name='patient_login'),
    path('add_appointment/', views.add_appointment, name='add_appointment'),
    path('add_prescription/', views.add_prescription, name='add_prescription'),
    path('logout/', LogoutView.as_view(next_page='home'), name='logout'),  # Redirects to home page after logout
    path('patient_dashboard/', views.patient_dashboard, name='patient_dashboard'),
    path('doctor_dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('health_records_list/', views.health_records_list, name='health_records_list'),
    path('health-stats/', health_stats_view, name='health_stats'),
    path('lab_results/', views.lab_results, name='lab_results'),
    path('add-lab-result/', views.add_lab_result, name='add_lab_result'),
    path('send-appointment-reminder/<int:appointment_id>/', views.send_appointment_reminder, name='send_appointment_reminder'),
    path('add_health_record/', views.add_health_record, name='add_health_record')

]
