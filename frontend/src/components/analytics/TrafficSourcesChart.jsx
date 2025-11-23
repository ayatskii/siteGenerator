import { Doughnut } from 'react-chartjs-2';
import { useTranslation } from 'react-i18next';
import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend
} from 'chart.js';

// Register Chart.js components
ChartJS.register(ArcElement, Tooltip, Legend);

const TrafficSourcesChart = ({ data }) => {
  const { t } = useTranslation();

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.trafficSources')}</h3>
        <div className="flex items-center justify-center h-64 text-gray-400">
          <p>{t('analytics.noTrafficData')}</p>
        </div>
      </div>
    );
  }

  const chartData = {
    labels: data.map(source => source.name),
    datasets: [
      {
        data: data.map(source => source.percentage),
        backgroundColor: data.map(source => source.color || '#3B82F6'),
        borderColor: '#fff',
        borderWidth: 2,
        hoverOffset: 10
      }
    ]
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: 'right',
        labels: {
          usePointStyle: true,
          padding: 15,
          generateLabels: (chart) => {
            const datasets = chart.data.datasets;
            return chart.data.labels.map((label, i) => ({
              text: `${label}: ${datasets[0].data[i]}%`,
              fillStyle: datasets[0].backgroundColor[i],
              hidden: false,
              index: i
            }));
          }
        }
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        titleColor: '#fff',
        bodyColor: '#fff',
        callbacks: {
          label: function(context) {
            const source = data[context.dataIndex];
            return [
              `${context.label}: ${context.parsed}%`,
              `${t('analytics.visitors')}: ${source.visitors.toLocaleString()}`
            ];
          }
        }
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.trafficSources')}</h3>
      <div className="h-64">
        <Doughnut data={chartData} options={options} />
      </div>
      
      {/* Additional Stats */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4">
          {data.slice(0, 4).map((source, index) => (
            <div key={index} className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: source.color || '#3B82F6' }}
                ></div>
                <span className="text-sm font-medium text-gray-700">{source.name}</span>
              </div>
              <span className="text-sm text-gray-600">{source.visitors.toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default TrafficSourcesChart;
