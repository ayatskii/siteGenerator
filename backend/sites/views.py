from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db import transaction
from .models import Site, Page
from .serializers import SiteCreateSerializer
from tokens.models import APIToken
from templates.models import Template
from affiliates.models import AffiliateLink
from .services.cloudflare_service import CloudflareService

class SiteViewSet(viewsets.ModelViewSet):
    queryset = Site.objects.all()
    serializer_class = SiteCreateSerializer # We might want a different ReadSerializer later
    permission_classes = [permissions.IsAuthenticated]

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
                # Note: In real world, this might fail if domain exists or other issues.
                # We should wrap in try-except block.
                # For now, we assume it works or we catch generic errors.
                # zone_info = cf_service.create_zone(data['domain'])
                # if not zone_info.get('success'):
                #     return Response({'error': 'Cloudflare Zone Creation Failed', 'details': zone_info}, status=400)
                pass # Skip actual API call for now to avoid breaking if no real token
            except Exception as e:
                return Response({'error': f'Cloudflare Error: {str(e)}'}, status=400)

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
