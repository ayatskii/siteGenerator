import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
);

const DeviceBreakdown = ({ data }) => {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Device Breakdown</h3>
        <div className="flex items-center justify-center h-64 text-gray-400">
          <p>No device data available</p>
        </div>
      </div>
    );
  }

  const { devices = {}, browsers = {}, operating_systems = {} } = data;

  // Device chart data
  const deviceData = {
    labels: Object.keys(devices),
    datasets: [
      {
        label: 'Device Usage (%)',
        data: Object.values(devices),
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgb(59, 130, 246)',
        borderWidth: 1
      }
    ]
  };

  // Browser chart data (top 5)
  const browserEntries = Object.entries(browsers).slice(0, 5);
  const browserData = {
    labels: browserEntries.map(([name]) => name),
    datasets: [
      {
        label: 'Browser Usage (%)',
        data: browserEntries.map(([, value]) => value),
        backgroundColor: 'rgba(16, 185, 129, 0.6)',
        borderColor: 'rgb(16, 185, 129)',
        borderWidth: 1
      }
    ]
  };

  const chartOptions = {
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        padding: 12,
        callbacks: {
          label: function(context) {
            return `${context.parsed.x.toFixed(1)}%`;
          }
        }
      }
    },
    scales: {
      x: {
        beginAtZero: true,
        max: 100,
        ticks: {
          callback: function(value) {
            return value + '%';
          }
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)'
        }
      },
      y: {
        grid: {
          display: false
        }
      }
    }
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Device & Browser Breakdown</h3>
      
      {/* Devices */}
      <div className="mb-6">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Devices</h4>
        <div className="h-32">
          <Bar data={deviceData} options={chartOptions} />
        </div>
      </div>

      {/* Browsers */}
      <div className="mb-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">Top Browsers</h4>
        <div className="h-40">
          <Bar data={browserData} options={chartOptions} />
        </div>
      </div>

      {/* OS Stats */}
      {Object.keys(operating_systems).length > 0 && (
        <div className="mt-6 pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-3">Operating Systems</h4>
          <div className="space-y-2">
            {Object.entries(operating_systems).slice(0, 5).map(([os, percentage], index) => (
              <div key={index} className="flex items-center justify-between">
                <span className="text-sm text-gray-600">{os}</span>
                <div className="flex items-center gap-2">
                  <div className="w-24 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-purple-500 h-2 rounded-full"
                      style={{ width: `${percentage}%` }}
                    ></div>
                  </div>
                  <span className="text-sm font-medium text-gray-700 w-12 text-right">
                    {percentage.toFixed(1)}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default DeviceBreakdown;
