from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from .models import Template, TemplateSection, TemplateVariable
from .serializers import TemplateSerializer, TemplateSectionSerializer, TemplateVariableSerializer

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload(self, request):
        if 'file' not in request.data:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        zip_file = request.data['file']
        # Logic to process zip file would go here
        # For now, we just return a success message
        return Response({'status': 'File received'}, status=status.HTTP_200_OK)


class TemplateSectionViewSet(viewsets.ModelViewSet):
    queryset = TemplateSection.objects.all()
    serializer_class = TemplateSectionSerializer

class TemplateVariableViewSet(viewsets.ModelViewSet):
    queryset = TemplateVariable.objects.all()
    serializer_class = TemplateVariableSerializer
