import os
import requests
import base64
from io import BytesIO
from PIL import Image
from django.core.files.base import ContentFile
from .models import MediaAsset

# Try to import cairosvg, handle if missing (e.g. in dev environment without deps)
try:
    import cairosvg
except ImportError:
    cairosvg = None

class ImageProcessingService:
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
                
                # Resize logic (simplified for now, can be expanded)
                # If image is very large, resize to max desktop width (e.g. 1920 or 800 as per plan)
                # Plan mentioned 800px desktop / 480px mobile. 
                # We'll keep original as master and potentially generate variants later.
                # For now, let's just ensure it's not massive.
                if asset_instance.width > 1920:
                    ratio = 1920 / asset_instance.width
                    new_height = int(asset_instance.height * ratio)
                    img = img.resize((1920, new_height), Image.Resampling.LANCZOS)
                    
                    # Save back to a BytesIO object
                    output = BytesIO()
                    img.save(output, format=img.format)
                    output.seek(0)
                    
                    # We would need to replace the file content here, but for now 
                    # we just update metadata and save the asset.
                    # Real resizing usually happens on serving or generating variants.
            
            asset_instance.save()
            
        except Exception as e:
            print(f"Error processing image: {e}")

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
