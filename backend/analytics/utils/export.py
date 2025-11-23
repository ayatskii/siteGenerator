import csv
from io import StringIO
from datetime import datetime


def export_to_csv(analytics_data: dict, site_name: str = "Site") -> str:
    """
    Export analytics data to CSV format.
    
    Args:
        analytics_data: Dictionary containing analytics data
        site_name: Name of the site for the report
    
    Returns:
        CSV content as string
    """
    output = StringIO()
    
    # Write header
    output.write(f"Analytics Report for {site_name}\n")
    output.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    output.write("\n")
    
    # Summary metrics
    output.write("SUMMARY METRICS\n")
    summary = analytics_data.get('visitors_summary', {})
    output.write(f"Total Page Views,{summary.get('total_page_views', 0)}\n")
    output.write(f"Unique Visitors,{summary.get('unique_visitors', 0)}\n")
    output.write(f"Bounce Rate,{analytics_data.get('bounce_rate', 0)}%\n")
    output.write(f"Avg Session Duration,{analytics_data.get('avg_session_duration', 0)} seconds\n")
    output.write("\n")
    
    # Page views timeline
    output.write("PAGE VIEWS TIMELINE\n")
    output.write("Date,Views,Unique Visitors\n")
    for entry in analytics_data.get('page_views_timeline', []):
        output.write(f"{entry['date']},{entry['views']},{entry['unique_visitors']}\n")
    output.write("\n")
    
    # Top pages
    output.write("TOP PAGES\n")
    output.write("Path,Title,Views,Unique Visitors\n")
    for page in analytics_data.get('top_pages', []):
        output.write(f"{page['path']},{page['title']},{page['views']},{page['unique_visitors']}\n")
    output.write("\n")
    
    # Traffic sources
    output.write("TRAFFIC SOURCES\n")
    output.write("Source,Percentage,Visitors\n")
    for source in analytics_data.get('traffic_sources', []):
        output.write(f"{source['name']},{source['percentage']}%,{source['visitors']}\n")
    output.write("\n")
    
    # Device breakdown
    output.write("DEVICE BREAKDOWN\n")
    device_data = analytics_data.get('device_breakdown', {})
    
    output.write("\nDevices\n")
    output.write("Type,Percentage\n")
    for device, percentage in device_data.get('devices', {}).items():
        output.write(f"{device},{percentage}%\n")
    
    output.write("\nBrowsers\n")
    output.write("Browser,Percentage\n")
    for browser, percentage in device_data.get('browsers', {}).items():
        output.write(f"{browser},{percentage}%\n")
    
    output.write("\nOperating Systems\n")
    output.write("OS,Percentage\n")
    for os, percentage in device_data.get('operating_systems', {}).items():
        output.write(f"{os},{percentage}%\n")
    output.write("\n")
    
    # Geographic data
    output.write("GEOGRAPHIC DISTRIBUTION\n")
    output.write("Country,Code,Percentage,Visitors\n")
    for country in analytics_data.get('geographic_data', []):
        output.write(f"{country['name']},{country['code']},{country['percentage']}%,{country['visitors']}\n")
    
    content = output.getvalue()
    output.close()
    
    return content
