from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import TextPrompt, ImagePrompt
from sites.models import Page, Block
from .serializers import TextPromptSerializer, ImagePromptSerializer, BulkGenerationRequestSerializer, BulkGenerationResponseSerializer
from .services import AIService
import logging

logger = logging.getLogger(__name__)

class PromptListView(generics.ListCreateAPIView):
    """
    List available text prompts or create a new one.
    """
    serializer_class = TextPromptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = TextPrompt.objects.filter(is_active=True)
        target_type = self.request.query_params.get('target_type')
        if target_type:
            queryset = queryset.filter(target_type=target_type)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class PromptDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a text prompt instance.
    """
    queryset = TextPrompt.objects.all()
    serializer_class = TextPromptSerializer
    permission_classes = [IsAuthenticated]


class ImagePromptListView(generics.ListCreateAPIView):
    """
    List available image prompts or create a new one.
    """
    serializer_class = ImagePromptSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ImagePrompt.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ImagePromptDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete an image prompt instance.
    """
    queryset = ImagePrompt.objects.all()
    serializer_class = ImagePromptSerializer
    permission_classes = [IsAuthenticated]


class GenerateContentView(APIView):
    """
    Trigger AI content generation.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = BulkGenerationRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        page_id = data['page_id']
        generations = data['generations']

        try:
            page = Page.objects.get(id=page_id)
            if page.site.owner != request.user:
                return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)
        except Page.DoesNotExist:
            return Response({'error': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)

        # Base Context
        base_context = {
            'keywords': page.primary_keywords,
            'lsi_phrases': page.lsi_keywords,
            'brand': page.site.brand_name,
            'language': page.site.language,
            'page_title': page.title,
            'page_description': page.description,
        }

        results = []
        errors = []
        service = AIService()

        for item in generations:
            block_id = item['block_id']
            prompt_id = item['prompt_id']
            extra_context = item.get('extra_context', {})
            
            # Block Context
            block_context = base_context.copy()
            block_context.update(extra_context)
            
            try:
                block = Block.objects.get(id=block_id)
                block_context['current_content'] = block.content
            except Block.DoesNotExist:
                errors.append(f"Block {block_id} not found")
                continue

            # Generate
            result = service.generate_content(prompt_id, block_context)
            
            if result['success']:
                # Auto-update block content if needed? 
                # For now, just return the content and let frontend handle update
                results.append({
                    'block_id': block_id,
                    'content': result['content'],
                    'success': True
                })
            else:
                results.append({
                    'block_id': block_id,
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                })
                errors.append(f"Block {block_id}: {result.get('error')}")

        response_data = {
            'status': 'completed',
            'results': results,
            'errors': errors
        }
        
        return Response(response_data)
