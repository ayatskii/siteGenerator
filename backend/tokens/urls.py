from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import APITokenViewSet

router = DefaultRouter()
router.register(r'tokens', APITokenViewSet, basename='token')

urlpatterns = [
    path('', include(router.urls)),
]
