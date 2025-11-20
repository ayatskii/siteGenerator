import os
import shutil
import json
import zipfile
from django.test import TestCase, override_settings
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from .models import Template, TemplateSection

@override_settings(MEDIA_URL='/media/', MEDIA_ROOT=os.path.join(settings.BASE_DIR, 'media_test'))
class TemplateUploadTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.temp_test_dir = os.path.join(settings.MEDIA_ROOT, 'test_temp')
        os.makedirs(self.temp_test_dir, exist_ok=True)

    def tearDown(self):
        if os.path.exists(self.temp_test_dir):
            shutil.rmtree(self.temp_test_dir)
        
        # Clean up created template assets
        template_assets = os.path.join(settings.MEDIA_ROOT, 'templates')
        if os.path.exists(template_assets):
            shutil.rmtree(template_assets)

    def create_zip(self, files):
        zip_path = os.path.join(self.temp_test_dir, 'test.zip')
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for filename, content in files.items():
                zipf.writestr(filename, content)
        return zip_path

    def test_upload_monolithic_valid(self):
        config = {
            "name": "Mono Test",
            "type": "MONOLITHIC",
            "description": "Test Desc"
        }
        files = {
            "config.json": json.dumps(config),
            "index.html": "<html><body><img src='assets/img.jpg'></body></html>",
            "assets/img.jpg": "fake image content"
        }
        zip_path = self.create_zip(files)
        
        with open(zip_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile("test.zip", f.read(), content_type="application/zip")
            response = self.client.post('/api/templates/upload/', {'file': uploaded_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Template.objects.count(), 1)
        template = Template.objects.first()
        self.assertEqual(template.name, "Mono Test")
        self.assertEqual(template.type, "MONOLITHIC")
        # Check if asset path was rewritten correctly
        self.assertIn("/media/templates/mono-test/assets/", template.content)

    def test_upload_sectional_valid(self):
        config = {
            "name": "Sect Test",
            "type": "SECTIONAL",
            "sections": [
                {"name": "Header", "file": "sections/header.html", "order": 1},
                {"name": "Footer", "file": "sections/footer.html", "order": 2}
            ]
        }
        files = {
            "config.json": json.dumps(config),
            "base.html": "<div>{{CONTENT}}</div>",
            "sections/header.html": "<header>Head</header>",
            "sections/footer.html": "<footer>Foot</footer>"
        }
        zip_path = self.create_zip(files)

        with open(zip_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile("test.zip", f.read(), content_type="application/zip")
            response = self.client.post('/api/templates/upload/', {'file': uploaded_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(TemplateSection.objects.count(), 2)

    def test_upload_invalid_zip(self):
        files = {"index.html": "missing config"}
        zip_path = self.create_zip(files)

        with open(zip_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile("test.zip", f.read(), content_type="application/zip")
            response = self.client.post('/api/templates/upload/', {'file': uploaded_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_forbidden_file(self):
        config = {"name": "Bad", "type": "MONOLITHIC"}
        files = {
            "config.json": json.dumps(config),
            "index.html": "html",
            "assets/hack.php": "<?php echo 'hack'; ?>"
        }
        zip_path = self.create_zip(files)

        with open(zip_path, 'rb') as f:
            uploaded_file = SimpleUploadedFile("test.zip", f.read(), content_type="application/zip")
            response = self.client.post('/api/templates/upload/', {'file': uploaded_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Forbidden file type", str(response.data))
