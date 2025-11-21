from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from api.models import User
from sites.models import Site
from .models import MediaFolder, MediaAsset, MediaAssetSiteData
from PIL import Image
import io

class MediaLibraryIntegrationTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            name="Test User",
            email="test@example.com",
            password="password123"
        )
        self.site = Site.objects.create(
            name="Test Site",
            domain="test.com",
            owner=self.user
        )
        
        # Create a dummy image
        self.image_file = io.BytesIO()
        image = Image.new('RGB', (100, 100), color='red')
        image.save(self.image_file, format='PNG')
        self.image_file.seek(0)

    def test_folder_hierarchy(self):
        """Test creating nested folders"""
        root_folder = MediaFolder.objects.create(name="Root", owner=self.user)
        child_folder = MediaFolder.objects.create(name="Child", parent=root_folder, owner=self.user)
        
        self.assertEqual(child_folder.parent, root_folder)
        self.assertIn(child_folder, root_folder.subfolders.all())

    def test_asset_upload_and_processing(self):
        """Test uploading an asset and checking metadata extraction"""
        uploaded_file = SimpleUploadedFile(
            name='test_image.png',
            content=self.image_file.getvalue(),
            content_type='image/png'
        )
        
        asset = MediaAsset.objects.create(
            file=uploaded_file,
            owner=self.user
        )
        
        # Check if metadata was extracted (via save method or signal if we had one, 
        # but here we rely on the view/service usually. 
        # In models.py save() only sets size and filename.
        # Width/Height/Format are set by ImageProcessingService which we should call or test separately.
        
        # Let's test the service directly here
        from .services import ImageProcessingService
        ImageProcessingService.process_upload(asset.file, asset)
        
        self.assertEqual(asset.width, 100)
        self.assertEqual(asset.height, 100)
        self.assertEqual(asset.format, 'PNG')

    def test_per_site_metadata(self):
        """Test adding site-specific metadata to an asset"""
        asset = MediaAsset.objects.create(
            filename="test.png",
            size=1024,
            owner=self.user
        )
        
        site_data = MediaAssetSiteData.objects.create(
            asset=asset,
            site=self.site,
            alt_text="Test Alt Text",
            title="Test Title"
        )
        
        self.assertEqual(site_data.alt_text, "Test Alt Text")
        self.assertEqual(asset.site_data.first().alt_text, "Test Alt Text")
