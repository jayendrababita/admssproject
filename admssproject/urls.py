
from django.contrib import admin
from django.urls import path, include

from admssproject.pwa_views import manifest, offline, service_worker

urlpatterns = [
    #path('admin/', admin.site.urls),
    path('manifest.webmanifest', manifest, name='pwa_manifest'),
    path('service-worker.js', service_worker, name='pwa_service_worker'),
    path('offline/', offline, name='pwa_offline'),
    path('', include('admssapp.urls')),
    path('', include('admssadmin.urls')),
    path('', include('admsscoll.urls')),
    path('', include('admssinsurance.urls')),
]
