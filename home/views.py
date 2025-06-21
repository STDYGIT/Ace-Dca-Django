from django.shortcuts import redirect, render
from resources.models import Year
from django.urls import reverse_lazy
from django.contrib.auth.views import LogoutView
from django.contrib.auth import logout
from resources.models import Resource
from django.conf.urls import handler404

def home(request):
    years=Year.objects.all()
    return render(request, 'home/home.html',{'years':years})

def base(request):
    return render(request,'home/base.html')

def login(request):
    return render(request,'home/login.html')

def privacy(request):
    return render(request,'home/privacy.html')
def aboutdev(request):
    return render(request,'home/aboutdev.html')

def terms(request):
    return render(request,'home/terms.html')

def google_login(request):
    return redirect('/auth/login/google-oauth2/')

def logout_view(request):
    logout(request)
    request.session.flush()  # Clears all session data
    return redirect('/')

def syllabuspage(request):
    syllabus_list = Resource.objects.filter(resource_type='Syllabus').order_by('-created_at')
    return render(request, 'home/syllabuspage.html', {'syllabus_list': syllabus_list})


def error_page(request, exception=None, status=500, title="Error", message="Something went wrong"):
    context = {
        "title": title,
        "message": message,
        "status_code": status
    }
    return render(request, "home/error.html", context=context, status=status)

def custom_400_view(request, exception):
    return error_page(request, exception, 400, "400 - Bad Request", "Your request couldn’t be processed.")

def custom_403_view(request, exception):
    return error_page(request, exception, 403, "403 - Forbidden", "You don’t have permission to access this resource.")

def custom_404_view(request, exception):
    return error_page(request, exception, 404, "404 - Page Not Found", "The page you’re looking for doesn’t exist.")

def custom_500_view(request):
    return error_page(request, None, 500, "500 - Server Error", "Oops! Something went wrong on our end.")