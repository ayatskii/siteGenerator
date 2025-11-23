import os
import requests
import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from django.conf import settings
from .models import MediaAsset

# Try to import cairosvg, handle if missing (Cairo library not installed on Windows)
try:
    import cairosvg
except (ImportError, OSError):
    cairosvg = None

class ImageProcessingService:
    """
    Enhanced image processing service with WebP conversion, responsive resizing,
    and comprehensive favicon generation.
    """
    
    @staticmethod
    def process_upload(file, asset_instance):
        """
        Extract metadata, convert SVGs, and optimize images on upload.
        """
        try:
            # Handle SVG
            if asset_instance.filename.lower().endswith('.svg'):
                if cairosvg:
                    # Convert SVG to PNG for preview/fallback
                    png_data = cairosvg.svg2png(file_obj=file)
                    img = Image.open(BytesIO(png_data))
                    asset_instance.width, asset_instance.height = img.size
                    asset_instance.format = 'SVG'
                    # Reset file pointer for saving if needed, though Django handles this
                    file.seek(0)
                else:
                    # Fallback if cairosvg not installed
                    asset_instance.format = 'SVG'
                    asset_instance.width = 0
                    asset_instance.height = 0
            else:
                # Handle Standard Images
                img = Image.open(file)
                asset_instance.width, asset_instance.height = img.size
                asset_instance.format = img.format
                
                # Resize logic: keep original as master, limit to 1920px
                if asset_instance.width > 1920:
                    ratio = 1920 / asset_instance.width
                    new_height = int(asset_instance.height * ratio)
                    img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                    
                    # Save back to a BytesIO object
                    output = BytesIO()
                    img.save(output, format=img.format)
                    output.seek(0)
            
            asset_instance.save()
            
        except Exception as e:
            print(f"Error processing image: {e}")

    @staticmethod
    def generate_responsive_variants(image_path, output_dir, base_filename):
        """
        Generate responsive image variants for PageSpeed optimization.
        Creates mobile (480px) and desktop (800px) versions in WebP and original format.
        
        Args:
            image_path: Path to original image
            output_dir: Directory to save variants
            base_filename: Base name for output files (without extension)
            
        Returns:
            dict: Paths to generated variants
        """
        os.makedirs(output_dir, exist_ok=True)
        
        variants = {
            'mobile': {},
            'desktop': {}
        }
        
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB for JPEG compatibility
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                
                original_format = img.format or 'PNG'
                ext = original_format.lower()
                
                # Generate mobile variant (480px width)
                mobile_width = 480
                if img.width > mobile_width:
                    ratio = mobile_width / img.width
                    mobile_height = int(img.height * ratio)
                    mobile_img = img.resize((mobile_width, mobile_height), Image.Resampling.LANCZOS)
                else:
                    mobile_img = img.copy()
                
                # Save mobile WebP
                mobile_webp_path = os.path.join(output_dir, f"{base_filename}_mobile.webp")
                mobile_img.save(mobile_webp_path, 'WEBP', quality=85)
                variants['mobile']['webp'] = mobile_webp_path
                
                # Save mobile original format
                mobile_orig_path = os.path.join(output_dir, f"{base_filename}_mobile.{ext}")
                mobile_img.save(mobile_orig_path, original_format, quality=90 if ext == 'jpg' else None)
                variants['mobile']['original'] = mobile_orig_path
                
                # Generate desktop variant (800px width)
                desktop_width = 800
                if img.width > desktop_width:
                    ratio = desktop_width / img.width
                    desktop_height = int(img.height * ratio)
                    desktop_img = img.resize((desktop_width, desktop_height), Image.Resampling.LANCZOS)
                else:
                    desktop_img = img.copy()
                
                # Save desktop WebP
                desktop_webp_path = os.path.join(output_dir, f"{base_filename}_desktop.webp")
                desktop_img.save(desktop_webp_path, 'WEBP', quality=85)
                variants['desktop']['webp'] = desktop_webp_path
                
                # Save desktop original format
                desktop_orig_path = os.path.join(output_dir, f"{base_filename}_desktop.{ext}")
                desktop_img.save(desktop_orig_path, original_format, quality=90 if ext == 'jpg' else None)
                variants['desktop']['original'] = desktop_orig_path
        
        except Exception as e:
            print(f"Error generating responsive variants: {e}")
            raise
        
        return variants

    @staticmethod
    def generate_favicons(svg_path, output_dir):
        """
        Generate comprehensive favicon package from SVG source.
        Creates ICO, PNG (multiple sizes), and copies SVG.
        
        Args:
            svg_path: Path to source SVG file
            output_dir: Directory to save favicons
            
        Returns:
            dict: Paths to all generated favicon files
        """
        if not cairosvg:
            raise Exception("cairosvg is required for favicon generation")
        
        os.makedirs(output_dir, exist_ok=True)
        
        favicon_files = {}
        
        try:
            # Read SVG content
            with open(svg_path, 'rb') as f:
                svg_content = f.read()
            
            # Generate PNG variants at different sizes
            sizes = [16, 32, 48, 180]  # 180 for apple-touch-icon
            
            for size in sizes:
                png_data = cairosvg.svg2png(
                    bytestring=svg_content,
                    output_width=size,
                    output_height=size
                )
                
                if size == 180:
                    # Apple touch icon
                    png_path = os.path.join(output_dir, 'apple-touch-icon.png')
                    favicon_files['apple_touch_icon'] = png_path
                else:
                    png_path = os.path.join(output_dir, f'favicon-{size}x{size}.png')
                    favicon_files[f'png_{size}'] = png_path
                
                with open(png_path, 'wb') as f:
                    f.write(png_data)
            
            # Generate ICO file (contains 16x16, 32x32, 48x48)
            ico_path = os.path.join(output_dir, 'favicon.ico')
            
            # Create ICO from PNG images
            images = []
            for size in [16, 32, 48]:
                png_data = cairosvg.svg2png(
                    bytestring=svg_content,
                    output_width=size,
                    output_height=size
                )
                images.append(Image.open(BytesIO(png_data)))
            
            # Save as ICO (Pillow supports multi-size ICO)
            images[0].save(
                ico_path,
                format='ICO',
                sizes=[(16, 16), (32, 32), (48, 48)],
                append_images=images[1:]
            )
            favicon_files['ico'] = ico_path
            
            # Copy original SVG
            svg_dest_path = os.path.join(output_dir, 'favicon.svg')
            with open(svg_dest_path, 'wb') as f:
                f.write(svg_content)
            favicon_files['svg'] = svg_dest_path
            
        except Exception as e:
            print(f"Error generating favicons: {e}")
            raise
        
        return favicon_files

    @staticmethod
    def convert_to_webp(image_path, output_path=None, quality=85):
        """
        Convert an image to WebP format.
        
        Args:
            image_path: Path to source image
            output_path: Path for output WebP (optional, defaults to same name with .webp)
            quality: WebP quality (0-100)
            
        Returns:
            str: Path to generated WebP file
        """
        if output_path is None:
            base = os.path.splitext(image_path)[0]
            output_path = f"{base}.webp"
        
        try:
            with Image.open(image_path) as img:
                # Convert RGBA to RGB if necessary
                if img.mode == 'RGBA':
                    rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                    rgb_img.paste(img, mask=img.split()[3])
                    img = rgb_img
                
                img.save(output_path, 'WEBP', quality=quality)
                
        except Exception as e:
            print(f"Error converting to WebP: {e}")
            raise
        
        return output_path

    @staticmethod
    def upload_from_url(url, folder, owner):
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            filename = os.path.basename(url.split('?')[0])
            if not filename:
                filename = "downloaded_image.jpg"
                
            content = ContentFile(response.content)
            
            asset = MediaAsset(
                file=content,
                filename=filename,
                folder=folder,
                owner=owner
            )
            # File needs to be saved to trigger storage
            asset.file.save(filename, content, save=False)
            asset.save()
            
            ImageProcessingService.process_upload(asset.file, asset)
            return asset
        except Exception as e:
            raise Exception(f"Failed to download image: {str(e)}")

    @staticmethod
    def upload_from_base64(data, filename, folder, owner):
        try:
            if 'base64,' in data:
                format, imgstr = data.split(';base64,') 
                ext = format.split('/')[-1]
            else:
                imgstr = data
                ext = 'png' # Default
                
            decoded = base64.b64decode(imgstr)
            content = ContentFile(decoded)
            
            if not filename.endswith(f".{ext}"):
                filename = f"{filename}.{ext}"
                
            asset = MediaAsset(
                file=content,
                filename=filename,
                folder=folder,
                owner=owner
            )
            asset.file.save(filename, content, save=False)
            asset.save()
            
            ImageProcessingService.process_upload(asset.file, asset)
            return asset
        except Exception as e:
            raise Exception(f"Failed to process base64 image: {str(e)}")

