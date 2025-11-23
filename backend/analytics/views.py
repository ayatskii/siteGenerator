from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from datetime import datetime, timedelta
from .models import UmamiConfig
from .serializers import (
    UmamiConfigSerializer, 
    AnalyticsDataSerializer, 
    AnalyticsSummarySerializer
)
from .services.analytics_service import AnalyticsService


class AnalyticsViewSet(viewsets.ViewSet):
    """
    ViewSet for analytics data.
    Provides endpoints for retrieving analytics data for sites.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='sites/(?P<site_id>[^/.]+)')
    def site_analytics(self, request, site_id=None):
        """
        Get full analytics data for a specific site.
        Query params:
        - start_date: Start date (YYYY-MM-DD), defaults to 30 days ago
        - end_date: End date (YYYY-MM-DD), defaults to today
        """
        # Parse date parameters
        end_date = request.query_params.get('end_date')
        start_date = request.query_params.get('start_date')
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=30)
        
        try:
            analytics_data = AnalyticsService.get_analytics(
                site_id=int(site_id),
                start_date=start_date,
                end_date=end_date
            )
            
            serializer = AnalyticsDataSerializer(analytics_data)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='sites/(?P<site_id>[^/.]+)/summary')
    def site_summary(self, request, site_id=None):
        """Get summary analytics for a specific site."""
        # Parse date parameters (same as site_analytics)
        end_date = request.query_params.get('end_date')
        start_date = request.query_params.get('start_date')
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=30)
        
        try:
            summary = AnalyticsService.get_summary(
                site_id=int(site_id),
                start_date=start_date,
                end_date=end_date
            )
            
            serializer = AnalyticsSummarySerializer(summary)
            return Response(serializer.data)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=False, methods=['get'], url_path='sites/(?P<site_id>[^/.]+)/export')
    def export_analytics(self, request, site_id=None):
        """
        Export analytics data to CSV or PDF.
        Query params:
        - format: 'csv' or 'pdf' (default: csv)
        - start_date: Start date (YYYY-MM-DD)
        - end_date: End date (YYYY-MM-DD)
        """
        from django.http import HttpResponse
        from analytics.utils.export import export_to_csv
        from analytics.utils.export_pdf import export_to_pdf
        from sites.models import Site
        
        # Get export format
        export_format = request.query_params.get('format', 'csv').lower()
        
        # Parse date parameters
        end_date = request.query_params.get('end_date')
        start_date = request.query_params.get('start_date')
        
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        else:
            end_date = datetime.now()
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        else:
            start_date = end_date - timedelta(days=30)
        
        try:
            # Verify site exists and user has access
            site = Site.objects.get(id=int(site_id), owner=request.user)
            site_name = site.name or site.domain
            
            # Get analytics data
            analytics_data = AnalyticsService.get_analytics(
                site_id=int(site_id),
                start_date=start_date,
                end_date=end_date
            )
            
            if export_format == 'pdf':
                # Export as PDF
                pdf_content = export_to_pdf(analytics_data, site_name)
                response = HttpResponse(pdf_content, content_type='application/pdf')
                response['Content-Disposition'] = f'attachment; filename="analytics_{site.domain}_{datetime.now().strftime("%Y%m%d")}.pdf"'
                return response
            else:
                # Export as CSV (default)
                csv_content = export_to_csv(analytics_data, site_name)
                response = HttpResponse(csv_content, content_type='text/csv')
                response['Content-Disposition'] = f'attachment; filename="analytics_{site.domain}_{datetime.now().strftime("%Y%m%d")}.csv"'
                return response
                
        except Site.DoesNotExist:
            return Response({'error': 'Site not found'}, status=status.HTTP_404_NOT_FOUND)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UmamiConfigViewSet(viewsets.ModelViewSet):
    """ViewSet for managing Umami configurations."""
    serializer_class = UmamiConfigSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Filter configs by sites owned by the user."""
        return UmamiConfig.objects.filter(site__owner=self.request.user)
