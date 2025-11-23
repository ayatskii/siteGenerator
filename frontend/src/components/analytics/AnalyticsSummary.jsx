import { ArrowUpIcon, ArrowDownIcon } from '@heroicons/react/24/solid';
import { useTranslation } from 'react-i18next';

const AnalyticsSummary = ({ data }) => {
  const { t } = useTranslation();

  if (!data || !data.visitors_summary) {
    return null;
  }

  const { visitors_summary } = data;
  
  const cards = [
    {
      title: t('analytics.totalPageViews'),
      value: visitors_summary.total_page_views?.toLocaleString() || '0',
      icon: '📊',
      color: 'blue',
      trend: visitors_summary.total_page_views > 1000 ? 'up' : null
    },
    {
      title: t('analytics.uniqueVisitors'),
      value: visitors_summary.unique_visitors?.toLocaleString() || '0',
      icon: '👥',
      color: 'green',
      trend: visitors_summary.unique_visitors > 500 ? 'up' : null
    },
    {
      title: t('analytics.bounceRate'),
      value: `${data.bounce_rate?.toFixed(1) || '0'}%`,
      icon: '📉',
      color: 'amber',
      trend: data.bounce_rate < 40 ? 'up' : 'down'
    },
    {
      title: t('analytics.avgSessionDuration'),
      value: `${Math.floor((data.avg_session_duration || 0) / 60)}m ${(data.avg_session_duration || 0) % 60}s`,
      icon: '⏱️',
      color: 'purple',
      trend: data.avg_session_duration > 120 ? 'up' : null
    }
  ];

  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    amber: 'bg-amber-50 border-amber-200',
    purple: 'bg-purple-50 border-purple-200'
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`${colorClasses[card.color]} border rounded-lg p-5 shadow-sm hover:shadow-md transition-shadow`}
        >
          <div className="flex items-start justify-between mb-3">
            <div>
              <p className="text-sm font-medium text-gray-600 mb-1">{card.title}</p>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
            </div>
            <span className="text-3xl">{card.icon}</span>
          </div>
          
          {card.trend && (
            <div className={`flex items-center text-sm ${card.trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
              {card.trend === 'up' ? (
                <ArrowUpIcon className="w-4 h-4 mr-1" />
              ) : (
                <ArrowDownIcon className="w-4 h-4 mr-1" />
              )}
              <span className="font-medium">
                {card.trend === 'up' ? t('analytics.performingWell') : t('analytics.needsAttention')}
              </span>
            </div>
          )}
        </div>
      ))}
    </div>
  );
};

export default AnalyticsSummary;
