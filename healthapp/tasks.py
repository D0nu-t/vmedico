from celery import shared_task
from django.core.mail import EmailMessage
from .models import Appointment

@shared_task
def send_appointment_reminder(appointment_id):
    appointment = Appointment.objects.get(id=appointment_id)

    subject = "Appointment Reminder"
    message = f"Dear {appointment.patient.user.username}, you have an upcoming appointment on {appointment.date_time.strftime('%Y-%m-%d %H:%M')}."
    email_from = "addala.ks@example.com"
    recipient_list = [appointment.patient.user.email]

    email = EmailMessage(subject, message, email_from, recipient_list)
    email.send()
