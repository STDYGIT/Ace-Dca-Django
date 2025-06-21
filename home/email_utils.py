from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()

def send_resource_notification(resource, request):
    """
    Send email notifications to all users about a new resource upload.
    
    Args:
        resource: The resource object that was uploaded
        request: The HTTP request object to build absolute URLs
    """
    # Get all users
    users = User.objects.all()
    
    # Prepare email subject
    subject = f'New Resource Uploaded - {resource.subject}'
    
    # Get the download URL
    download_url = request.build_absolute_uri(
        reverse('download_resource', kwargs={'resource_id': resource.id})
    )
    
    # Send email to each user
    for user in users:
        # Prepare email context
        context = {
            'user': user,
            'resource': resource,
            'download_url': download_url,
        }
        
        # Render email template
        html_message = render_to_string('email/resource_notification.html', context)
        
        # Send email
        try:
            send_mail(
                subject=subject,
                message='',  # Plain text version (empty as we're using HTML)
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
        except Exception as e:
            print(f"Failed to send email to {user.email}: {str(e)}")
            # You might want to log this error or handle it differently 