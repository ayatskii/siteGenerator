import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Analytics Service
 * Handles all API calls related to analytics data
 */
class AnalyticsService {
  /**
   * Get full analytics data for a site
   * @param {number} siteId - Site ID
   * @param {Date|string} startDate - Start date (YYYY-MM-DD)
   * @param {Date|string} endDate - End date (YYYY-MM-DD)
   * @returns {Promise} Analytics data
   */
  async getAnalytics(siteId, startDate, endDate) {
    try {
      const params = {};
      if (startDate) {
        params.start_date = typeof startDate === 'string' ? startDate : startDate.toISOString().split('T')[0];
      }
      if (endDate) {
        params.end_date = typeof endDate === 'string' ? endDate : endDate.toISOString().split('T')[0];
      }

      const response = await axios.get(
        `${API_BASE_URL}/api/analytics/sites/${siteId}/`,
        {
          params,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error fetching analytics:', error);
      throw error;
    }
  }

  /**
   * Get analytics summary for a site
   * @param {number} siteId - Site ID
   * @param {Date|string} startDate - Start date (YYYY-MM-DD)
   * @param {Date|string} endDate - End date (YYYY-MM-DD)
   * @returns {Promise} Analytics summary
   */
  async getSummary(siteId, startDate, endDate) {
    try {
      const params = {};
      if (startDate) {
        params.start_date = typeof startDate === 'string' ? startDate : startDate.toISOString().split('T')[0];
      }
      if (endDate) {
        params.end_date = typeof endDate === 'string' ? endDate : endDate.toISOString().split('T')[0];
      }

      const response = await axios.get(
        `${API_BASE_URL}/api/analytics/sites/${siteId}/summary/`,
        {
          params,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error fetching analytics summary:', error);
      throw error;
    }
  }

  /**
   * Export analytics data
   * @param {number} siteId - Site ID
   * @param {string} format - Export format ('csv' or 'pdf')
   * @param {Date|string} startDate - Start date (YYYY-MM-DD)
   * @param {Date|string} endDate - End date (YYYY-MM-DD)
   * @returns {Promise} Blob download
   */
  async exportData(siteId, format = 'csv', startDate, endDate) {
    try {
      const params = { format };
      if (startDate) {
        params.start_date = typeof startDate === 'string' ? startDate : startDate.toISOString().split('T')[0];
      }
      if (endDate) {
        params.end_date = typeof endDate === 'string' ? endDate : endDate.toISOString().split('T')[0];
      }

      const response = await axios.get(
        `${API_BASE_URL}/api/analytics/sites/${siteId}/export/`,
        {
          params,
          responseType: 'blob',
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      
      const contentDisposition = response.headers['content-disposition'];
      let filename = `analytics_${siteId}_${new Date().toISOString().split('T')[0]}.${format}`;
      
      if (contentDisposition) {
        const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
        if (filenameMatch) {
          filename = filenameMatch[1];
        }
      }
      
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);

      return true;
    } catch (error) {
      console.error('Error exporting analytics:', error);
      throw error;
    }
  }
  /**
   * Get Umami configuration for a site
   * @param {number} siteId - Site ID
   * @returns {Promise} Umami config
   */
  async getUmamiConfig(siteId) {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/umami-configs/?site_id=${siteId}`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );
      // Return the first config found (since we filter by site)
      return response.data.length > 0 ? response.data[0] : null;
    } catch (error) {
      console.error('Error fetching Umami config:', error);
      throw error;
    }
  }

  /**
   * Save Umami configuration for a site
   * @param {number} siteId - Site ID
   * @param {Object} config - Config data (api_url, api_token, umami_site_id)
   * @returns {Promise} Saved config
   */
  async saveUmamiConfig(siteId, config) {
    try {
      // First check if config exists
      const existingConfig = await this.getUmamiConfig(siteId);
      
      let response;
      if (existingConfig) {
        // Update
        response = await axios.patch(
          `${API_BASE_URL}/api/umami-configs/${existingConfig.id}/`,
          { ...config, site: siteId },
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          }
        );
      } else {
        // Create
        response = await axios.post(
          `${API_BASE_URL}/api/umami-configs/`,
          { ...config, site: siteId },
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
          }
        );
      }
      return response.data;
    } catch (error) {
      console.error('Error saving Umami config:', error);
      throw error;
    }
  }
}

export default new AnalyticsService();
