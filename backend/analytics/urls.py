from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AnalyticsViewSet, UmamiConfigViewSet

router = DefaultRouter()
router.register(r'analytics', AnalyticsViewSet, basename='analytics')
router.register(r'umami-config', UmamiConfigViewSet, basename='umami-config')

urlpatterns = router.urls
