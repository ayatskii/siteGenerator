from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework.exceptions import ValidationError
from .models import Template, TemplateSection, TemplateVariable
from .serializers import TemplateSerializer, TemplateSectionSerializer, TemplateVariableSerializer
from .services import TemplateUploadService

class TemplateViewSet(viewsets.ModelViewSet):
    queryset = Template.objects.all()
    serializer_class = TemplateSerializer

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser])
    def upload(self, request):
        if 'file' not in request.data:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            service = TemplateUploadService(request.data['file'])
            service.process()
            return Response({'status': 'Template uploaded successfully'}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TemplateSectionViewSet(viewsets.ModelViewSet):
    queryset = TemplateSection.objects.all()
    serializer_class = TemplateSectionSerializer

class TemplateVariableViewSet(viewsets.ModelViewSet):
    queryset = TemplateVariable.objects.all()
    serializer_class = TemplateVariableSerializer
