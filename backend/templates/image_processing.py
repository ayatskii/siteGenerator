import os
import random
from PIL import Image
from io import BytesIO

class ImageFingerprinter:
    """
    Handles image fingerprinting by varying size, quality, and stripping metadata.
    """
    def __init__(self, seed: str):
        self.rng = random.Random(seed)

    def process_image(self, image_path: str, output_path: str):
        """
        Process an image to apply fingerprinting variations.
        """
        try:
            with Image.open(image_path) as img:
                # 1. Strip Metadata
                # We do this by creating a new image and copying data
                data = list(img.getdata())
                image_without_exif = Image.new(img.mode, img.size)
                image_without_exif.putdata(data)
                
                # 2. Resize Variation (+/- 1-2%)
                width, height = image_without_exif.size
                variation = self.rng.uniform(0.98, 1.02)
                new_width = int(width * variation)
                new_height = int(height * variation)
                
                # Ensure we don't distort too much or make it too small
                if new_width < 10 or new_height < 10:
                    new_width, new_height = width, height
                elif new_width == width and new_height == height:
                    # Force at least 1px change if random variation resulted in same size
                    if self.rng.choice([True, False]):
                        new_width += 1
                    else:
                        new_width -= 1
                    
                resized_img = image_without_exif.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 3. Compression Variation
                quality = self.rng.randint(80, 95)
                
                # Save
                # Determine format from extension
                ext = os.path.splitext(output_path)[1].lower()
                if ext in ['.jpg', '.jpeg']:
                    resized_img.save(output_path, 'JPEG', quality=quality, optimize=True)
                elif ext == '.png':
                    # PNG doesn't use quality in the same way, but we can use optimize
                    resized_img.save(output_path, 'PNG', optimize=True)
                elif ext == '.webp':
                    resized_img.save(output_path, 'WEBP', quality=quality)
                else:
                    # Fallback for others
                    resized_img.save(output_path)
                    
        except Exception as e:
            print(f"Error processing image {image_path}: {e}")
            # Fallback: just copy the file if processing fails
            # In a real app, we might want to log this properly
            import shutil
            shutil.copy2(image_path, output_path)
