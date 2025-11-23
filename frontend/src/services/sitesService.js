import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * Sites Service
 * Handles all API calls related to sites and admin dashboard
 */
class SitesService {
  /**
   * Get dashboard statistics
   * @returns {Promise} Dashboard statistics
   */
  async getDashboardStatistics() {
    try {
      const response = await axios.get(
        `${API_BASE_URL}/api/sites/statistics/`,
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error fetching dashboard statistics:', error);
      throw error;
    }
  }

  /**
   * Get filtered site list
   * @param {Object} filters - Filter parameters
   * @returns {Promise} Filtered sites list
   */
  async getFilteredSites(filters = {}) {
    try {
      const params = {};
      if (filters.language) params.language = filters.language;
      if (filters.brand) params.brand = filters.brand;
      if (filters.geo) params.geo = filters.geo;
      if (filters.search) params.search = filters.search;

      const response = await axios.get(
        `${API_BASE_URL}/api/sites/list_filtered/`,
        {
          params,
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error fetching filtered sites:', error);
      throw error;
    }
  }

  /**
   * Duplicate a site
   * @param {number} siteId - Site ID to duplicate
   * @returns {Promise} New site data
   */
  async duplicateSite(siteId) {
    try {
      const response = await axios.post(
        `${API_BASE_URL}/api/sites/${siteId}/duplicate/`,
        {},
        {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error duplicating site:', error);
      throw error;
    }
  }
}

export default new SitesService();
