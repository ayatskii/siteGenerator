import React, { useState, useEffect } from 'react';
import { Button, Input, Card } from '../ui';
import { useTranslation } from 'react-i18next';
import analyticsService from '../../services/analyticsService';
import { toast } from 'react-toastify';

const UmamiConfigForm = ({ siteId, onConfigSaved }) => {
  const { t } = useTranslation();
  const [formData, setFormData] = useState({
    api_url: '',
    api_token: '',
    umami_site_id: '',
    is_active: true
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    const fetchConfig = async () => {
      try {
        const config = await analyticsService.getUmamiConfig(siteId);
        if (config) {
          setFormData({
            api_url: config.api_url,
            api_token: config.api_token, // Note: This might be masked or encrypted
            umami_site_id: config.umami_site_id,
            is_active: config.is_active
          });
        }
      } catch (error) {
        console.error("Error fetching Umami config:", error);
      } finally {
        setLoading(false);
      }
    };

    if (siteId) {
      fetchConfig();
    }
  }, [siteId]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await analyticsService.saveUmamiConfig(siteId, formData);
      toast.success(t('analytics.configSaved'));
      if (onConfigSaved) onConfigSaved();
    } catch (error) {
      toast.error(t('analytics.configError'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div>{t('analytics.loadingConfig')}</div>;

  return (
    <Card>
      <div className="mb-6">
        <h2 className="text-xl font-semibold text-gray-900">{t('analytics.configureTitle')}</h2>
        <p className="text-gray-600 text-sm mt-1">
          {t('analytics.configureDesc')}
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label={t('analytics.umamiUrl')}
          placeholder={t('analytics.umamiUrlPlaceholder')}
          value={formData.api_url}
          onChange={(e) => setFormData({ ...formData, api_url: e.target.value })}
          required
          helpText={t('analytics.umamiUrlHelp')}
        />

        <Input
          label={t('analytics.siteId')}
          placeholder={t('analytics.siteIdPlaceholder')}
          value={formData.umami_site_id}
          onChange={(e) => setFormData({ ...formData, umami_site_id: e.target.value })}
          required
          helpText={t('analytics.siteIdHelp')}
        />

        <Input
          label={t('analytics.apiToken')}
          type="password"
          placeholder={t('analytics.apiTokenPlaceholder')}
          value={formData.api_token}
          onChange={(e) => setFormData({ ...formData, api_token: e.target.value })}
          required
          helpText={t('analytics.apiTokenHelp')}
        />

        <div className="flex items-center pt-2">
          <input
            type="checkbox"
            id="is_active"
            checked={formData.is_active}
            onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
            className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
          />
          <label htmlFor="is_active" className="ml-2 text-sm text-gray-700">
            {t('analytics.enableIntegration')}
          </label>
        </div>

        <div className="pt-4 flex justify-end">
          <Button type="submit" variant="primary" isLoading={saving}>
            {t('analytics.saveConfig')}
          </Button>
        </div>
      </form>
    </Card>
  );
};

export default UmamiConfigForm;
