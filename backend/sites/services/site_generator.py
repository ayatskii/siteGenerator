import os
import shutil
import uuid
import zipfile
import json
from django.conf import settings
from django.utils import timezone
from templates.models import Template
from templates.engine import VariableContext, render_template
from templates.fingerprinting import CSSRandomizer, FootprintManager
from templates.image_processing import ImageFingerprinter
from sites.services.block_renderer import BlockRenderer
from sites.services.pagespeed import PageSpeedOptimizer
from media_library.services import ImageProcessingService

class SiteGenerator:
    def __init__(self, site, template_id=None, fingerprint_config=None):
        self.site = site
        # Use site's template if not provided
        self.template = Template.objects.get(id=template_id) if template_id else site.template
        self.fingerprint_config = fingerprint_config or {}
        
        # Use site's fingerprint type if not provided in config
        if not self.fingerprint_config.get('footprint_type'):
            self.fingerprint_config['footprint_type'] = site.fingerprint_type.upper() if site.fingerprint_type else 'CUSTOM'

        self.build_id = str(uuid.uuid4())
        self.build_dir = os.path.join(settings.MEDIA_ROOT, 'builds', self.build_id)
        
        # Fingerprinting tools
        seed = str(site.id) # Deterministic seed based on site ID
        self.css_randomizer = CSSRandomizer(seed)
        self.image_fingerprinter = ImageFingerprinter(seed)
        
        # Determine footprint type
        footprint_type = self.fingerprint_config.get('footprint_type', 'CUSTOM')
        self.footprint_manager = FootprintManager(footprint_type, seed=seed)

    def generate(self):
        """
        Orchestrates the site generation process.
        """
        try:
            os.makedirs(self.build_dir, exist_ok=True)
            
            # 1. Prepare Assets
            self._prepare_assets()
            
            # 2. Fingerprint Assets
            self._fingerprint_assets()
            
            # 3. Render Pages
            self._render_pages()
            
            # 4. Package
            output_zip = self._package_site()
            
            return output_zip
            
        except Exception as e:
            # Log error here
            print(f"Error generating site: {e}")
            raise e
        finally:
            # Cleanup build dir - keep it for now for debugging/download
            # shutil.rmtree(self.build_dir) 
            pass

    def _prepare_assets(self):
        """
        Copies template assets, generates favicons, and copies logo to build directory.
        """
        target_assets = os.path.join(self.build_dir, 'assets')
        os.makedirs(target_assets, exist_ok=True)
        
        # 1. Copy template assets if available
        if self.template:
            slug = self.template.name.lower().replace(' ', '-')
            source_assets = os.path.join(settings.MEDIA_ROOT, 'templates', slug, 'assets')
            
            if os.path.exists(source_assets):
                # Copy all assets
                for item in os.listdir(source_assets):
                    s = os.path.join(source_assets, item)
                    d = os.path.join(target_assets, item)
                    if os.path.isdir(s):
                        shutil.copytree(s, d)
                    else:
                        shutil.copy2(s, d)
        
        # 2. Generate favicons from site favicon (if SVG)
        if self.site.favicon_url and self.site.favicon_url.endswith('.svg'):
            try:
                # Assume favicon_url is a path to media
                favicon_path = os.path.join(settings.MEDIA_ROOT, self.site.favicon_url.lstrip('/'))
                
                if os.path.exists(favicon_path):
                    favicon_output_dir = os.path.join(target_assets, 'favicons')
                    favicon_files = ImageProcessingService.generate_favicons(favicon_path, favicon_output_dir)
                    
                    # Store paths for later use in HTML generation
                    self._favicon_files = favicon_files
                else:
                    print(f"Favicon source not found: {favicon_path}")
                    self._favicon_files = {}
            except Exception as e:
                print(f"Error generating favicons: {e}")
                self._favicon_files = {}
        else:
            self._favicon_files = {}
        
        # 3. Copy logo to assets (for footprint-aware path replacement)
        if self.site.logo_url:
            try:
                logo_path = os.path.join(settings.MEDIA_ROOT, self.site.logo_url.lstrip('/'))
                
                if os.path.exists(logo_path):
                    logo_filename = os.path.basename(logo_path)
                    logo_dest = os.path.join(target_assets, 'images', logo_filename)
                    os.makedirs(os.path.dirname(logo_dest), exist_ok=True)
                    shutil.copy2(logo_path, logo_dest)
                    
                    # Update logo_url to point to copied version
                    self._logo_relative_path = f"assets/images/{logo_filename}"
                else:
                    self._logo_relative_path = self.site.logo_url
            except Exception as e:
                print(f"Error copying logo: {e}")
                self._logo_relative_path = self.site.logo_url
        else:
            self._logo_relative_path = ""

    def _fingerprint_assets(self):
        """
        Applies fingerprinting to CSS and Images.
        """
        assets_dir = os.path.join(self.build_dir, 'assets')
        if not os.path.exists(assets_dir):
            return

        for root, dirs, files in os.walk(assets_dir):
            for file in files:
                file_path = os.path.join(root, file)
                ext = os.path.splitext(file)[1].lower()
                
                # CSS Randomization
                if ext == '.css':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Generate map (accumulative if multiple CSS files)
                    self.css_randomizer.generate_class_map(content)
                    
                    # Apply map to CSS itself
                    new_content = self.css_randomizer.apply_class_map(content, is_css=True)
                    
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                
                # Image Fingerprinting
                elif ext in ['.jpg', '.jpeg', '.png', '.webp']:
                    self.image_fingerprinter.process_image(file_path, file_path)

    def _generate_header_menu(self):
        """Generate HTML for header menu from site pages."""
        pages = self.site.pages.filter(published=True).all()
        menu_items = []
        
        for page in pages:
            # Check if page should appear in header (you may need to add a field to Page model)
            # For now, include all published pages
            slug = page.slug if page.slug != 'index' else ''
            href = f"/{slug}.html" if slug else "/index.html"
            menu_items.append(f'<a href="{href}">{page.title}</a>')
        
        return ' | '.join(menu_items) if menu_items else ''
    
    def _generate_footer_menu(self):
        """Generate HTML for footer menu from site pages."""
        # Similar to header menu, but might filter differently
        return self._generate_header_menu()  # Simplified for now
    
    def _generate_footer_images(self):
        """Generate HTML for footer images (payment methods, etc.)."""
        if not self.site.footer_images:
            return ''
        
        images_html = []
        for img_url in self.site.footer_images:
            images_html.append(f'<img src="{img_url}" alt="" loading="lazy" />')
        
        return ' '.join(images_html)
    
    def _generate_metadata(self, page):
        """Generate HTML meta tags for a page."""
        meta_tags = []
        
        if page.meta_title:
            meta_tags.append(f'<title>{page.meta_title}</title>')
        
        if page.meta_description:
            meta_tags.append(f'<meta name="description" content="{page.meta_description}" />')
        
        if page.canonical_url:
            meta_tags.append(f'<link rel="canonical" href="{page.canonical_url}" />')
        
        # Add OG tags for social sharing
        if page.meta_title:
            meta_tags.append(f'<meta property="og:title" content="{page.meta_title}" />')
        if page.meta_description:
            meta_tags.append(f'<meta property="og:description" content="{page.meta_description}" />')
        if self.site.domain:
            meta_tags.append(f'<meta property="og:url" content="https://{self.site.domain}/{page.slug}.html" />')
        
        return '\n'.join(meta_tags)
    
    def _generate_microdata(self, page):
        """Generate JSON-LD microdata for a page."""
        # Use site's microdata_settings or generate basic Organization schema
        microdata_config = self.site.microdata_settings or {}
        
        if not microdata_config or microdata_config.get('inherit_presets'):
            # Generate basic Organization schema
            schema = {
                "@context": "https://schema.org",
                "@type": "Organization",
                "name": self.site.brand_name or self.site.name,
                "url": f"https://{self.site.domain}",
            }
            
            if self._logo_relative_path:
                schema["logo"] = f"https://{self.site.domain}/{self._logo_relative_path}"
        else:
            # Use custom microdata
            import json
            try:
                schema = json.loads(microdata_config.get('custom_json_ld', '{}'))
            except:
                schema = {}
        
        if schema:
            import json
            return f'<script type="application/ld+json">\n{json.dumps(schema, indent=2)}\n</script>'
        
        return ''
    
    def _generate_favicon_links(self):
        """Generate HTML link tags for all favicon variants."""
        if not self._favicon_files:
            # Fallback to site's favicon_url if no generated files
            if self.site.favicon_url:
                return f'<link rel="icon" href="{self.site.favicon_url}" />'
            return ''
        
        links = []
        
        # ICO
        if 'ico' in self._favicon_files:
            links.append('<link rel="icon" href="/assets/favicons/favicon.ico" />')
        
        # PNG variants
        for size in [16, 32, 48]:
            if f'png_{size}' in self._favicon_files:
                links.append(f'<link rel="icon" type="image/png" sizes="{size}x{size}" href="/assets/favicons/favicon-{size}x{size}.png" />')
        
        # Apple touch icon
        if 'apple_touch_icon' in self._favicon_files:
            links.append('<link rel="apple-touch-icon" sizes="180x180" href="/assets/favicons/apple-touch-icon.png" />')
        
        # SVG
        if 'svg' in self._favicon_files:
            links.append('<link rel="icon" type="image/svg+xml" href="/assets/favicons/favicon.svg" />')
        
        return '\n'.join(links)

    def _render_pages(self):
        """
        Renders all pages for the site.
        """
        pages = self.site.pages.all()
        if not pages.exists():
            # Should we generate a default index?
            pass
        
        # Initialize PageSpeed optimizer if enabled
        pagespeed_optimizer = None
        if self.site.page_speed_optimization:
            pagespeed_optimizer = PageSpeedOptimizer(self.build_dir)

        for page in pages:
            # 1. Render Page Content (Blocks)
            content_html = ""
            for block in page.blocks.filter(is_active=True).order_by('order'):
                content_html += BlockRenderer.render_block(block)
            
            # 2. Prepare Context Data with ALL required variables
            site_data = {
                'brand_name': self.site.brand_name,
                'domain': self.site.domain,
                'language': self.site.language,
                'logo_url': self._logo_relative_path,
                'favicon_links': self._generate_favicon_links(),
                'affiliate_link': self.site.affiliate_link.url if self.site.affiliate_link else '#',
            }
            
            page_data = {
                'title': page.title,
                'description': page.description,
                'h1': page.h1_heading,
                'canonical_url': page.canonical_url or f"https://{self.site.domain}/{page.slug}.html",
                'content_html': content_html,
                'meta_title': page.meta_title or page.title,
                'meta_description': page.meta_description or page.description,
                'metadata': self._generate_metadata(page),
                'microdata': self._generate_microdata(page),
                'header_menu_html': self._generate_header_menu(),
                'footer_menu_html': self._generate_footer_menu(),
                'footer_images_html': self._generate_footer_images(),
                'styles_inline': self.site.custom_css or '',
                'scripts_inline': self.site.custom_js or '',
            }
            
            # Add Global Settings
            global_settings = {} 
            
            context = VariableContext(site_data, page_data, global_settings)
            
            # 3. Render Template
            if self.template:
                html_content = render_template(self.template, context)
            else:
                # Fallback if no template
                html_content = f"<html><body>{content_html}</body></html>"
            
            # 4. Apply PageSpeed Optimization (if enabled)
            if pagespeed_optimizer:
                try:
                    html_content = pagespeed_optimizer.optimize_html(html_content)
                except Exception as e:
                    print(f"Error applying PageSpeed optimization: {e}")
            
            # 5. Apply Fingerprinting to HTML
            # CSS Classes
            html_content = self.css_randomizer.apply_class_map(html_content, is_css=False)
            
            # CMS Footprints (Path remapping)
            html_content = self.footprint_manager.remap_paths(html_content)
            
            # 6. Inject Analytics (Umami)
            try:
                # Avoid circular import
                from analytics.models import UmamiConfig
                umami_config = UmamiConfig.objects.filter(site=self.site, is_active=True).first()
                
                if umami_config:
                    # Decrypt token if needed, but for the script we mainly need the website-id and src
                    # The standard Umami script is:
                    # <script defer src="{api_url}/script.js" data-website-id="{site_id}"></script>
                    
                    # Ensure api_url doesn't end with slash for cleaner URL construction, though usually browser handles it
                    api_url = umami_config.api_url.rstrip('/')
                    script_tag = f'<script defer src="{api_url}/script.js" data-website-id="{umami_config.umami_site_id}"></script>'
                    
                    # Inject before </head>
                    if '</head>' in html_content:
                        html_content = html_content.replace('</head>', f'{script_tag}\n</head>')
                    else:
                        # Fallback: inject at end
                        html_content += f"\n{script_tag}"
            except Exception as e:
                print(f"Error injecting Umami analytics: {e}")
                # Don't fail generation just because of analytics injection error
            
            # 7. Save to file
            filename = 'index.html' if page.slug == 'index' or page.slug == '' else f"{page.slug}.html"
            with open(os.path.join(self.build_dir, filename), 'w', encoding='utf-8') as f:
                f.write(html_content)

    def _package_site(self):
        """
        Zips the generated site.
        """
        zip_filename = f"{self.site.domain}_{self.build_id}.zip"
        zip_path = os.path.join(settings.MEDIA_ROOT, 'builds', zip_filename)
        
        # Ensure builds dir exists
        os.makedirs(os.path.dirname(zip_path), exist_ok=True)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.build_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, self.build_dir)
                    zipf.write(file_path, arcname)
                    
        return zip_path
