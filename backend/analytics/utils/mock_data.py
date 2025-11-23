import random
from datetime import datetime, timedelta
from typing import Dict, List, Any


class MockAnalyticsData:
    """
    Generate realistic mock analytics data for testing and development.
    Used when a site doesn't have Umami configured.
    """
    
    @staticmethod
    def generate_page_views(days: int = 30, seed: int = None) -> List[Dict[str, Any]]:
        """Generate daily page view data with realistic trends."""
        if seed:
            random.seed(seed)
        
        data = []
        base_views = random.randint(500, 2000)
        
        for i in range(days):
            date = datetime.now() - timedelta(days=days - i - 1)
            # Add some variance and trending
            trend = i * 5  # Slight upward trend
            variance = random.randint(-100, 150)
            views = max(base_views + trend + variance, 100)
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'views': views,
                'unique_visitors': int(views * random.uniform(0.6, 0.8))
            })
        
        return data
    
    @staticmethod
    def generate_visitors(days: int = 30) -> Dict[str, Any]:
        """Generate visitor statistics."""
        page_views_data = MockAnalyticsData.generate_page_views(days)
        
        total_views = sum(d['views'] for d in page_views_data)
        total_unique = sum(d['unique_visitors'] for d in page_views_data)
        
        # Previous period comparison
        prev_period_views = int(total_views * random.uniform(0.8, 1.2))
        prev_period_unique = int(total_unique * random.uniform(0.8, 1.2))
        
        return {
            'total_page_views': total_views,
            'unique_visitors': total_unique,
            'previous_period': {
                'total_page_views': prev_period_views,
                'unique_visitors': prev_period_unique
            },
            'change_percentage': {
                'views': round(((total_views - prev_period_views) / prev_period_views) * 100, 2),
                'visitors': round(((total_unique - prev_period_unique) / prev_period_unique) * 100, 2)
            }
        }
    
    @staticmethod
    def generate_top_pages(limit: int = 10) -> List[Dict[str, Any]]:
        """Generate top pages data."""
        pages = [
            {'path': '/', 'title': 'Home'},
            {'path': '/about', 'title': 'About Us'},
            {'path': '/contact', 'title': 'Contact'},
            {'path': '/services', 'title': 'Services'},
            {'path': '/blog', 'title': 'Blog'},
            {'path': '/products', 'title': 'Products'},
            {'path': '/pricing', 'title': 'Pricing'},
            {'path': '/faq', 'title': 'FAQ'},
            {'path': '/terms', 'title': 'Terms of Service'},
            {'path': '/privacy', 'title': 'Privacy Policy'},
        ]
        
        result = []
        total_views = random.randint(5000, 15000)
        
        for i, page in enumerate(pages[:limit]):
            # Home page gets most views
            if i == 0:
                views = int(total_views * random.uniform(0.3, 0.4))
            else:
                views = int(total_views * random.uniform(0.05, 0.15) / (i + 1))
            
            result.append({
                **page,
                'views': views,
                'unique_visitors': int(views * random.uniform(0.6, 0.85))
            })
        
        # Sort by views
        result.sort(key=lambda x: x['views'], reverse=True)
        return result
    
    @staticmethod
    def generate_traffic_sources() -> List[Dict[str, Any]]:
        """Generate traffic source breakdown."""
        sources = [
            {'name': 'Direct', 'percentage': random.randint(25, 40)},
            {'name': 'Google', 'percentage': random.randint(20, 35)},
            {'name': 'Facebook', 'percentage': random.randint(5, 15)},
            {'name': 'Twitter', 'percentage': random.randint(3, 10)},
            {'name': 'LinkedIn', 'percentage': random.randint(2, 8)},
            {'name': 'Other', 'percentage': 0}  # Calculate remainder
        ]
        
        # Normalize to 100%
        total = sum(s['percentage'] for s in sources[:-1])
        sources[-1]['percentage'] = max(0, 100 - total)
        
        # Add visitor counts
        total_visitors = random.randint(3000, 10000)
        for source in sources:
            source['visitors'] = int(total_visitors * source['percentage'] / 100)
            source['color'] = MockAnalyticsData._get_color_for_source(source['name'])
        
        return sources
    
    @staticmethod
    def generate_device_breakdown() -> Dict[str, Any]:
        """Generate device and browser statistics."""
        devices = {
            'mobile': random.randint(45, 65),
            'desktop': random.randint(30, 50),
            'tablet': random.randint(5, 15)
        }
        
        # Normalize
        total = sum(devices.values())
        devices = {k: round((v / total) * 100, 1) for k, v in devices.items()}
        
        browsers = {
            'Chrome': random.randint(55, 70),
            'Safari': random.randint(15, 25),
            'Firefox': random.randint(5, 12),
            'Edge': random.randint(3, 8),
            'Other': 0
        }
        
        # Normalize browsers
        total_browsers = sum(browsers.values())
        browsers = {k: round((v / total_browsers) * 100, 1) for k, v in browsers.items()}
        browsers['Other'] = round(100 - sum(list(browsers.values())[:-1]), 1)
        
        operating_systems = {
            'Windows': random.randint(40, 55),
            'macOS': random.randint(20, 30),
            'iOS': random.randint(15, 25),
            'Android': random.randint(10, 20),
            'Linux': random.randint(2, 5),
            'Other': 0
        }
        
        total_os = sum(operating_systems.values())
        operating_systems = {k: round((v / total_os) * 100, 1) for k, v in operating_systems.items()}
        operating_systems['Other'] = round(100 - sum(list(operating_systems.values())[:-1]), 1)
        
        return {
            'devices': devices,
            'browsers': browsers,
            'operating_systems': operating_systems
        }
    
    @staticmethod
    def generate_geographic_data() -> List[Dict[str, Any]]:
        """Generate geographic distribution data."""
        countries = [
            {'code': 'US', 'name': 'United States', 'percentage': random.randint(30, 50)},
            {'code': 'GB', 'name': 'United Kingdom', 'percentage': random.randint(10, 20)},
            {'code': 'CA', 'name': 'Canada', 'percentage': random.randint(5, 15)},
            {'code': 'DE', 'name': 'Germany', 'percentage': random.randint(5, 12)},
            {'code': 'FR', 'name': 'France', 'percentage': random.randint(4, 10)},
            {'code': 'AU', 'name': 'Australia', 'percentage': random.randint(3, 8)},
            {'code': 'IN', 'name': 'India', 'percentage': random.randint(3, 8)},
            {'code': 'Other', 'name': 'Other', 'percentage': 0}
        ]
        
        # Normalize
        total = sum(c['percentage'] for c in countries[:-1])
        countries[-1]['percentage'] = max(0, 100 - total)
        
        # Add visitor counts
        total_visitors = random.randint(3000, 10000)
        for country in countries:
            country['visitors'] = int(total_visitors * country['percentage'] / 100)
        
        return countries
    
    @staticmethod
    def generate_bounce_rate() -> float:
        """Generate realistic bounce rate."""
        return round(random.uniform(35.0, 65.0), 2)
    
    @staticmethod
    def generate_avg_session_duration() -> int:
        """Generate average session duration in seconds."""
        return random.randint(120, 300)  # 2-5 minutes
    
    @staticmethod
    def get_full_analytics(days: int = 30, site_seed: int = None) -> Dict[str, Any]:
        """Generate complete analytics dataset."""
        if site_seed:
            random.seed(site_seed)
        
        return {
            'page_views_timeline': MockAnalyticsData.generate_page_views(days, site_seed),
            'visitors_summary': MockAnalyticsData.generate_visitors(days),
            'top_pages': MockAnalyticsData.generate_top_pages(),
            'traffic_sources': MockAnalyticsData.generate_traffic_sources(),
            'device_breakdown': MockAnalyticsData.generate_device_breakdown(),
            'geographic_data': MockAnalyticsData.generate_geographic_data(),
            'bounce_rate': MockAnalyticsData.generate_bounce_rate(),
            'avg_session_duration': MockAnalyticsData.generate_avg_session_duration()
        }
    
    @staticmethod
    def _get_color_for_source(source_name: str) -> str:
        """Get color for traffic source."""
        colors = {
            'Direct': '#3B82F6',  # Blue
            'Google': '#10B981',  # Green
            'Facebook': '#6366F1',  # Indigo
            'Twitter': '#8B5CF6',  # Purple
            'LinkedIn': '#EF4444',  # Red
            'Other': '#6B7280'  # Gray
        }
        return colors.get(source_name, '#9CA3AF')
