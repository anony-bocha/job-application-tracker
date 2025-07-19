from django.core.mail import send_mail
from django.conf import settings

def send_application_notification(client_email, job_title, freelancer_name):
    subject = f"New Application for {job_title}"
    message = f"{freelancer_name} has applied for your job posting: {job_title}."
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [client_email]
    
    send_mail(subject, message, from_email, recipient_list)
