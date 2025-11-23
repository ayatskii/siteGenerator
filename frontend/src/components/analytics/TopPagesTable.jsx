import { useState } from 'react';
import { useTranslation } from 'react-i18next';

const TopPagesTable = ({ data }) => {
  const { t } = useTranslation();
  const [sortField, setSortField] = useState('views');
  const [sortDirection, setSortDirection] = useState('desc');

  if (!data || data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">{t('analytics.topPages')}</h3>
        <div className="text-center py-8 text-gray-400">
          <p>{t('analytics.noPageData')}</p>
        </div>
      </div>
    );
  }

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const sortedData = [...data].sort((a, b) => {
    const aValue = a[sortField];
    const bValue = b[sortField];
    
    if (sortDirection === 'asc') {
      return aValue > bValue ? 1 : -1;
    } else {
      return aValue < bValue ? 1 : -1;
    }
  });

  return (
    <div className="bg-white rounded-lg shadow overflow-hidden">
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900">{t('analytics.topPages')}</h3>
        <p className="text-sm text-gray-600 mt-1">{t('analytics.mostVisited')}</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('path')}
              >
                <div className="flex items-center gap-1">
                  {t('analytics.path')} <SortIcon field="path" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('title')}
              >
                <div className="flex items-center gap-1">
                  {t('analytics.pageTitle')} <SortIcon field="title" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('views')}
              >
                <div className="flex items-center justify-end gap-1">
                  {t('analytics.views')} <SortIcon field="views" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
              <th
                scope="col"
                className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('unique_visitors')}
              >
                <div className="flex items-center justify-end gap-1">
                  {t('analytics.uniqueVisitors')} <SortIcon field="unique_visitors" sortField={sortField} sortDirection={sortDirection} />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedData.map((page, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-blue-600">
                  {page.path}
                </td>
                <td className="px-6 py-4 text-sm text-gray-900 max-w-md truncate">
                  {page.title}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 text-right font-semibold">
                  {page.views.toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-600 text-right">
                  {page.unique_visitors.toLocaleString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

const SortIcon = ({ field, sortField, sortDirection }) => {
  if (sortField !== field) {
    return <span className="text-gray-400">⇅</span>;
  }
  return <span>{sortDirection === 'asc' ? '↑' : '↓'}</span>;
};

export default TopPagesTable;
