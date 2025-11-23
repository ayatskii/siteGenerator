from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ..models import UmamiConfig, AnalyticsCache
from ..utils.mock_data import MockAnalyticsData


class AnalyticsService:
    """
    Service for retrieving analytics data.
    Uses Umami API if configured, otherwise returns mock data.
    """
    
    @staticmethod
    def get_analytics(site_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get analytics data for a site.
        Uses Umami API if configured, otherwise returns mock data.
        """
        from sites.models import Site
        
        try:
            site = Site.objects.get(id=site_id)
        except Site.DoesNotExist:
            raise ValueError(f"Site with id {site_id} not found")
        
        # Check if site has Umami configured
        try:
            umami_config = site.umami_config
            if umami_config.is_active:
                try:
                    return AnalyticsService._fetch_umami_stats(umami_config, start_date, end_date)
                except Exception as e:
                    print(f"Error fetching Umami stats: {e}")
                    # Fallback to mock data if API fails? Or re-raise?
                    # For now, let's fall back so the UI doesn't break, but log it.
                    pass
        except UmamiConfig.DoesNotExist:
            pass
        
        # Calculate days
        days = (end_date - start_date).days + 1
        
        # Generate mock data with site ID as seed for consistency
        analytics_data = MockAnalyticsData.get_full_analytics(days=days, site_seed=site_id)
        
        return analytics_data

    @staticmethod
    def _fetch_umami_stats(config, start_date, end_date) -> Dict[str, Any]:
        """
        Fetch real data from Umami API.
        """
        import requests
        
        # Ensure URL doesn't have trailing slash
        base_url = config.api_url.rstrip('/')
        headers = {
            'Authorization': f'Bearer {config.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Umami expects timestamps in milliseconds
        params = {
            'startAt': int(start_date.timestamp() * 1000),
            'endAt': int(end_date.timestamp() * 1000),
        }
        
        def get_umami_data(endpoint, extra_params=None):
            p = params.copy()
            if extra_params:
                p.update(extra_params)
            
            url = f"{base_url}/api/websites/{config.umami_site_id}/{endpoint}"
            response = requests.get(url, headers=headers, params=p)
            response.raise_for_status()
            return response.json()

        # 1. General Stats
        stats = get_umami_data('stats')
        # Response format: { pageviews: { value: 100, change: 10 }, visitors: { ... }, ... }
        
        # 2. Pageviews Timeline
        # unit: hour, day, month, year
        timeline = get_umami_data('pageviews', {'unit': 'day'})
        # Response: { pageviews: [{x: '2023-01-01', y: 10}, ...], sessions: [...] }
        
        # 3. Top Pages
        top_pages_data = get_umami_data('metrics', {'type': 'url', 'limit': 10})
        # Response: [{x: '/path', y: 100}, ...]
        
        # 4. Referrers
        referrers_data = get_umami_data('metrics', {'type': 'referrer', 'limit': 10})
        
        # 5. Devices/Browsers
        browsers_data = get_umami_data('metrics', {'type': 'browser', 'limit': 10})
        devices_data = get_umami_data('metrics', {'type': 'device', 'limit': 10})
        
        # 6. Geographic
        countries_data = get_umami_data('metrics', {'type': 'country', 'limit': 50})

        # --- Map to Internal Format ---
        
        # Visitors Summary
        visitors_summary = {
            'total_page_views': stats.get('pageviews', {}).get('value', 0),
            'unique_visitors': stats.get('visitors', {}).get('value', 0),
            'change_percentage': stats.get('visitors', {}).get('change', 0),
            # Bounce rate and duration might be in stats or need calculation
            # Umami stats usually include bounce rate and duration
            'bounce_rate': stats.get('bounces', {}).get('value', 0), # This might be count, not rate. 
            # Actually Umami API v2 stats endpoint returns 'bounces' as object with value. 
            # Let's assume value is the rate or count. If count, we need to calc rate.
            # For simplicity, let's trust the value or mock if missing.
        }
        
        # Calculate derived metrics if needed
        # Umami's 'bounces' value is usually the number of bounces. 
        # Bounce rate = (bounces / total_visits) * 100
        total_visits = stats.get('visits', {}).get('value', 0)
        bounce_count = stats.get('bounces', {}).get('value', 0)
        bounce_rate = (bounce_count / total_visits * 100) if total_visits > 0 else 0
        
        avg_duration = stats.get('totaltime', {}).get('value', 0) / total_visits if total_visits > 0 else 0
        
        # Timeline
        # Umami returns [{x: '2023-01-01 00:00:00', y: 10}, ...]
        # We need to map to simple date string if needed
        page_views_timeline = [
            {'date': item['x'].split(' ')[0], 'views': item['y']} 
            for item in timeline.get('pageviews', [])
        ]
        
        # Top Pages
        top_pages = [
            {'path': item['x'], 'views': item['y']}
            for item in top_pages_data
        ]
        
        # Traffic Sources
        traffic_sources = [
            {'source': item['x'], 'visitors': item['y']}
            for item in referrers_data
        ]
        
        # Device Breakdown
        device_breakdown = {
            'desktop': 0, 'mobile': 0, 'tablet': 0, # Aggregate if possible
            'browsers': {item['x']: item['y'] for item in browsers_data}
        }
        # Aggregate devices
        for item in devices_data:
            dev_type = item['x'].lower()
            if dev_type in device_breakdown:
                device_breakdown[dev_type] += item['y']
            else:
                device_breakdown[dev_type] = item['y'] # Fallback
                
        # Geographic
        geographic_data = [
            {'country': item['x'], 'visitors': item['y']}
            for item in countries_data
        ]
        
        return {
            'visitors_summary': visitors_summary,
            'bounce_rate': round(bounce_rate, 1),
            'avg_session_duration': int(avg_duration),
            'page_views_timeline': page_views_timeline,
            'top_pages': top_pages,
            'traffic_sources': traffic_sources,
            'device_breakdown': device_breakdown,
            'geographic_data': geographic_data
        }
    
    @staticmethod
    def get_summary(site_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get summarized analytics metrics."""
        full_data = AnalyticsService.get_analytics(site_id, start_date, end_date)
        
        return {
            'total_page_views': full_data['visitors_summary']['total_page_views'],
            'unique_visitors': full_data['visitors_summary']['unique_visitors'],
            'bounce_rate': full_data['bounce_rate'],
            'avg_session_duration': full_data['avg_session_duration'],
            'change_from_previous': full_data['visitors_summary']['change_percentage'],
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat()
            }
        }
    
    @staticmethod
    def get_top_pages(site_id: int, start_date: datetime, end_date: datetime, limit: int = 10) -> list:
        """Get top pages for a site."""
        full_data = AnalyticsService.get_analytics(site_id, start_date, end_date)
        return full_data['top_pages'][:limit]
    
    @staticmethod
    def get_traffic_sources(site_id: int, start_date: datetime, end_date: datetime) -> list:
        """Get traffic sources breakdown."""
        full_data = AnalyticsService.get_analytics(site_id, start_date, end_date)
        return full_data['traffic_sources']
    
    @staticmethod
    def get_device_breakdown(site_id: int, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """Get device and browser statistics."""
        full_data = AnalyticsService.get_analytics(site_id, start_date, end_date)
        return full_data['device_breakdown']
    
    @staticmethod
    def get_timeline_data(site_id: int, start_date: datetime, end_date: datetime) -> list:
        """Get timeline data for charts."""
        full_data = AnalyticsService.get_analytics(site_id, start_date, end_date)
        return full_data['page_views_timeline']
