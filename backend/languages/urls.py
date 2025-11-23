from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LanguagePresetViewSet

router = DefaultRouter()
router.register(r'languages', LanguagePresetViewSet, basename='language')

urlpatterns = [
    path('', include(router.urls)),
]
