from rest_framework import viewsets, permissions
from .models import LanguagePreset
from .serializers import LanguagePresetSerializer

class LanguagePresetViewSet(viewsets.ModelViewSet):
    queryset = LanguagePreset.objects.all()
    serializer_class = LanguagePresetSerializer
    permission_classes = [permissions.IsAuthenticated]
