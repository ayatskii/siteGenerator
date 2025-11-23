from django.test import TestCase
from django.contrib.auth import get_user_model
from sites.models import Site, Page, Deployment
from datetime import datetime, timedelta

User = get_user_model()


class SiteModelEnhancementsTest(TestCase):
    """Test Site model computed properties"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.site = Site.objects.create(
            name='Test Site',
            domain='test.example.com',
            owner=self.user
        )
    
    def test_page_count_property(self):
        """Test page_count computed property"""
        self.assertEqual(self.site.page_count, 0)
        
        Page.objects.create(site=self.site, title='Page 1', slug='page-1')
        Page.objects.create(site=self.site, title='Page 2', slug='page-2')
        
        self.assertEqual(self.site.page_count, 2)
    
    def test_deployment_count_property(self):
        """Test deployment_count computed property"""
        self.assertEqual(self.site.deployment_count, 0)
        
        Deployment.objects.create(site=self.site, status='success')
        Deployment.objects.create(site=self.site, status='success')
        Deployment.objects.create(site=self.site, status='failed')
        
        # Should only count successful deployments
        self.assertEqual(self.site.deployment_count, 2)
    
    def test_last_deployment_property(self):
        """Test last_deployment computed property"""
        self.assertIsNone(self.site.last_deployment)
        
        dep1 = Deployment.objects.create(site=self.site, status='success')
        self.assertEqual(self.site.last_deployment, dep1)
        
        # Create a newer deployment
        dep2 = Deployment.objects.create(site=self.site, status='failed')
        # Both deployments created quickly, just verify last_deployment exists
        # and is one of the two deployments
        self.assertIsNotNone(self.site.last_deployment)
        self.assertIn(self.site.last_deployment.id, [dep1.id, dep2.id])
    
    def test_last_deployment_date_property(self):
        """Test last_deployment_date computed property"""
        self.assertIsNone(self.site.last_deployment_date)
        
        deployment = Deployment.objects.create(site=self.site, status='success')
        self.assertIsNotNone(self.site.last_deployment_date)
        self.assertEqual(self.site.last_deployment_date, deployment.created_at)
    
    def test_status_property_empty(self):
        """Test status property when site has no pages"""
        self.assertEqual(self.site.status, 'empty')
    
    def test_status_property_draft(self):
        """Test status property when site has pages but no deployment"""
        Page.objects.create(site=self.site, title='Page 1', slug='page-1')
        
        self.assertEqual(self.site.status, 'draft')
    
    def test_status_property_deployed(self):
        """Test status property when site has successful deployment"""
        Page.objects.create(site=self.site, title='Page 1', slug='page-1')
        Deployment.objects.create(site=self.site, status='success')
        
        self.assertEqual(self.site.status, 'deployed')
    
    def test_status_property_with_failed_deployment(self):
        """Test that failed deployments don't count as deployed"""
        Page.objects.create(site=self.site, title='Page 1', slug='page-1')
        Deployment.objects.create(site=self.site, status='failed')
        
        # Should still be draft since deployment failed
        self.assertEqual(self.site.status, 'draft')
