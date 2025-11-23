"""
PageSpeed Optimization Service for Site Generator

Handles HTML optimization by:
- Replacing <img> tags with <picture> tags
- Adding responsive image variants (mobile/desktop)
- Converting images to WebP format with fallbacks
- Adding lazy loading attributes
"""

import os
import re
from bs4 import BeautifulSoup
from media_library.services import ImageProcessingService


class PageSpeedOptimizer:
    """
    Optimizes HTML for PageSpeed by transforming images to responsive <picture> elements.
    """
    
    def __init__(self, build_dir, assets_url_prefix='/assets/'):
        """
        Args:
            build_dir: Root directory of the build (where assets folder is)
            assets_url_prefix: URL prefix for assets (e.g., '/assets/' or 'assets/')
        """
        self.build_dir = build_dir
        self.assets_dir = os.path.join(build_dir, 'assets')
        self.images_dir = os.path.join(self.assets_dir, 'images')
        self.assets_url_prefix = assets_url_prefix.rstrip('/') + '/'
    
    def optimize_html(self, html_content):
        """
        Parse HTML and replace all <img> tags with optimized <picture> tags.
        
        Args:
            html_content: String containing HTML
            
        Returns:
            str: Optimized HTML
        """
        if not html_content:
            return html_content
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all <img> tags
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src')
            if not src:
                continue
            
            # Skip external images and SVGs
            if src.startswith(('http://', 'https://', 'data:')) or src.endswith('.svg'):
                continue
            
            # Process the image and replace tag
            try:
                picture_tag = self._create_picture_tag(img, src, soup)
                if picture_tag:
                    img.replace_with(picture_tag)
            except Exception as e:
                print(f"Error optimizing image {src}: {e}")
                # Keep original <img> tag if optimization fails
                continue
        
        return str(soup)
    
    def _create_picture_tag(self, original_img, src, soup):
        """
        Create a <picture> tag with responsive sources from an <img> tag.
        
        Args:
            original_img: BeautifulSoup img tag
            src: Source URL of the image
            soup: BeautifulSoup object for creating new tags
            
        Returns:
            BeautifulSoup picture tag or None
        """
        # Determine the image path in the build directory
        # src might be: "assets/images/hero.jpg" or "/assets/images/hero.jpg"
        src_path = src.lstrip('/')
        image_path = os.path.join(self.build_dir, src_path)
        
        if not os.path.exists(image_path):
            print(f"Image not found: {image_path}")
            return None
        
        # Generate responsive variants
        base_name = os.path.splitext(os.path.basename(image_path))[0]
        output_dir = os.path.dirname(image_path)
        
        try:
            variants = ImageProcessingService.generate_responsive_variants(
                image_path, output_dir, base_name
            )
        except Exception as e:
            print(f"Failed to generate variants for {image_path}: {e}")
            return None
        
        # Build relative paths for the variants
        rel_dir = os.path.relpath(output_dir, self.build_dir)
        
        # Create <picture> element
        picture = soup.new_tag('picture')
        
        # Add WebP sources (best quality, modern format)
        # Desktop WebP (min-width: 768px)
        desktop_webp_rel = os.path.join(rel_dir, os.path.basename(variants['desktop']['webp']))
        desktop_webp_url = desktop_webp_rel.replace('\\', '/')
        source_desk_webp = soup.new_tag(
            'source',
            srcset=desktop_webp_url,
            type='image/webp',
            media='(min-width: 768px)'
        )
        picture.append(source_desk_webp)
        
        # Mobile WebP (default for smaller screens)
        mobile_webp_rel = os.path.join(rel_dir, os.path.basename(variants['mobile']['webp']))
        mobile_webp_url = mobile_webp_rel.replace('\\', '/')
        source_mob_webp = soup.new_tag(
            'source',
            srcset=mobile_webp_url,
            type='image/webp'
        )
        picture.append(source_mob_webp)
        
        # Add original format sources (fallback for browsers without WebP)
        # Desktop original
        desktop_orig_rel = os.path.join(rel_dir, os.path.basename(variants['desktop']['original']))
        desktop_orig_url = desktop_orig_rel.replace('\\', '/')
        source_desk_orig = soup.new_tag(
            'source',
            srcset=desktop_orig_url,
            media='(min-width: 768px)'
        )
        picture.append(source_desk_orig)
        
        # Mobile original (fallback)
        mobile_orig_rel = os.path.join(rel_dir, os.path.basename(variants['mobile']['original']))
        mobile_orig_url = mobile_orig_rel.replace('\\', '/')
        
        # Create fallback <img> tag
        fallback_img = soup.new_tag('img', src=mobile_orig_url)
        
        # Copy attributes from original img (alt, class, etc.)
        for attr, value in original_img.attrs.items():
            if attr != 'src':  # Don't copy src, we already set it
                fallback_img[attr] = value
        
        # Add loading="lazy" for performance
        fallback_img['loading'] = 'lazy'
        
        picture.append(fallback_img)
        
        return picture
