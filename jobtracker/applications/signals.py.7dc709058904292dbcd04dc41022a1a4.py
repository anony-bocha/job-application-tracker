from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import JobApplication

@receiver(post_save, sender=JobApplication)
def send_application_notification(sender, instance, created, **kwargs):
    if created:
        user_email = instance.user.email
        if user_email:  # Ensure user has email
            subject = f"New Job Application Added: {instance.position} at {instance.company.name}"
            message = f"""
Hi {instance.user.username},

You have successfully added a new job application to your tracker.

Company: {instance.company.name}
Position: {instance.position}
Status: {instance.get_status_display()}
Applied Date: {instance.applied_date}

You can view this application by logging into your Job Tracker.

Keep going!

- Job Tracker
"""
            send_mail(subject, message, None, [user_email], fail_silently=True)
