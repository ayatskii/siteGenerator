from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MediaFolderViewSet, MediaAssetViewSet

router = DefaultRouter()
router.register(r'folders', MediaFolderViewSet, basename='media-folder')
router.register(r'assets', MediaAssetViewSet, basename='media-asset')

urlpatterns = [
    path('', include(router.urls)),
]
