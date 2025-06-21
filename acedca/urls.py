"""
URL configuration for acedca project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path , include

urlpatterns = [
    path('admin/', admin.site.urls),
    # we made a new app called resources and we are including its urls
    path('resources/', include('resources.urls')),
    # we made a new app called home and we are including its urls
    path('', include('home.urls')),
]
# ✅ Put it here at the end
handler400 = 'home.views.custom_400_view'
handler403 = 'home.views.custom_403_view'
handler404 = 'home.views.custom_404_view'
handler500 = 'home.views.custom_500_view'

from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



