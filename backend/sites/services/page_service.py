from django.db import transaction
from sites.models import Page, Block
from sites.serializers import BlockSerializer
from templates.models import Template
from templates.engine import VariableContext, render_template
from .block_renderer import BlockRenderer

class PageService:
    """
    Service for handling page-related operations like saving content and generating previews.
    """

    @staticmethod
    @transaction.atomic
    def save_page_content(page: Page, data: dict):
        """
        Updates page fields and manages blocks (create/update/delete).
        """
        # 1. Update Page Fields
        page_fields = [
            'title', 'slug', 'description', 
            'meta_title', 'meta_description', 'h1_heading', 
            'use_h1_in_hero', 'canonical_url', 'custom_head_html',
            'primary_keywords', 'lsi_keywords', 'published'
        ]
        
        for field in page_fields:
            if field in data:
                setattr(page, field, data[field])
        
        page.save()

        # 2. Manage Blocks
        if 'blocks' in data:
            blocks_data = data['blocks']
            
            # Get existing block IDs to track deletions
            existing_block_ids = set(page.blocks.values_list('id', flat=True))
            incoming_block_ids = set()
            
            for index, block_data in enumerate(blocks_data):
                block_id = block_data.get('id')
                
                if block_id:
                    # Update existing block
                    try:
                        block = Block.objects.get(id=block_id, page=page)
                        block.type = block_data.get('type', block.type)
                        block.order = index # Update order based on list position
                        block.content = block_data.get('content', block.content)
                        block.is_active = block_data.get('is_active', block.is_active)
                        block.save()
                        incoming_block_ids.add(block.id)
                    except Block.DoesNotExist:
                        # Handle case where block ID is provided but doesn't exist (shouldn't happen normally)
                        pass
                else:
                    # Create new block
                    Block.objects.create(
                        page=page,
                        type=block_data.get('type'),
                        order=index,
                        content=block_data.get('content', {}),
                        is_active=block_data.get('is_active', True)
                    )
            
            # Delete blocks that were not in the incoming list
            blocks_to_delete = existing_block_ids - incoming_block_ids
            Block.objects.filter(id__in=blocks_to_delete).delete()

        return page

    @staticmethod
    def generate_preview(page: Page) -> str:
        """
        Generates a full HTML preview of the page using the site's template.
        Does NOT write to disk.
        """
        site = page.site
        template = site.template
        
        if not template:
            return "<h1>No template selected for this site.</h1>"

        # 1. Render Blocks to HTML
        blocks = page.blocks.filter(is_active=True).order_by('order')
        content_html = ""
        for block in blocks:
            content_html += BlockRenderer.render_block(block) + "\n"

        # 2. Prepare Context
        # We need to inject the rendered content into the page data for the context
        page_data = {
            'title': page.title,
            'description': page.description,
            'h1': page.h1_heading,
            'canonical_url': page.canonical_url,
            'content_html': content_html,
            # Add other necessary fields
        }
        
        site_data = {
            'brand_name': site.brand_name,
            'domain': site.domain,
            'language': site.language,
            'logo_url': site.logo_url,
            # Add other necessary fields
        }

        context = VariableContext(site_data, page_data)

        # 3. Render Template
        full_html = render_template(template, context)
        
        return full_html
