from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Template, TemplateSection, TemplateVariable

class TemplateModelTest(TestCase):
    def test_create_monolithic_template(self):
        template = Template.objects.create(
            name="Mono Template",
            type="MONOLITHIC",
            content="<html><body>{{CONTENT}}</body></html>"
        )
        self.assertEqual(template.name, "Mono Template")
        self.assertEqual(template.type, "MONOLITHIC")

    def test_create_sectional_template(self):
        template = Template.objects.create(
            name="Sectional Template",
            type="SECTIONAL"
        )
        section = TemplateSection.objects.create(
            template=template,
            name="Header",
            content="<header>...</header>",
            order=1
        )
        self.assertEqual(section.template, template)
        self.assertEqual(section.name, "Header")

class TemplateAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.template_data = {
            "name": "API Template",
            "type": "MONOLITHIC",
            "content": "<div>Content</div>"
        }

    def test_create_template_api(self):
        response = self.client.post('/api/templates/', self.template_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Template.objects.count(), 1)
        self.assertEqual(Template.objects.get().name, "API Template")

    def test_get_templates_api(self):
        Template.objects.create(**self.template_data)
        response = self.client.get('/api/templates/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
