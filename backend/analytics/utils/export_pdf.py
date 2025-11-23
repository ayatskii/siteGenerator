from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from io import BytesIO
from datetime import datetime


def export_to_pdf(analytics_data: dict, site_name: str = "Site") -> bytes:
    """
    Export analytics data to PDF format using ReportLab.
    
    Args:
        analytics_data: Dictionary containing analytics data
        site_name: Name of the site for the report
    
    Returns:
        PDF content as bytes
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E40AF'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=16,
        textColor=colors.HexColor('#1E40AF'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    # Title
    title = Paragraph(f"Analytics Report: {site_name}", title_style)
    elements.append(title)
    
    subtitle = Paragraph(
        f"Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}",
        styles['Normal']
    )
    elements.append(subtitle)
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary metrics
    elements.append(Paragraph("Summary Metrics", heading_style))
    
    summary = analytics_data.get('visitors_summary', {})
    summary_data = [
        ['Metric', 'Value'],
        ['Total Page Views', f"{summary.get('total_page_views', 0):,}"],
        ['Unique Visitors', f"{summary.get('unique_visitors', 0):,}"],
        ['Bounce Rate', f"{analytics_data.get('bounce_rate', 0):.1f}%"],
        ['Avg Session Duration', f"{analytics_data.get('avg_session_duration', 0)} seconds"],
    ]
    
    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Top Pages
    elements.append(Paragraph("Top Pages", heading_style))
    
    top_pages_data = [['Path', 'Title', 'Views', 'Visitors']]
    for page in analytics_data.get('top_pages', [])[:10]:
        top_pages_data.append([
            page['path'][:30],  # Truncate long paths
            page['title'][:30],  # Truncate long titles
            f"{page['views']:,}",
            f"{page['unique_visitors']:,}"
        ])
    
    top_pages_table = Table(top_pages_data, colWidths=[1.5*inch, 2*inch, 1*inch, 1*inch])
    top_pages_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(top_pages_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Traffic Sources
    elements.append(Paragraph("Traffic Sources", heading_style))
    
    traffic_data = [['Source', 'Percentage', 'Visitors']]
    for source in analytics_data.get('traffic_sources', []):
        traffic_data.append([
            source['name'],
            f"{source['percentage']}%",
            f"{source['visitors']:,}"
        ])
    
    traffic_table = Table(traffic_data, colWidths=[2*inch, 1.5*inch, 1.5*inch])
    traffic_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(traffic_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Device Breakdown
    elements.append(Paragraph("Device Breakdown", heading_style))
    
    device_data = analytics_data.get('device_breakdown', {})
    device_breakdown_data = [['Category', 'Type', 'Percentage']]
    
    for device, percentage in device_data.get('devices', {}).items():
        device_breakdown_data.append(['Device', device.capitalize(), f"{percentage}%"])
    
    for browser, percentage in list(device_data.get('browsers', {}).items())[:5]:  # Top 5 browsers
        device_breakdown_data.append(['Browser', browser, f"{percentage}%"])
    
    device_table = Table(device_breakdown_data, colWidths=[2*inch, 2*inch, 1.5*inch])
    device_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (2, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(device_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Geographic Distribution
    elements.append(Paragraph("Geographic Distribution (Top 10)", heading_style))
    
    geo_data = [['Country', 'Percentage', 'Visitors']]
    for country in analytics_data.get('geographic_data', [])[:10]:
        if country['code'] != 'Other':  # Skip "Other" in main list
            geo_data.append([
                country['name'],
                f"{country['percentage']}%",
                f"{country['visitors']:,}"
            ])
    
    geo_table = Table(geo_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
    geo_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E40AF')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    elements.append(geo_table)
    
    # Build PDF
    doc.build(elements)
    
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content
