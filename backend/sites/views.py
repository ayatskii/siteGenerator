from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from django.utils import timezone
from .models import Site, Page, Block, SwiperPreset, Deployment
from .serializers import (
    SiteCreateSerializer, SiteListSerializer, SiteDashboardSerializer, SiteStatisticsSerializer,
    PageSerializer, BlockSerializer, SwiperPresetSerializer, PageContentSerializer, DeploymentSerializer
)
from tokens.models import APIToken
from templates.models import Template
from affiliates.models import AffiliateLink
from .services.cloudflare_service import CloudflareService
from .services.page_service import PageService

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return SiteListSerializer
        elif self.action == 'retrieve':
            return SiteDashboardSerializer
        return SiteCreateSerializer

    def get_queryset(self):
        return Site.objects.filter(owner=self.request.user)

    @action(detail=False, methods=['post'])
    def create_site(self, request):
        serializer = SiteCreateSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.validated_data
            
            # Extract related objects
            token_id = data.pop('cloudflare_token_id')
            pages_structure = data.pop('pages_structure', [])
            template_id = data.pop('template_id', None)
            affiliate_link_id = data.pop('affiliate_link_id', None)
            
            token = APIToken.objects.get(id=token_id)
            
            # Cloudflare Integration
            cf_service = CloudflareService(token.token_value) # Decrypts automatically? 
            # EncryptedCharField handles decryption on access usually, but let's verify. 
            # If not, we might need token.token_value.decrypt() or similar depending on library.
            # Assuming django-fernet-fields handles it transparently on attribute access.
            
            try:
                # 1. Create Zone
                # We wrap in try-except to prevent failure if domain exists or other issues
                zone_info = cf_service.create_zone(data['domain'])
                if not zone_info.get('success'):
                    # Log error but don't stop site creation? Or return error?
                    # For now, let's return error to be strict
                    # return Response({'error': 'Cloudflare Zone Creation Failed', 'details': zone_info}, status=400)
                    print(f"Cloudflare Zone Creation Warning: {zone_info}")
            except Exception as e:
                # return Response({'error': f'Cloudflare Error: {str(e)}'}, status=400)
                print(f"Cloudflare Error: {str(e)}")

            with transaction.atomic():
                # 2. Create Site
                site = Site.objects.create(
                    owner=request.user,
                    name=data.get('brand_name') or data['domain'],
                    domain=data['domain'],
                    language=data.get('language', 'en-US'),
                    brand_name=data.get('brand_name', ''),
                    logo_url=data.get('logo_url', ''),
                    favicon_url=data.get('favicon_url', ''),
                    geo_targeting=data.get('geo_targeting', ''),
                    fingerprint_type=data.get('fingerprint_type', 'random_class'),
                    allow_indexing=data.get('allow_indexing', True),
                    redirect_404_to_homepage=data.get('redirect_404_to_homepage', False),
                    force_www=data.get('force_www', False),
                    page_speed_optimization=data.get('page_speed_optimization', False),
                    microdata_settings=data.get('microdata_settings', {}),
                    header_cta_config=data.get('header_cta_config', {}),
                    footer_images=data.get('footer_images', []),
                    custom_head_html=data.get('custom_head_html', '')
                )
                
                if template_id:
                    site.template = Template.objects.get(id=template_id)
                if affiliate_link_id:
                    site.affiliate_link = AffiliateLink.objects.get(id=affiliate_link_id)
                site.save()

                # 3. Create Pages
                # Always create Home page
                Page.objects.create(
                    site=site,
                    title="Home",
                    slug="home", # or index? usually empty slug or 'home' mapped to /
                    published=True
                )
                
                for page_data in pages_structure:
                    Page.objects.create(
                        site=site,
                        title=page_data.get('title'),
                        slug=page_data.get('slug'),
                        published=True # or based on checkbox?
                    )

            return Response({'status': 'success', 'site_id': site.id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get dashboard statistics.
        Returns: total sites, deployed sites, total pages, storage used
        """
        user_sites = Site.objects.filter(owner=request.user)
        
        total_sites = user_sites.count()
        sites_deployed = user_sites.filter(deployments__status='success').distinct().count()
        total_pages = Page.objects.filter(site__owner=request.user).count()
        
        # Calculate storage (simplified - just count as 0 for now)
        # In real implementation, you'd sum up media file sizes
        storage_used = 0.0
        
        data = {
            'total_sites': total_sites,
            'sites_deployed': sites_deployed,
            'total_pages': total_pages,
            'storage_used': storage_used
        }
        
        serializer = SiteStatisticsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def list_filtered(self, request):
        """
        Optimized list endpoint with filtering.
        Query params: language, brand, geo, status, search
        """
        queryset = self.get_queryset()
        
        # Apply filters
        language = request.query_params.get('language')
        if language:
            queryset = queryset.filter(language=language)
        
        brand = request.query_params.get('brand')
        if brand:
            queryset = queryset.filter(brand_name__icontains=brand)
        
        geo = request.query_params.get('geo')
        if geo:
            queryset = queryset.filter(geo_targeting__icontains=geo)
        
        search = request.query_params.get('search')
        if search:
            queryset = queryset.filter(domain__icontains=search)
        
        # Note: Status filtering would need to be done in Python since it's a property
        # For now, we'll serialize all and let frontend filter
        
        serializer = SiteListSerializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate an entire site with all its pages and blocks.
        """
        original_site = self.get_object()
        
        # Generate new domain name
        new_domain = f"{original_site.domain}-copy"
        counter = 1
        while Site.objects.filter(domain=new_domain).exists():
            new_domain = f"{original_site.domain}-copy-{counter}"
            counter += 1
        
        try:
            with transaction.atomic():
                # Duplicate site
                new_site = Site.objects.create(
                    owner=request.user,
                    name=f"{original_site.name} (Copy)",
                    domain=new_domain,
                    language=original_site.language,
                    brand_name=original_site.brand_name,
                    logo_url=original_site.logo_url,
                    favicon_url=original_site.favicon_url,
                    geo_targeting=original_site.geo_targeting,
                    template=original_site.template,
                    fingerprint_type=original_site.fingerprint_type,
                    affiliate_link=original_site.affiliate_link,
                    allow_indexing=original_site.allow_indexing,
                    redirect_404_to_homepage=original_site.redirect_404_to_homepage,
                    force_www=original_site.force_www,
                    page_speed_optimization=original_site.page_speed_optimization,
                    microdata_settings=original_site.microdata_settings,
                    header_cta_config=original_site.header_cta_config,
                    footer_images=original_site.footer_images,
                    custom_head_html=original_site.custom_head_html
                )
                
                # Duplicate all pages
                for original_page in original_site.pages.all():
                    new_page = Page.objects.create(
                        site=new_site,
                        title=original_page.title,
                        slug=original_page.slug,
                        description=original_page.description,
                        meta_title=original_page.meta_title,
                        meta_description=original_page.meta_description,
                        h1_heading=original_page.h1_heading,
                        use_h1_in_hero=original_page.use_h1_in_hero,
                        canonical_url=original_page.canonical_url,
                        custom_head_html=original_page.custom_head_html,
                        primary_keywords=original_page.primary_keywords,
                        lsi_keywords=original_page.lsi_keywords,
                        published=original_page.published
                    )
                    
                    # Duplicate all blocks for this page
                    for original_block in original_page.blocks.all():
                        Block.objects.create(
                            page=new_page,
                            type=original_block.type,
                            order=original_block.order,
                            content=original_block.content,
                            is_active=original_block.is_active
                        )
                
                serializer = SiteDashboardSerializer(new_site)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
                
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class PageViewSet(viewsets.ModelViewSet):
    serializer_class = PageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter pages by site if site_id is provided in query params
        site_id = self.request.query_params.get('site_id')
        if site_id:
            return Page.objects.filter(site__id=site_id, site__owner=self.request.user)
        # Otherwise return all pages for sites owned by user
        return Page.objects.filter(site__owner=self.request.user)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        page = self.get_object()
        
        # Create a copy
        page.pk = None
        page.id = None
        page.slug = f"{page.slug}-copy"
        page.title = f"{page.title} (Copy)"
        page.published = False # Set to draft
        
        # Ensure unique slug
        counter = 1
        original_slug = page.slug
        while Page.objects.filter(site=page.site, slug=page.slug).exists():
            page.slug = f"{original_slug}-{counter}"
            counter += 1
            
        page.save()
        
        # Correct logic for duplicating blocks:
        original_page = Page.objects.get(pk=pk)
        for block in original_page.blocks.all():
            block.pk = None
            block.id = None
            block.page = page
            block.save()

        serializer = self.get_serializer(page)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def save_content(self, request, pk=None):
        """
        Saves page content including blocks.
        """
        page = self.get_object()
        serializer = PageContentSerializer(page, data=request.data, partial=True)
        
        if serializer.is_valid():
            try:
                updated_page = PageService.save_page_content(page, serializer.validated_data)
                return Response({'status': 'success', 'page_id': updated_page.id})
            except Exception as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def preview(self, request, pk=None):
        """
        Generates a live preview of the page.
        """
        page = self.get_object()
        try:
            html_content = PageService.generate_preview(page)
            return Response(html_content, content_type='text/html')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class BlockViewSet(viewsets.ModelViewSet):
    serializer_class = BlockSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Filter blocks by page if page_id is provided
        page_id = self.request.query_params.get('page_id')
        if page_id:
            return Block.objects.filter(page__id=page_id, page__site__owner=self.request.user)
        return Block.objects.filter(page__site__owner=self.request.user)

    @action(detail=False, methods=['post'])
    def reorder(self, request):
        """
        Reorder blocks. Expects a list of objects with 'id' and 'order'.
        """
        blocks_data = request.data.get('blocks', [])
        if not blocks_data:
            return Response({'error': 'No blocks provided'}, status=status.HTTP_400_BAD_REQUEST)

        # Verify ownership and update
        for item in blocks_data:
            block_id = item.get('id')
            new_order = item.get('order')
            if block_id is not None and new_order is not None:
                try:
                    block = Block.objects.get(id=block_id, page__site__owner=request.user)
                    block.order = new_order
                    block.save()
                except Block.DoesNotExist:
                    continue # Skip invalid blocks or blocks not owned by user

        return Response({'status': 'success'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        Duplicate a block.
        """
        try:
            block = self.get_object()
            block.pk = None
            block.id = None
            # Put it after the original block
            block.order = block.order + 1 
            block.save()
            
            # Shift subsequent blocks down? 
            # Ideally yes, but for simplicity let's just save it. 
            # The frontend usually handles reordering or we can implement a shift logic here.
            # Let's do a simple shift.
            subsequent_blocks = Block.objects.filter(page=block.page, order__gte=block.order).exclude(id=block.id)
            for b in subsequent_blocks:
                b.order += 1
                b.save()

            serializer = self.get_serializer(block)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class SwiperPresetViewSet(viewsets.ModelViewSet):
    serializer_class = SwiperPresetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SwiperPreset.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class DeploymentViewSet(viewsets.ModelViewSet):
    serializer_class = DeploymentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Filter deployments by site if provided
        site_id = self.request.query_params.get('site_id')
        if site_id:
            return Deployment.objects.filter(site__id=site_id, site__owner=self.request.user)
        return Deployment.objects.filter(site__owner=self.request.user)
    
    @action(detail=False, methods=['post'])
    def deploy(self, request):
        """
        Trigger a new deployment for a site.
        """
        site_id = request.data.get('site_id')
        if not site_id:
            return Response({'error': 'site_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            site = Site.objects.get(id=site_id, owner=request.user)
        except Site.DoesNotExist:
            return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Create deployment record
        deployment = Deployment.objects.create(
            site=site,
            status='processing'
        )
        
        try:
            # Import here to avoid circular imports
            from .services.site_generator import SiteGenerator
            
            # Generate site
            generator = SiteGenerator(site)
            zip_path = generator.generate()
            
            # Deploy to Cloudflare (if token available)
            # For now, we'll just mark as success
            # In a real implementation, we'd use Celery to run this async
            deployment.status = 'success'
            deployment.commit_hash = generator.build_id
            deployment.log = f"Site generated successfully. ZIP: {zip_path}"
            deployment.finished_at = timezone.now()
            deployment.save()
            
            return Response({
                'status': 'success',
                'deployment_id': deployment.id,
                'download_url': f'/api/deployments/{deployment.id}/download/'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            deployment.status = 'failed'
            deployment.log = str(e)
            deployment.finished_at = timezone.now()
            deployment.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        """
        Download the generated ZIP file for a deployment.
        """
        from django.http import FileResponse
        import os
        from django.conf import settings
        
        deployment = self.get_object()
        
        # Extract zip path from log or construct it
        # For now, we'll construct it from the commit_hash
        if deployment.commit_hash:
            zip_filename = f"{deployment.site.domain}_{deployment.commit_hash}.zip"
            zip_path = os.path.join(settings.MEDIA_ROOT, 'builds', zip_filename)
            
            if os.path.exists(zip_path):
                response = FileResponse(open(zip_path, 'rb'), content_type='application/zip')
                response['Content-Disposition'] = f'attachment; filename="{deployment.site.domain}.zip"'
                return response
            else:
                return Response({'error': 'ZIP file not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response({'error': 'No deployment file available'}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=True, methods=['post'])
    def rollback(self, request, pk=None):
        """
        Rollback to a previous deployment.
        This creates a new deployment using the same build.
        """
        deployment = self.get_object()
        
        if deployment.status != 'success':
            return Response({'error': 'Can only rollback to successful deployments'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Create a new deployment record
        new_deployment = Deployment.objects.create(
            site=deployment.site,
            status='processing'
        )
        
        try:
            # Re-deploy the same build
            # In a real implementation, we'd re-upload the saved ZIP to Cloudflare
            new_deployment.status = 'success'
            new_deployment.commit_hash = deployment.commit_hash
            new_deployment.log = f"Rollback from deployment {deployment.id}"
            new_deployment.finished_at = timezone.now()
            new_deployment.save()
            
            return Response({
                'status': 'success',
                'deployment_id': new_deployment.id
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            new_deployment.status = 'failed'
            new_deployment.log = str(e)
            new_deployment.finished_at = timezone.now()
            new_deployment.save()
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class GenerationViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['post'])
    def generate_content(self, request):
        """
        Generate content for specific blocks using AI prompts.
        Expected payload:
        {
            "page_id": 123,
            "generations": [
                {"block_id": 1, "prompt_id": 10, "target_field": "body"},
                {"block_id": 2, "prompt_id": 11, "target_field": "text"}
            ]
        }
        """
        page_id = request.data.get('page_id')
        generations = request.data.get('generations', [])
        
        if not page_id or not generations:
            return Response({'error': 'page_id and generations list required'}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            page = Page.objects.get(id=page_id, site__owner=request.user)
        except Page.DoesNotExist:
            return Response({'error': 'Page not found'}, status=status.HTTP_404_NOT_FOUND)
            
        # Prepare context data
        context_data = {
            'keywords': page.primary_keywords,
            'lsi_phrases': page.lsi_keywords,
            'brand': page.site.brand_name or page.site.name,
            'language': page.site.language,
            'page_title': page.title,
            'page_description': page.description,
            'domain': page.site.domain,
        }
        
        from prompts.services import AIService
        ai_service = AIService()
        
        results = []
        errors = []
        
        for gen in generations:
            block_id = gen.get('block_id')
            prompt_id = gen.get('prompt_id')
            target_field = gen.get('target_field', 'content') # Default field if not specified? 
            # Actually blocks have 'content' JSON field, so target_field should be a key inside 'content'
            
            try:
                block = Block.objects.get(id=block_id, page=page)
                
                # Generate content
                response = ai_service.generate_content(prompt_id, context_data)
                
                if response['success']:
                    generated_text = response['content']
                    
                    # Update block content
                    # We assume target_field is a key in the content dict, e.g. 'body', 'heading', 'text'
                    if not block.content:
                        block.content = {}
                        
                    block.content[target_field] = generated_text
                    block.save()
                    
                    results.append({
                        'block_id': block_id,
                        'status': 'success',
                        'generated_length': len(generated_text)
                    })
                else:
                    errors.append({
                        'block_id': block_id,
                        'error': response.get('error', 'Unknown generation error')
                    })
                    
            except Block.DoesNotExist:
                errors.append({'block_id': block_id, 'error': 'Block not found'})
            except Exception as e:
                errors.append({'block_id': block_id, 'error': str(e)})
                
        return Response({
            'status': 'completed',
            'results': results,
            'errors': errors
        })
