from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, TemplateSectionViewSet, TemplateVariableViewSet

router = DefaultRouter()
router.register(r'templates', TemplateViewSet)
router.register(r'sections', TemplateSectionViewSet)
router.register(r'variables', TemplateVariableViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
