import React, { useState, useEffect } from "react";
import { Tabs, Card, Button, Input, Table, Badge, Modal } from "../components/ui";
import { HiPlus, HiPencil, HiTrash, HiGlobe, HiKey, HiLink, HiCode } from "react-icons/hi";
import SwiperPresetModal from "../components/SwiperPresetModal";
import api from "../services/api";
import { toast } from "react-toastify";
import { useTranslation } from "react-i18next";

const Settings = () => {
  const { t } = useTranslation();

  // Languages State
  const [languages, setLanguages] = useState([]);
  const [languageModal, setLanguageModal] = useState(false);
  const [currentLanguage, setCurrentLanguage] = useState(null);
  const [languageForm, setLanguageForm] = useState({ code: "", name: "", active: true });

  // API Tokens State
  const [tokens, setTokens] = useState([]);
  const [tokenModal, setTokenModal] = useState(false);
  const [currentToken, setCurrentToken] = useState(null);
  const [tokenForm, setTokenForm] = useState({ name: "", service_type: "cloudflare", token_value: "" });
  const [showToken, setShowToken] = useState({});

  // Affiliate Links State
  const [affiliates, setAffiliates] = useState([]);
  const [affiliateModal, setAffiliateModal] = useState(false);
  const [currentAffiliate, setCurrentAffiliate] = useState(null);
  const [affiliateForm, setAffiliateForm] = useState({ name: "", link_type: "static", link_template: "" });

  // Swiper Presets State
  const [presets, setPresets] = useState([]);
  const [presetModal, setPresetModal] = useState(false);
  const [currentPreset, setCurrentPreset] = useState(null);

  useEffect(() => {
    fetchLanguages();
    fetchTokens();
    fetchAffiliates();
    fetchPresets();
  }, []);

  // Languages CRUD
  const fetchLanguages = async () => {
    try {
      const response = await api.get("/api/languages/");
      setLanguages(response.data);
    } catch (error) {
      console.error("Error fetching languages:", error);
    }
  };

  const handleSaveLanguage = async () => {
    try {
      if (currentLanguage) {
        await api.put(`/api/languages/${currentLanguage.id}/`, languageForm);
        toast.success(t('settings.languages.updateSuccess'));
      } else {
        await api.post("/api/languages/", languageForm);
        toast.success(t('settings.languages.createSuccess'));
      }
      setLanguageModal(false);
      setCurrentLanguage(null);
      setLanguageForm({ code: "", name: "", active: true });
      fetchLanguages();
    } catch (error) {
      toast.error(t('settings.languages.saveError'));
    }
  };

  const handleDeleteLanguage = async (id) => {
    if (!confirm(t('settings.languages.deleteConfirm'))) return;
    try {
      await api.delete(`/api/languages/${id}/`);
      toast.success(t('settings.languages.deleteSuccess'));
      fetchLanguages();
    } catch (error) {
      toast.error(t('settings.languages.deleteError'));
    }
  };

  // API Tokens CRUD
  const fetchTokens = async () => {
    try {
      const response = await api.get("/api/tokens/");
      setTokens(response.data);
    } catch (error) {
      console.error("Error fetching tokens:", error);
    }
  };

  const handleSaveToken = async () => {
    try {
      if (currentToken) {
        await api.put(`/api/tokens/${currentToken.id}/`, tokenForm);
        toast.success(t('settings.tokens.updateSuccess'));
      } else {
        await api.post("/api/tokens/", tokenForm);
        toast.success(t('settings.tokens.createSuccess'));
      }
      setTokenModal(false);
      setCurrentToken(null);
      setTokenForm({ name: "", service_type: "cloudflare", token_value: "" });
      fetchTokens();
    } catch (error) {
      toast.error(t('settings.tokens.saveError'));
    }
  };

  const handleDeleteToken = async (id) => {
    if (!confirm(t('settings.tokens.deleteConfirm'))) return;
    try {
      await api.delete(`/api/tokens/${id}/`);
      toast.success(t('settings.tokens.deleteSuccess'));
      fetchTokens();
    } catch (error) {
      toast.error(t('settings.tokens.deleteError'));
    }
  };

  // Affiliate Links CRUD
  const fetchAffiliates = async () => {
    try {
      const response = await api.get("/api/affiliates/");
      setAffiliates(response.data);
    } catch (error) {
      console.error("Error fetching affiliates:", error);
    }
  };

  const handleSaveAffiliate = async () => {
    try {
      if (currentAffiliate) {
        await api.patch(`/api/affiliates/${currentAffiliate.id}/`, {
          ...affiliateForm,
          url: affiliateForm.link_template,
        });
        toast.success(t('settings.affiliates.updateSuccess'));
      } else {
        await api.post("/api/affiliates/", {
          ...affiliateForm,
          url: affiliateForm.link_template,
        });
        toast.success(t('settings.affiliates.createSuccess'));
      }
      setAffiliateModal(false);
      setCurrentAffiliate(null);
      setAffiliateForm({ name: "", link_type: "static", link_template: "" });
      fetchAffiliates();
    } catch (error) {
      toast.error(t('settings.affiliates.saveError'));
    }
  };

  const handleDeleteAffiliate = async (id) => {
    if (!confirm(t('settings.affiliates.deleteConfirm'))) return;
    try {
      await api.delete(`/api/affiliates/${id}/`);
      toast.success(t('settings.affiliates.deleteSuccess'));
      fetchAffiliates();
    } catch (error) {
      toast.error(t('settings.affiliates.deleteError'));
    }
  };

  // Swiper Presets CRUD
  const fetchPresets = async () => {
    try {
      const response = await api.get("/api/presets/");
      setPresets(response.data);
    } catch (error) {
      console.error("Error fetching presets:", error);
    }
  };

  const handleSavePreset = async (presetData) => {
    try {
      if (currentPreset) {
        await api.patch(`/api/presets/${currentPreset.id}/`, presetData);
        toast.success(t('settings.presets.updateSuccess'));
      } else {
        await api.post("/api/presets/", presetData);
        toast.success(t('settings.presets.createSuccess'));
      }
      setPresetModal(false);
      setCurrentPreset(null);
      fetchPresets();
    } catch (error) {
      console.error("Error saving preset:", error);
      toast.error(t('settings.presets.saveError'));
    }
  };

  const handleDeletePreset = async (id) => {
    if (!confirm(t('settings.presets.deleteConfirm'))) return;
    try {
      await api.delete(`/api/presets/${id}/`);
      toast.success(t('settings.presets.deleteSuccess'));
      fetchPresets();
    } catch (error) {
      toast.error(t('settings.presets.deleteError'));
    }
  };

  const tabs = [
    {
      label: t('settings.tabs.languages'),
      icon: <HiGlobe className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">{t('settings.languages.title')}</h2>
            <Button
              variant="primary"
              size="sm"
              icon={<HiPlus className="w-4 h-4" />}
              onClick={() => {
                setCurrentLanguage(null);
                setLanguageForm({ code: "", name: "", active: true });
                setLanguageModal(true);
              }}
            >
              {t('settings.languages.add')}
            </Button>
          </div>
          <Table
            columns={[
              { header: t('settings.languages.code'), render: (lang) => <span className="font-mono">{lang.code}</span> },
              { header: t('settings.languages.name'), accessor: "name" },
              {
                header: t('settings.languages.status'),
                render: (lang) => (
                  <Badge variant={lang.active ? "success" : "default"}>
                    {lang.active ? t('settings.languages.active') : t('settings.languages.inactive')}
                  </Badge>
                ),
              },
              {
                header: t('settings.languages.actions'),
                render: (lang) => (
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setCurrentLanguage(lang);
                        setLanguageForm({ code: lang.code, name: lang.name, active: lang.active });
                        setLanguageModal(true);
                      }}
                    >
                      <HiPencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteLanguage(lang.id)}
                    >
                      <HiTrash className="w-4 h-4 text-red-600" />
                    </Button>
                  </div>
                ),
              },
            ]}
            data={languages}
            emptyMessage={t('settings.languages.empty')}
          />
        </div>
      ),
    },
    {
      label: t('settings.tabs.apiTokens'),
      icon: <HiKey className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">{t('settings.tokens.title')}</h2>
            <Button
              variant="primary"
              size="sm"
              icon={<HiPlus className="w-4 h-4" />}
              onClick={() => {
                setCurrentToken(null);
                setTokenForm({ name: "", service_type: "cloudflare", token_value: "" });
                setTokenModal(true);
              }}
            >
              {t('settings.tokens.add')}
            </Button>
          </div>
          <Table
            columns={[
              { header: t('settings.tokens.name'), accessor: "name" },
              { header: t('settings.tokens.service'), accessor: "service_type" },
              {
                header: t('settings.tokens.token'),
                render: (token) => (
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-sm">
                      {showToken[token.id] ? token.token_value : "••••••••••••"}
                    </span>
                    <button
                      onClick={() => setShowToken({ ...showToken, [token.id]: !showToken[token.id] })}
                      className="text-blue-600 hover:text-blue-800 text-xs"
                    >
                      {showToken[token.id] ? t('settings.tokens.hide') : t('settings.tokens.show')}
                    </button>
                  </div>
                ),
              },
              {
                header: t('settings.languages.actions'),
                render: (token) => (
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setCurrentToken(token);
                        setTokenForm({ name: token.name, service_type: token.service_type, token_value: token.token_value });
                        setTokenModal(true);
                      }}
                    >
                      <HiPencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteToken(token.id)}
                    >
                      <HiTrash className="w-4 h-4 text-red-600" />
                    </Button>
                  </div>
                ),
              },
            ]}
            data={tokens}
            emptyMessage={t('settings.tokens.empty')}
          />
        </div>
      ),
    },
    {
      label: t('settings.tabs.affiliateLinks'),
      icon: <HiLink className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">{t('settings.affiliates.title')}</h2>
            <Button
              variant="primary"
              size="sm"
              icon={<HiPlus className="w-4 h-4" />}
              onClick={() => {
                setCurrentAffiliate(null);
                setAffiliateForm({ name: "", link_type: "static", link_template: "" });
                setAffiliateModal(true);
              }}
            >
              {t('settings.affiliates.add')}
            </Button>
          </div>
          <Table
            columns={[
              { header: t('settings.affiliates.name'), accessor: "name" },
              { header: t('settings.affiliates.type'), accessor: "link_type" },
              {
                header: t('settings.affiliates.template'),
                render: (aff) => <span className="font-mono text-sm truncate max-w-xs block">{aff.link_template}</span>,
              },
              {
                header: t('settings.languages.actions'),
                render: (aff) => (
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setCurrentAffiliate(aff);
                        setAffiliateForm({ name: aff.name, link_type: aff.link_type, link_template: aff.link_template });
                        setAffiliateModal(true);
                      }}
                    >
                      <HiPencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteAffiliate(aff.id)}
                    >
                      <HiTrash className="w-4 h-4 text-red-600" />
                    </Button>
                  </div>
                ),
              },
            ]}
            data={affiliates}
            emptyMessage={t('settings.affiliates.empty')}
          />
        </div>
      ),
    },
    {
      label: t('settings.tabs.swiperPresets'),
      icon: <HiCode className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">{t('settings.presets.title')}</h2>
            <Button
              variant="primary"
              size="sm"
              icon={<HiPlus className="w-4 h-4" />}
              onClick={() => {
                setCurrentPreset(null);
                setPresetModal(true);
              }}
            >
              {t('settings.presets.add')}
            </Button>
          </div>
          <Table
            columns={[
              { header: t('settings.presets.name'), accessor: "name" },
              { 
                header: t('settings.presets.slides'), 
                render: (preset) => (
                  <Badge variant="gray">{t('settings.presets.slidesCount', { count: preset.items?.length || 0 })}</Badge>
                )
              },
              { header: t('settings.presets.buttonText'), accessor: "button_text" },
              {
                header: t('settings.languages.actions'),
                render: (preset) => (
                  <div className="flex space-x-2">
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => {
                        setCurrentPreset(preset);
                        setPresetModal(true);
                      }}
                    >
                      <HiPencil className="w-4 h-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeletePreset(preset.id)}
                    >
                      <HiTrash className="w-4 h-4 text-red-600" />
                    </Button>
                  </div>
                ),
              },
            ]}
            data={presets}
            emptyMessage={t('settings.presets.empty')}
          />
        </div>
      ),
    },

  ];

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">{t('settings.title')}</h1>
        <p className="mt-1 text-sm text-gray-600">
          {t('settings.subtitle')}
        </p>
      </div>

      <Card padding="none">
        <Tabs tabs={tabs} />
      </Card>

      {/* Language Modal */}
      <Modal
        isOpen={languageModal}
        onClose={() => setLanguageModal(false)}
        title={currentLanguage ? t('settings.languages.editTitle') : t('settings.languages.addTitle')}
        footer={
          <>
            <Button variant="secondary" onClick={() => setLanguageModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" onClick={handleSaveLanguage}>
              {t('common.save')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label={t('settings.languages.codeLabel')}
            value={languageForm.code}
            onChange={(e) => setLanguageForm({ ...languageForm, code: e.target.value })}
            placeholder={t('settings.languages.codePlaceholder')}
            required
          />
          <Input
            label={t('settings.languages.nameLabel')}
            value={languageForm.name}
            onChange={(e) => setLanguageForm({ ...languageForm, name: e.target.value })}
            placeholder={t('settings.languages.namePlaceholder')}
            required
          />
          <div className="flex items-center">
            <input
              type="checkbox"
              id="active"
              checked={languageForm.active}
              onChange={(e) => setLanguageForm({ ...languageForm, active: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="active" className="ml-2 text-sm text-gray-700">
              {t('settings.languages.activeLabel')}
            </label>
          </div>
        </div>
      </Modal>

      {/* Token Modal */}
      <Modal
        isOpen={tokenModal}
        onClose={() => setTokenModal(false)}
        title={currentToken ? t('settings.tokens.editTitle') : t('settings.tokens.addTitle')}
        footer={
          <>
            <Button variant="secondary" onClick={() => setTokenModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" onClick={handleSaveToken}>
              {t('common.save')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label={t('settings.tokens.nameLabel')}
            value={tokenForm.name}
            onChange={(e) => setTokenForm({ ...tokenForm, name: e.target.value })}
            placeholder={t('settings.tokens.namePlaceholder')}
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.tokens.serviceLabel')}</label>
            <select
              value={tokenForm.service_type}
              onChange={(e) => setTokenForm({ ...tokenForm, service_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="cloudflare">Cloudflare</option>
              <option value="openai">OpenAI</option>
              <option value="other">Other</option>
            </select>
          </div>
          <Input
            label={t('settings.tokens.valueLabel')}
            value={tokenForm.token_value}
            onChange={(e) => setTokenForm({ ...tokenForm, token_value: e.target.value })}
            placeholder={t('settings.tokens.valuePlaceholder')}
            type="password"
            required
          />
        </div>
      </Modal>

      {/* Affiliate Modal */}
      <Modal
        isOpen={affiliateModal}
        onClose={() => setAffiliateModal(false)}
        title={currentAffiliate ? t('settings.affiliates.editTitle') : t('settings.affiliates.addTitle')}
        footer={
          <>
            <Button variant="secondary" onClick={() => setAffiliateModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" onClick={handleSaveAffiliate}>
              {t('common.save')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label={t('settings.affiliates.nameLabel')}
            value={affiliateForm.name}
            onChange={(e) => setAffiliateForm({ ...affiliateForm, name: e.target.value })}
            placeholder={t('settings.affiliates.namePlaceholder')}
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.affiliates.typeLabel')}</label>
            <select
              value={affiliateForm.link_type}
              onChange={(e) => setAffiliateForm({ ...affiliateForm, link_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="static">Static</option>
              <option value="dynamic">Dynamic</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('settings.affiliates.templateLabel')}</label>
            <textarea
              value={affiliateForm.link_template}
              onChange={(e) => setAffiliateForm({ ...affiliateForm, link_template: e.target.value })}
              placeholder={t('settings.affiliates.templatePlaceholder')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="mt-1 text-xs text-gray-500">{t('settings.affiliates.templateHelp')}</p>
          </div>
        </div>
      </Modal>

      {/* Swiper Preset Modal */}
      <SwiperPresetModal
        isOpen={presetModal}
        onClose={() => {
          setPresetModal(false);
          setCurrentPreset(null);
        }}
        onSave={handleSavePreset}
        preset={currentPreset}
      />
    </div>
  );
};

export default Settings;
