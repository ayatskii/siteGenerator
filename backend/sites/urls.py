from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SiteViewSet, PageViewSet, BlockViewSet, SwiperPresetViewSet

router = DefaultRouter()
router.register(r'blocks', BlockViewSet, basename='block')
router.register(r'swiper-presets', SwiperPresetViewSet, basename='swiper-preset')
router.register(r'pages', PageViewSet, basename='page')
router.register(r'', SiteViewSet, basename='site')

urlpatterns = [
    path('', include(router.urls)),
]
