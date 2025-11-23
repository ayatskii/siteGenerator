import { useState } from 'react';

const SiteFilters = ({ onFilterChange }) => {
  const [filters, setFilters] = useState({
    language: '',
    brand: '',
    geo: '',
    search: ''
  });

  const handleFilterChange = (key, value) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const clearFilters = () => {
    const emptyFilters = {
      language: '',
      brand: '',
      geo: '',
      search: ''
    };
    setFilters(emptyFilters);
    onFilterChange(emptyFilters);
  };

  const hasActiveFilters = Object.values(filters).some(value => value !== '');

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="flex flex-wrap gap-4 items-center">
        {/* Search */}
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            placeholder="Search sites..."
            value={filters.search}
            onChange={(e) => handleFilterChange('search', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Language Filter */}
        <div className="min-w-[150px]">
          <select
            value={filters.language}
            onChange={(e) => handleFilterChange('language', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Languages</option>
            <option value="en-US">English (US)</option>
            <option value="en-GB">English (GB)</option>
            <option value="fr-FR">French</option>
            <option value="de-DE">German</option>
            <option value="es-ES">Spanish</option>
            <option value="it-IT">Italian</option>
          </select>
        </div>

        {/* Brand Filter */}
        <div className="min-w-[150px]">
          <input
            type="text"
            placeholder="Filter by brand"
            value={filters.brand}
            onChange={(e) => handleFilterChange('brand', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Geo Targeting Filter */}
        <div className="min-w-[150px]">
          <input
            type="text"
            placeholder="Filter by geo"
            value={filters.geo}
            onChange={(e) => handleFilterChange('geo', e.target.value)}
            className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
          />
        </div>

        {/* Clear Filters Button */}
        {hasActiveFilters && (
          <button
            onClick={clearFilters}
            className="px-4 py-2 text-sm text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Clear Filters
          </button>
        )}
      </div>

      {/* Active Filters Tags */}
      {hasActiveFilters && (
        <div className="mt-3 flex flex-wrap gap-2">
          {filters.search && (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm">
              Search: {filters.search}
              <button
                onClick={() => handleFilterChange('search', '')}
                className="hover:text-blue-900"
              >
                ×
              </button>
            </span>
          )}
          {filters.language && (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm">
              Language: {filters.language}
              <button
                onClick={() => handleFilterChange('language', '')}
                className="hover:text-green-900"
              >
                ×
              </button>
            </span>
          )}
          {filters.brand && (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-purple-100 text-purple-700 rounded-full text-sm">
              Brand: {filters.brand}
              <button
                onClick={() => handleFilterChange('brand', '')}
                className="hover:text-purple-900"
              >
                ×
              </button>
            </span>
          )}
          {filters.geo && (
            <span className="inline-flex items-center gap-1 px-3 py-1 bg-amber-100 text-amber-700 rounded-full text-sm">
              Geo: {filters.geo}
              <button
                onClick={() => handleFilterChange('geo', '')}
                className="hover:text-amber-900"
              >
                ×
              </button>
            </span>
          )}
        </div>
      )}
    </div>
  );
};

export default SiteFilters;
