from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import Resource, Semester
import os

User = get_user_model()

@receiver(post_save, sender=Resource)
def send_resource_notification(sender, instance, created, **kwargs):
    if created:  # Only send notification for new resources
        # Get all users
        users = User.objects.all()
        
        # Prepare email content
        subject = f'New Resource Available: {instance.subject}'
        
        # Create context for template
        context = {
            'user': None,  # Will be set for each user
            'resource': instance,
            'download_url': f"{settings.SITE_URL}/resources/download/{instance.id}/",
        }
        
        # Get the logo path
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'logo.png')
        
        # Send email to each user
        for user in users:
            context['user'] = user
            
            # Render the email template
            html_message = render_to_string('resources/email/resource_notification.html', context)
            
            # Send email with attachment
            try:
                send_mail(
                    subject=subject,
                    message='',  # Plain text version (empty as we're using HTML)
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
            except Exception as e:
                print(f"Failed to send email to {user.email}: {str(e)}")
                # You might want to log this error or handle it differently 