from rest_framework import viewsets, permissions
from .models import AffiliateLink
from .serializers import AffiliateLinkSerializer

class AffiliateLinkViewSet(viewsets.ModelViewSet):
    queryset = AffiliateLink.objects.all()
    serializer_class = AffiliateLinkSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)
