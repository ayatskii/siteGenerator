from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from sites.models import Site, Page, Deployment
from analytics.models import UmamiConfig
from datetime import datetime, timedelta

User = get_user_model()


class AnalyticsAPITest(TestCase):
    """Test analytics API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
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
        self.client.force_authenticate(user=self.user)
    
    def test_get_analytics_for_site(self):
        """Test getting analytics data for a site"""
        response = self.client.get(f'/api/analytics/sites/{self.site.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('page_views_timeline', response.data)
        self.assertIn('visitors_summary', response.data)
        self.assertIn('top_pages', response.data)
        self.assertIn('traffic_sources', response.data)
        self.assertIn('device_breakdown', response.data)
        self.assertIn('geographic_data', response.data)
    
    def test_get_analytics_with_date_range(self):
        """Test analytics with custom date range"""
        start_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        response = self.client.get(
            f'/api/analytics/sites/{self.site.id}/',
            {'start_date': start_date, 'end_date': end_date}
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Should have 8 days (inclusive)
        self.assertEqual(len(response.data['page_views_timeline']), 8)
    
    def test_get_analytics_summary(self):
        """Test getting analytics summary"""
        response = self.client.get(f'/api/analytics/sites/{self.site.id}/summary/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_page_views', response.data)
        self.assertIn('unique_visitors', response.data)
        self.assertIn('bounce_rate', response.data)
        self.assertIn('avg_session_duration', response.data)
        self.assertIn('change_from_previous', response.data)
        self.assertIn('period', response.data)
    
    def test_get_analytics_nonexistent_site(self):
        """Test getting analytics for non-existent site"""
        response = self.client.get('/api/analytics/sites/99999/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_analytics_requires_authentication(self):
        """Test that analytics endpoints require authentication"""
        self.client.force_authenticate(user=None)
        
        response = self.client.get(f'/api/analytics/sites/{self.site.id}/')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SiteStatisticsAPITest(TestCase):
    """Test site statistics API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create multiple sites
        self.site1 = Site.objects.create(
            name='Site 1',
            domain='site1.example.com',
            owner=self.user
        )
        self.site2 = Site.objects.create(
            name='Site 2',
            domain='site2.example.com',
            owner=self.user
        )
        
        # Create pages
        Page.objects.create(site=self.site1, title='Home', slug='home')
        Page.objects.create(site=self.site1, title='About', slug='about')
        Page.objects.create(site=self.site2, title='Home', slug='home')
        
        # Create deployment
        Deployment.objects.create(
            site=self.site1,
            status='success'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_get_dashboard_statistics(self):
        """Test getting dashboard statistics"""
        response = self.client.get('/api/sites/sites/statistics/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sites'], 2)
        self.assertEqual(response.data['sites_deployed'], 1)
        self.assertEqual(response.data['total_pages'], 3)
        self.assertIn('storage_used', response.data)
    
    def test_statistics_only_show_user_sites(self):
        """Test that statistics only show sites owned by the user"""
        other_user = User.objects.create_user(
            username='other',
            email='other@example.com',
            password='pass123'
        )
        Site.objects.create(
            name='Other Site',
            domain='other.example.com',
            owner=other_user
        )
        
        response = self.client.get('/api/sites/sites/statistics/')
        
        # Should still only show 2 sites (user's sites)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['total_sites'], 2)


class SiteListFilteredAPITest(TestCase):
    """Test site list with filtering"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create sites with different attributes
        self.site1 = Site.objects.create(
            name='English Site',
            domain='en.example.com',
            owner=self.user,
            language='en-US',
            brand_name='Brand A'
        )
        self.site2 = Site.objects.create(
            name='French Site',
            domain='fr.example.com',
            owner=self.user,
            language='fr-FR',
            brand_name='Brand B'
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_get_filtered_site_list(self):
        """Test getting site list"""
        response = self.client.get('/api/sites/sites/list_filtered/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
    
    def test_filter_by_language(self):
        """Test filtering by language"""
        response = self.client.get('/api/sites/sites/list_filtered/?language=en-US')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['domain'], 'en.example.com')
    
    def test_filter_by_brand(self):
        """Test filtering by brand name"""
        response = self.client.get('/api/sites/sites/list_filtered/?brand=Brand A')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['brand_name'], 'Brand A')
    
    def test_search_by_domain(self):
        """Test searching by domain"""
        response = self.client.get('/api/sites/sites/list_filtered/?search=fr.example')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['domain'], 'fr.example.com')


class SiteDuplicationAPITest(TestCase):
    """Test site duplication endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.site = Site.objects.create(
            name='Original Site',
            domain='original.example.com',
            owner=self.user,
            language='en-US',
            brand_name='My Brand'
        )
        
        # Create pages and blocks
        self.page = Page.objects.create(
            site=self.site,
            title='Home Page',
            slug='home',
            description='Homepage description'
        )
        
        from sites.models import Block
        Block.objects.create(
            page=self.page,
            type='hero',
            order=0,
            content={'title': 'Welcome'}
        )
        
        self.client.force_authenticate(user=self.user)
    
    def test_duplicate_site(self):
        """Test duplicating a site"""
        response = self.client.post(f'/api/sites/sites/{self.site.id}/duplicate/')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('domain', response.data)
        self.assertTrue(response.data['domain'].startswith('original.example.com-copy'))
        self.assertEqual(response.data['brand_name'], 'My Brand')
        
        # Verify new site was created
        new_site = Site.objects.get(domain=response.data['domain'])
        self.assertEqual(new_site.pages.count(), 1)
        self.assertEqual(new_site.pages.first().blocks.count(), 1)
    
    def test_duplicate_site_multiple_times(self):
        """Test duplicating the same site multiple times"""
        # First duplication
        response1 = self.client.post(f'/api/sites/sites/{self.site.id}/duplicate/')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Second duplication - should get different domain
        response2 = self.client.post(f'/api/sites/sites/{self.site.id}/duplicate/')
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Domains should be different
        self.assertNotEqual(response1.data['domain'], response2.data['domain'])
    
    def test_duplicate_nonexistent_site(self):
        """Test duplicating a non-existent site"""
        response = self.client.post('/api/sites/sites/99999/duplicate/')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
