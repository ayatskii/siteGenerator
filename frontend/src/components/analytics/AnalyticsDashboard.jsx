import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { format, subDays } from 'date-fns';
import analyticsService from '../../services/analyticsService';
import AnalyticsSummary from './AnalyticsSummary';
import PageViewsChart from './PageViewsChart';
import TopPagesTable from './TopPagesTable';
import TrafficSourcesChart from './TrafficSourcesChart';
import DeviceBreakdown from './DeviceBreakdown';
import GeographicMap from './GeographicMap';
import ExportButton from './ExportButton';
import UmamiConfigForm from './UmamiConfigForm';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';

const AnalyticsDashboard = ({ siteId: propSiteId }) => {
  const params = useParams();
  const siteId = propSiteId || params.siteId;
  
  const [hasConfig, setHasConfig] = useState(false);
  const [checkingConfig, setCheckingConfig] = useState(true);
  
  const [analyticsData, setAnalyticsData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Date range state - default to last 30 days
  const [startDate, setStartDate] = useState(subDays(new Date(), 30));
  const [endDate, setEndDate] = useState(new Date());

  // Check configuration first
  useEffect(() => {
    const checkConfig = async () => {
      if (!siteId) return;
      try {
        const config = await analyticsService.getUmamiConfig(siteId);
        setHasConfig(!!config && config.is_active);
      } catch (error) {
        console.error("Error checking analytics config:", error);
      } finally {
        setCheckingConfig(false);
      }
    };
    checkConfig();
  }, [siteId]);

  // Fetch analytics data only if configured
  useEffect(() => {
    const fetchAnalytics = async () => {
      if (!siteId || !hasConfig) return;
      
      setLoading(true);
      setError(null);
      
      try {
        const data = await analyticsService.getAnalytics(
          siteId,
          format(startDate, 'yyyy-MM-dd'),
          format(endDate, 'yyyy-MM-dd')
        );
        setAnalyticsData(data);
      } catch (err) {
        setError(err.message || 'Failed to load analytics data');
        console.error('Analytics fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    if (siteId && hasConfig) {
      fetchAnalytics();
    }
  }, [siteId, hasConfig, startDate, endDate]);

  if (checkingConfig) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Checking configuration...</p>
        </div>
      </div>
    );
  }

  if (!hasConfig) {
    return (
      <div className="container mx-auto px-4 py-6">
        <UmamiConfigForm 
          siteId={siteId} 
          onConfigSaved={() => setHasConfig(true)} 
        />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
          <p className="mt-4 text-gray-600">Loading analytics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
          <h3 className="text-red-800 font-semibold mb-2">Error Loading Analytics</h3>
          <p className="text-red-600">{error}</p>
          <button
            onClick={() => window.location.reload()}
            className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
          >
            Retry
          </button>
          <div className="mt-4 pt-4 border-t border-red-200">
             <button 
                onClick={() => setHasConfig(false)}
                className="text-sm text-red-700 hover:text-red-900 underline"
             >
                Check Configuration
             </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      {/* Header */}
      <div className="flex justify-between items-start mb-6">
        <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Analytics Dashboard</h1>
            <p className="text-gray-600">Track your site's performance and visitor insights</p>
        </div>
        <button 
            onClick={() => setHasConfig(false)}
            className="text-sm text-blue-600 hover:text-blue-800"
        >
            Configure Settings
        </button>
      </div>

      {/* Controls Bar */}
      <div className="bg-white rounded-lg shadow p-4 mb-6">
        <div className="flex flex-wrap items-center gap-4 justify-between">
          {/* Date Range Picker */}
          <div className="flex items-center gap-3">
            <label className="text-sm font-medium text-gray-700">Date Range:</label>
            <DatePicker
              selected={startDate}
              onChange={setStartDate}
              selectsStart
              startDate={startDate}
              endDate={endDate}
              maxDate={endDate}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              dateFormat="MMM d, yyyy"
            />
            <span className="text-gray-500">to</span>
            <DatePicker
              selected={endDate}
              onChange={setEndDate}
              selectsEnd
              startDate={startDate}
              endDate={endDate}
              minDate={startDate}
              maxDate={new Date()}
              className="px-3 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
              dateFormat="MMM d, yyyy"
            />
          </div>

          {/* Export Button */}
          <ExportButton
            siteId={siteId}
            startDate={startDate}
            endDate={endDate}
          />
        </div>
      </div>

      {/* Summary Cards */}
      <AnalyticsSummary data={analyticsData} />

      {/* Main Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Page Views Chart */}
        <PageViewsChart data={analyticsData?.page_views_timeline || []} />
        
        {/* Traffic Sources */}
        <TrafficSourcesChart data={analyticsData?.traffic_sources || []} />
      </div>

      {/* Top Pages Table */}
      <div className="mb-6">
        <TopPagesTable data={analyticsData?.top_pages || []} />
      </div>

      {/* Device & Geographic Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Device Breakdown */}
        <DeviceBreakdown data={analyticsData?.device_breakdown || {}} />
        
        {/* Geographic Distribution */}
        <GeographicMap data={analyticsData?.geographic_data || []} />
      </div>
    </div>
  );
};

export default AnalyticsDashboard;
