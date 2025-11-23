import { useState } from 'react';
import { Link } from 'react-router-dom';
import DuplicateSiteModal from './DuplicateSiteModal';

const SiteCard = ({ site, onDuplicate }) => {
  const [showDuplicateModal, setShowDuplicateModal] = useState(false);
  const [showActions, setShowActions] = useState(false);

  const getStatusBadge = () => {
    const statusConfig = {
      deployed: {
        text: 'Deployed',
        className: 'bg-green-100 text-green-800 border-green-200'
      },
      draft: {
        text: 'Draft',
        className: 'bg-amber-100 text-amber-800 border-amber-200'
      },
      empty: {
        text: 'Empty',
        className: 'bg-gray-100 text-gray-800 border-gray-200'
      }
    };

    const config = statusConfig[site.status] || statusConfig.empty;
    
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium border ${config.className}`}>
        {config.text}
      </span>
    );
  };

  const formatDate = (dateString) => {
    if (!dateString) return 'Never';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  return (
    <>
      <div className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow border border-gray-200">
        {/* Card Header */}
        <div className="p-5 border-b border-gray-200">
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <Link to={`/sites/${site.id}`} className="group">
                <h3 className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 truncate">
                  {site.name || site.domain}
                </h3>
                <p className="text-sm text-gray-500 mt-1 truncate">{site.domain}</p>
              </Link>
            </div>
            
            {/* Actions Menu */}
            <div className="relative ml-3">
              <button
                onClick={() => setShowActions(!showActions)}
                className="p-2 hover:bg-gray-100 rounded-full transition-colors"
              >
                <svg className="w-5 h-5 text-gray-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                </svg>
              </button>
              
              {showActions && (
                <>
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200">
                    <div className="py-1">
                      <Link
                        to={`/sites/${site.id}/analytics`}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        📊 View Analytics
                      </Link>
                      <button
                        onClick={() => {
                          setShowActions(false);
                          setShowDuplicateModal(true);
                        }}
                        className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        📋 Duplicate Site
                      </button>
                      <Link
                        to={`/sites/${site.id}`}
                        className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                      >
                        ⚙️ Settings
                      </Link>
                    </div>
                  </div>
                  <div
                    className="fixed inset-0 z-0"
                    onClick={() => setShowActions(false)}
                  ></div>
                </>
              )}
            </div>
          </div>

          {/* Status Badge */}
          <div className="mt-3">
            {getStatusBadge()}
          </div>
        </div>

        {/* Card Body - Stats */}
        <div className="p-5">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-gray-500 mb-1">Pages</p>
              <p className="text-2xl font-bold text-gray-900">{site.page_count || 0}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 mb-1">Deployments</p>
              <p className="text-2xl font-bold text-gray-900">{site.deployment_count || 0}</p>
            </div>
          </div>

          {/* Additional Info */}
          <div className="mt-4 pt-4 border-t border-gray-200 space-y-2">
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Language:</span>
              <span className="font-medium text-gray-900">{site.language || 'N/A'}</span>
            </div>
            {site.brand_name && (
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-500">Brand:</span>
                <span className="font-medium text-gray-900">{site.brand_name}</span>
              </div>
            )}
            <div className="flex items-center justify-between text-sm">
              <span className="text-gray-500">Last Deployment:</span>
              <span className="font-medium text-gray-900">{formatDate(site.last_deployment_date)}</span>
            </div>
          </div>
        </div>

        {/* Card Footer - Quick Actions */}
        <div className="px-5 py-3 bg-gray-50 border-t border-gray-200 flex gap-2">
          <Link
            to={`/sites/${site.id}/analytics`}
            className="flex-1 text-center px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md transition-colors"
          >
            Analytics
          </Link>
          <Link
            to={`/sites/${site.id}`}
            className="flex-1 text-center px-3 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-md transition-colors"
          >
            Manage
          </Link>
        </div>
      </div>

      {/* Duplicate Modal */}
      {showDuplicateModal && (
        <DuplicateSiteModal
          site={site}
          onClose={() => setShowDuplicateModal(false)}
          onDuplicate={onDuplicate}
        />
      )}
    </>
  );
};

export default SiteCard;
