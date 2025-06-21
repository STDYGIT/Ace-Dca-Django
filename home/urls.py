from sqlite3 import paramstyle
from django.urls import path,include
from .views import base,syllabuspage,home,google_login,logout_view,privacy,terms,aboutdev
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.contrib.auth.views import LogoutView


urlpatterns = [
    # Enable allauth URLs
    path('', home, name='home'),
    path('base/', base, name='base'),
    path('syllabuspage/', syllabuspage, name='syllabuspage'),
    path('resources/', include('resources.urls')),
    path('auth/', include('social_django.urls', namespace='social')),  # Google OAuth
    path('login/', google_login, name='login'),  # Force Google login
    path('logout/', logout_view, name='logout'),  # Logout and redirect home
    path('privacy/',privacy, name='privacy'),
    path('terms/',terms, name='terms'),
    path('aboutdev/',aboutdev, name='aboutdev'),
]

