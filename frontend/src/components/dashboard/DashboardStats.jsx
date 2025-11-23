import { useState, useEffect } from 'react';
import sitesService from '../../services/sitesService';

const DashboardStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const data = await sitesService.getDashboardStatistics();
        setStats(data);
      } catch (err) {
        setError(err.message || 'Failed to load statistics');
        console.error('Stats fetch error:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-8 bg-gray-200 rounded w-3/4"></div>
          </div>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
        <p className="text-red-600 text-sm">Failed to load statistics: {error}</p>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Sites',
      value: stats?.total_sites || 0,
      icon: '🌐',
      color: 'blue',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600'
    },
    {
      title: 'Sites Deployed',
      value: stats?.sites_deployed || 0,
      icon: '🚀',
      color: 'green',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600'
    },
    {
      title: 'Total Pages',
      value: stats?.total_pages || 0,
      icon: '📄',
      color: 'purple',
      bgColor: 'bg-purple-50',
      textColor: 'text-purple-600'
    },
    {
      title: 'Storage Used',
      value: `${(stats?.storage_used || 0).toFixed(1)} MB`,
      icon: '💾',
      color: 'amber',
      bgColor: 'bg-amber-50',
      textColor: 'text-amber-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {statCards.map((card, index) => (
        <div key={index} className={`${card.bgColor} rounded-lg shadow p-6 border border-gray-200`}>
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">{card.title}</h3>
            <span className="text-2xl">{card.icon}</span>
          </div>
          <p className={`text-3xl font-bold ${card.textColor}`}>
            {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
          </p>
        </div>
      ))}
    </div>
  );
};

export default DashboardStats;
