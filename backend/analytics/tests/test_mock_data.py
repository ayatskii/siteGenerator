from django.test import TestCase
from analytics.utils.mock_data import MockAnalyticsData


class MockAnalyticsDataTest(TestCase):
    """Test mock analytics data generation"""
    
    def test_generate_page_views(self):
        """Test page views generation"""
        data = MockAnalyticsData.generate_page_views(days=7)
        
        self.assertEqual(len(data), 7)
        for entry in data:
            self.assertIn('date', entry)
            self.assertIn('views', entry)
            self.assertIn('unique_visitors', entry)
            self.assertGreater(entry['views'], 0)
            self.assertGreater(entry['unique_visitors'], 0)
            # Visitors should be less than views
            self.assertLessEqual(entry['unique_visitors'], entry['views'])
    
    def test_generate_page_views_with_seed(self):
        """Test that same seed produces same data"""
        data1 = MockAnalyticsData.generate_page_views(days=5, seed=12345)
        data2 = MockAnalyticsData.generate_page_views(days=5, seed=12345)
        
        self.assertEqual(data1, data2)
    
    def test_generate_visitors(self):
        """Test visitor statistics generation"""
        data = MockAnalyticsData.generate_visitors(days=30)
        
        self.assertIn('total_page_views', data)
        self.assertIn('unique_visitors', data)
        self.assertIn('previous_period', data)
        self.assertIn('change_percentage', data)
        
        self.assertGreater(data['total_page_views'], 0)
        self.assertGreater(data['unique_visitors'], 0)
        self.assertIn('views', data['change_percentage'])
        self.assertIn('visitors', data['change_percentage'])
    
    def test_generate_top_pages(self):
        """Test top pages generation"""
        data = MockAnalyticsData.generate_top_pages(limit=5)
        
        self.assertEqual(len(data), 5)
        for page in data:
            self.assertIn('path', page)
            self.assertIn('title', page)
            self.assertIn('views', page)
            self.assertIn('unique_visitors', page)
        
        # Pages should be sorted by views descending
        for i in range(len(data) - 1):
            self.assertGreaterEqual(data[i]['views'], data[i + 1]['views'])
    
    def test_generate_traffic_sources(self):
        """Test traffic sources generation"""
        data = MockAnalyticsData.generate_traffic_sources()
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check percentages sum to 100
        total_percentage = sum(s['percentage'] for s in data)
        self.assertEqual(total_percentage, 100)
        
        # Check all required fields
        for source in data:
            self.assertIn('name', source)
            self.assertIn('percentage', source)
            self.assertIn('visitors', source)
            self.assertIn('color', source)
    
    def test_generate_device_breakdown(self):
        """Test device breakdown generation"""
        data = MockAnalyticsData.generate_device_breakdown()
        
        self.assertIn('devices', data)
        self.assertIn('browsers', data)
        self.assertIn('operating_systems', data)
        
        # Check device percentages sum to approximately 100
        device_total = sum(data['devices'].values())
        self.assertGreaterEqual(device_total, 99.5)
        self.assertLessEqual(device_total, 100.5)
        
        # Check browsers
        self.assertIn('Chrome', data['browsers'])
        self.assertIn('Safari', data['browsers'])
        
        # Check OS
        self.assertIn('Windows', data['operating_systems'])
        self.assertIn('macOS', data['operating_systems'])
    
    def test_generate_geographic_data(self):
        """Test geographic data generation"""
        data = MockAnalyticsData.generate_geographic_data()
        
        self.assertIsInstance(data, list)
        self.assertGreater(len(data), 0)
        
        # Check percentages sum to 100
        total_percentage = sum(c['percentage'] for c in data)
        self.assertEqual(total_percentage, 100)
        
        for country in data:
            self.assertIn('code', country)
            self.assertIn('name', country)
            self.assertIn('percentage', country)
            self.assertIn('visitors', country)
    
    def test_generate_bounce_rate(self):
        """Test bounce rate generation"""
        rate = MockAnalyticsData.generate_bounce_rate()
        
        self.assertIsInstance(rate, float)
        self.assertGreaterEqual(rate, 35.0)
        self.assertLessEqual(rate, 65.0)
    
    def test_generate_avg_session_duration(self):
        """Test session duration generation"""
        duration = MockAnalyticsData.generate_avg_session_duration()
        
        self.assertIsInstance(duration, int)
        self.assertGreaterEqual(duration, 120)
        self.assertLessEqual(duration, 300)
    
    def test_get_full_analytics(self):
        """Test full analytics generation"""
        data = MockAnalyticsData.get_full_analytics(days=7)
        
        self.assertIn('page_views_timeline', data)
        self.assertIn('visitors_summary', data)
        self.assertIn('top_pages', data)
        self.assertIn('traffic_sources', data)
        self.assertIn('device_breakdown', data)
        self.assertIn('geographic_data', data)
        self.assertIn('bounce_rate', data)
        self.assertIn('avg_session_duration', data)
        
        # Verify page_views_timeline has correct number of days
        self.assertEqual(len(data['page_views_timeline']), 7)
    
    def test_get_color_for_source(self):
        """Test color assignment for traffic sources"""
        color_direct = MockAnalyticsData._get_color_for_source('Direct')
        color_google = MockAnalyticsData._get_color_for_source('Google')
        color_unknown = MockAnalyticsData._get_color_for_source('Unknown')
        
        self.assertIsInstance(color_direct, str)
        self.assertTrue(color_direct.startswith('#'))
        self.assertIsInstance(color_google, str)
        self.assertTrue(color_google.startswith('#'))
        self.assertIsInstance(color_unknown, str)
