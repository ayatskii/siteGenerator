import { useTranslation } from 'react-i18next';

const GeographicMap = ({ data }) => {
  const { t } = useTranslation();

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.geographicDistribution')}</h3>
        <div className="flex items-center justify-center h-64 text-gray-400">
          <p>{t('analytics.noGeoData')}</p>
        </div>
      </div>
    );
  }

  // Filter out "Other" and get top countries
  const topCountries = data
    .filter(country => country.code !== 'Other')
    .slice(0, 10);

  const getBarColor = (index) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-purple-500',
      'bg-amber-500',
      'bg-red-500',
      'bg-indigo-500',
      'bg-pink-500',
      'bg-teal-500',
      'bg-orange-500',
      'bg-cyan-500'
    ];
    return colors[index % colors.length];
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.geographicDistribution')}</h3>
      <p className="text-sm text-gray-600 mb-6">{t('analytics.topCountries')}</p>
      
      <div className="space-y-4">
        {topCountries.map((country, index) => (
          <div key={index} className="relative">
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{country.code === 'US' ? '🇺🇸' : 
                                            country.code === 'GB' ? '🇬🇧' :
                                            country.code === 'CA' ? '🇨🇦' :
                                            country.code === 'AU' ? '🇦🇺' :
                                            country.code === 'DE' ? '🇩🇪' :
                                            country.code === 'FR' ? '🇫🇷' :
                                            country.code === 'ES' ? '🇪🇸' :
                                            country.code === 'IT' ? '🇮🇹' :
                                            country.code === 'NL' ? '🇳🇱' :
                                            '🌍'}</span>
                <div>
                  <p className="text-sm font-medium text-gray-900">{country.name}</p>
                  <p className="text-xs text-gray-500">{country.visitors.toLocaleString()} {t('analytics.visitors')}</p>
                </div>
              </div>
              <span className="text-sm font-semibold text-gray-700">
                {country.percentage.toFixed(1)}%
              </span>
            </div>
            
            <div className="w-full bg-gray-200 rounded-full h-2.5">
              <div
                className={`${getBarColor(index)} h-2.5 rounded-full transition-all duration-500`}
                style={{ width: `${country.percentage}%` }}
              ></div>
            </div>
          </div>
        ))}
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="grid grid-cols-2 gap-4 text-center">
          <div>
            <p className="text-2xl font-bold text-gray-900">{topCountries.length}</p>
            <p className="text-xs text-gray-600">{t('analytics.countries')}</p>
          </div>
          <div>
            <p className="text-2xl font-bold text-gray-900">
              {topCountries.reduce((sum, c) => sum + c.visitors, 0).toLocaleString()}
            </p>
            <p className="text-xs text-gray-600">{t('analytics.totalVisitors')}</p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GeographicMap;
