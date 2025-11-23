from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/', include('tokens.urls')),
    path('api/prompts/', include('prompts.urls')),
    path('api/', include('templates.urls')),
    path('api/', include('api.urls')),
    path('api/media/', include('media_library.urls')),
    path('api/', include('sites.urls')),
    path('api/', include('analytics.urls')),
    path('api/', include('affiliates.urls')),
    path('api/', include('languages.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
