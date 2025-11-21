from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from .models import MediaFolder, MediaAsset
from .serializers import MediaFolderSerializer, MediaAssetSerializer
from .services import ImageProcessingService

class MediaFolderViewSet(viewsets.ModelViewSet):
    serializer_class = MediaFolderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return MediaFolder.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

class MediaAssetViewSet(viewsets.ModelViewSet):
    serializer_class = MediaAssetSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser, JSONParser)

    def get_queryset(self):
        return MediaAsset.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
        # Process image after save
        instance = serializer.instance
        ImageProcessingService.process_upload(instance.file, instance)

    @action(detail=False, methods=['post'])
    def upload_url(self, request):
        url = request.data.get('url')
        folder_id = request.data.get('folder')
        
        if not url:
            return Response({'error': 'URL is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        folder = None
        if folder_id:
            try:
                folder = MediaFolder.objects.get(id=folder_id, owner=request.user)
            except MediaFolder.DoesNotExist:
                return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            asset = ImageProcessingService.upload_from_url(url, folder, request.user)
            serializer = self.get_serializer(asset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def upload_base64(self, request):
        data = request.data.get('image')
        filename = request.data.get('filename', 'upload')
        folder_id = request.data.get('folder')
        
        if not data:
            return Response({'error': 'Image data is required'}, status=status.HTTP_400_BAD_REQUEST)

        folder = None
        if folder_id:
            try:
                folder = MediaFolder.objects.get(id=folder_id, owner=request.user)
            except MediaFolder.DoesNotExist:
                return Response({'error': 'Folder not found'}, status=status.HTTP_404_NOT_FOUND)

        try:
            asset = ImageProcessingService.upload_from_base64(data, filename, folder, request.user)
            serializer = self.get_serializer(asset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
