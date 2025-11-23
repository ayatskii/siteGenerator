from django.test import TestCase
from django.contrib.auth import get_user_model
from sites.models import Site
from analytics.models import UmamiConfig, AnalyticsCache
from datetime import date

User = get_user_model()


class UmamiConfigModelTest(TestCase):
    """Test UmamiConfig model"""
    
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
    
    def test_create_umami_config(self):
        """Test creating Umami configuration"""
        config = UmamiConfig.objects.create(
            site=self.site,
            api_url='https://umami.example.com/api',
            api_token='test-token-123',
            umami_site_id='site-id-123',
            is_active=True
        )
        
        self.assertEqual(config.site, self.site)
        self.assertEqual(config.api_url, 'https://umami.example.com/api')
        self.assertEqual(config.umami_site_id, 'site-id-123')
        self.assertTrue(config.is_active)
        self.assertIsNotNone(config.created_at)
    
    def test_umami_config_str(self):
        """Test string representation"""
        config = UmamiConfig.objects.create(
            site=self.site,
            api_url='https://umami.example.com/api',
            api_token='test-token',
            umami_site_id='site-123'
        )
        
        self.assertEqual(str(config), f"Umami Config for {self.site.domain}")
    
    def test_one_config_per_site(self):
        """Test that only one config can exist per site"""
        UmamiConfig.objects.create(
            site=self.site,
            api_url='https://umami.example.com/api',
            api_token='token1',
            umami_site_id='site-1'
        )
        
        # Creating a second config for the same site should fail
        with self.assertRaises(Exception):
            UmamiConfig.objects.create(
                site=self.site,
                api_url='https://umami2.example.com/api',
                api_token='token2',
                umami_site_id='site-2'
            )


class AnalyticsCacheModelTest(TestCase):
    """Test AnalyticsCache model"""
    
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
    
    def test_create_analytics_cache(self):
        """Test creating analytics cache entry"""
        cache = AnalyticsCache.objects.create(
            site=self.site,
            date=date(2025, 11, 22),
            page_views=1500,
            unique_visitors=800,
            bounce_rate=45.5,
            avg_session_duration=180,
            top_pages=[
                {'path': '/', 'views': 500},
                {'path': '/about', 'views': 300}
            ],
            traffic_sources=[
                {'name': 'Direct', 'percentage': 40}
            ],
            device_breakdown={
                'mobile': 55,
                'desktop': 40,
                'tablet': 5
            },
            geographic_data={
                'US': 60,
                'UK': 20,
                'Other': 20
            }
        )
        
        self.assertEqual(cache.page_views, 1500)
        self.assertEqual(cache.unique_visitors, 800)
        self.assertEqual(cache.bounce_rate, 45.5)
        self.assertEqual(len(cache.top_pages), 2)
        self.assertIn('mobile', cache.device_breakdown)
    
    def test_analytics_cache_ordering(self):
        """Test that cache entries are ordered by date descending"""
        AnalyticsCache.objects.create(
            site=self.site,
            date=date(2025, 11, 20),
            page_views=1000,
            unique_visitors=500
        )
        cache2 = AnalyticsCache.objects.create(
            site=self.site,
            date=date(2025, 11, 22),
            page_views=1500,
            unique_visitors=800
        )
        
        # Most recent should be first
        first = AnalyticsCache.objects.first()
        self.assertEqual(first.page_views, 1500)
        self.assertEqual(first.date, date(2025, 11, 22))
    
    def test_unique_together_site_date(self):
        """Test that site and date combination must be unique"""
        AnalyticsCache.objects.create(
            site=self.site,
            date=date(2025, 11, 22),
            page_views=1000,
            unique_visitors=500
        )
        
        # Creating another entry for the same site and date should fail
        with self.assertRaises(Exception):
            AnalyticsCache.objects.create(
                site=self.site,
                date=date(2025, 11, 22),
                page_views=2000,
                unique_visitors=1000
            )
