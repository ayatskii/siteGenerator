from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/', include('tokens.urls')),
    path('api/', include('prompts.urls')),
    path('api/', include('templates.urls')),
    path('api/', include('api.urls')),
    path('api/media/', include('media_library.urls')),
]
