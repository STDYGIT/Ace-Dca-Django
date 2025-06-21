from django.urls import path
from .views import Sem1, Y1, Y2, Y3,add,upload_resource_view,edit_resource,delete_resource,ignore_non_existent_resource,ignore_resource
# localhost:8000/resources/year1
app_name = 'resources'
urlpatterns = [
    path('<int:semester_id>/', Sem1, name='Sem1'),
    path('Y1/', Y1, name='Y1'),
    path('Y2/', Y2, name='Y2'),
    path('Y3/', Y3, name='Y3'),
    path('add/', add, name='add'),
    path('upload/<int:semester_id>/', upload_resource_view, name='upload_resource'),
    # REMOVE 'resources/' prefix from these paths!
    path('edit/<int:resource_id>/', edit_resource, name='edit_resource'), # Corrected
    path('delete/<int:resource_id>/', delete_resource, name='delete_resource'), # Corrected
    path('ignore_resource/<int:resource_id>/', ignore_resource, name='ignore_resource'),
    path('ignore_non_existent/', ignore_non_existent_resource, name='ignore_non_existent_resource'),
]

# media settings for pyqs and books
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += staticfiles_urlpatterns()