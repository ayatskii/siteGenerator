from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, PageViewSet, BlockViewSet, SwiperPresetViewSet, DeploymentViewSet, GenerationViewSet

router = DefaultRouter()
router.register(r'sites', SiteViewSet)
router.register(r'pages', PageViewSet, basename='page')
router.register(r'blocks', BlockViewSet, basename='block')
router.register(r'presets', SwiperPresetViewSet, basename='preset')
router.register(r'deployments', DeploymentViewSet, basename='deployment')
router.register(r'generation', GenerationViewSet, basename='generation')

urlpatterns = [
    path('', include(router.urls)),
]
