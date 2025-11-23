import React, { useState, useEffect } from "react";
import { Tabs, Card, Button, Input, Table, Badge, Modal } from "../components/ui";
import { HiPlus, HiPencil, HiTrash, HiGlobe, HiKey, HiLink, HiCode, HiPhotograph } from "react-icons/hi";
import SwiperPresetModal from "../components/SwiperPresetModal";
import api from "../services/api";
import { toast } from "react-toastify";

const Settings = () => {
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
        toast.success("Language updated successfully");
      } else {
        await api.post("/api/languages/", languageForm);
        toast.success("Language created successfully");
      }
      setLanguageModal(false);
      setCurrentLanguage(null);
      setLanguageForm({ code: "", name: "", active: true });
      fetchLanguages();
    } catch (error) {
      toast.error("Failed to save language");
    }
  };

  const handleDeleteLanguage = async (id) => {
    if (!confirm("Are you sure you want to delete this language?")) return;
    try {
      await api.delete(`/api/languages/${id}/`);
      toast.success("Language deleted successfully");
      fetchLanguages();
    } catch (error) {
      toast.error("Failed to delete language");
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
        toast.success("Token updated successfully");
      } else {
        await api.post("/api/tokens/", tokenForm);
        toast.success("Token created successfully");
      }
      setTokenModal(false);
      setCurrentToken(null);
      setTokenForm({ name: "", service_type: "cloudflare", token_value: "" });
      fetchTokens();
    } catch (error) {
      toast.error("Failed to save token");
    }
  };

  const handleDeleteToken = async (id) => {
    if (!confirm("Are you sure you want to delete this token?")) return;
    try {
      await api.delete(`/api/tokens/${id}/`);
      toast.success("Token deleted successfully");
      fetchTokens();
    } catch (error) {
      toast.error("Failed to delete token");
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
        toast.success("Affiliate link updated successfully");
      } else {
        await api.post("/api/affiliates/", {
          ...affiliateForm,
          url: affiliateForm.link_template,
        });
        toast.success("Affiliate link created successfully");
      }
      setAffiliateModal(false);
      setCurrentAffiliate(null);
      setAffiliateForm({ name: "", link_type: "static", link_template: "" });
      fetchAffiliates();
    } catch (error) {
      toast.error("Failed to save affiliate link");
    }
  };

  const handleDeleteAffiliate = async (id) => {
    if (!confirm("Are you sure you want to delete this affiliate link?")) return;
    try {
      await api.delete(`/api/affiliates/${id}/`);
      toast.success("Affiliate link deleted successfully");
      fetchAffiliates();
    } catch (error) {
      toast.error("Failed to delete affiliate link");
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
        toast.success("Preset updated successfully");
      } else {
        await api.post("/api/presets/", presetData);
        toast.success("Preset created successfully");
      }
      setPresetModal(false);
      setCurrentPreset(null);
      fetchPresets();
    } catch (error) {
      console.error("Error saving preset:", error);
      toast.error("Failed to save preset");
    }
  };

  const handleDeletePreset = async (id) => {
    if (!confirm("Are you sure you want to delete this preset?")) return;
    try {
      await api.delete(`/api/presets/${id}/`);
      toast.success("Preset deleted successfully");
      fetchPresets();
    } catch (error) {
      toast.error("Failed to delete preset");
    }
  };

  const tabs = [
    {
      label: "Languages",
      icon: <HiGlobe className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Language Presets</h2>
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
              Add Language
            </Button>
          </div>
          <Table
            columns={[
              { header: "Code", render: (lang) => <span className="font-mono">{lang.code}</span> },
              { header: "Name", accessor: "name" },
              {
                header: "Status",
                render: (lang) => (
                  <Badge variant={lang.active ? "success" : "default"}>
                    {lang.active ? "Active" : "Inactive"}
                  </Badge>
                ),
              },
              {
                header: "Actions",
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
            emptyMessage="No languages configured"
          />
        </div>
      ),
    },
    {
      label: "API Tokens",
      icon: <HiKey className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">API Tokens</h2>
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
              Add Token
            </Button>
          </div>
          <Table
            columns={[
              { header: "Name", accessor: "name" },
              { header: "Service", accessor: "service_type" },
              {
                header: "Token",
                render: (token) => (
                  <div className="flex items-center space-x-2">
                    <span className="font-mono text-sm">
                      {showToken[token.id] ? token.token_value : "••••••••••••"}
                    </span>
                    <button
                      onClick={() => setShowToken({ ...showToken, [token.id]: !showToken[token.id] })}
                      className="text-blue-600 hover:text-blue-800 text-xs"
                    >
                      {showToken[token.id] ? "Hide" : "Show"}
                    </button>
                  </div>
                ),
              },
              {
                header: "Actions",
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
            emptyMessage="No API tokens configured"
          />
        </div>
      ),
    },
    {
      label: "Affiliate Links",
      icon: <HiLink className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Affiliate Links</h2>
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
              Add Link
            </Button>
          </div>
          <Table
            columns={[
              { header: "Name", accessor: "name" },
              { header: "Type", accessor: "link_type" },
              {
                header: "Template",
                render: (aff) => <span className="font-mono text-sm truncate max-w-xs block">{aff.link_template}</span>,
              },
              {
                header: "Actions",
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
            emptyMessage="No affiliate links configured"
          />
        </div>
      ),
    },
    {
      label: "Swiper Presets",
      icon: <HiCode className="w-5 h-5" />,
      content: (
        <div>
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold text-gray-900">Swiper Presets</h2>
            <Button
              variant="primary"
              size="sm"
              icon={<HiPlus className="w-4 h-4" />}
              onClick={() => {
                setCurrentPreset(null);
                setPresetModal(true);
              }}
            >
              Add Preset
            </Button>
          </div>
          <Table
            columns={[
              { header: "Name", accessor: "name" },
              { 
                header: "Slides", 
                render: (preset) => (
                  <Badge variant="gray">{preset.items?.length || 0} slides</Badge>
                )
              },
              { header: "Button Text", accessor: "button_text" },
              {
                header: "Actions",
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
            emptyMessage="No swiper presets configured"
          />
        </div>
      ),
    },

  ];

  return (
    <div className="max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="mt-1 text-sm text-gray-600">
          Manage languages, API tokens, and affiliate links
        </p>
      </div>

      <Card padding="none">
        <Tabs tabs={tabs} />
      </Card>

      {/* Language Modal */}
      <Modal
        isOpen={languageModal}
        onClose={() => setLanguageModal(false)}
        title={currentLanguage ? "Edit Language" : "Add Language"}
        footer={
          <>
            <Button variant="secondary" onClick={() => setLanguageModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveLanguage}>
              Save
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Language Code"
            value={languageForm.code}
            onChange={(e) => setLanguageForm({ ...languageForm, code: e.target.value })}
            placeholder="en-US"
            required
          />
          <Input
            label="Language Name"
            value={languageForm.name}
            onChange={(e) => setLanguageForm({ ...languageForm, name: e.target.value })}
            placeholder="English (US)"
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
              Active
            </label>
          </div>
        </div>
      </Modal>

      {/* Token Modal */}
      <Modal
        isOpen={tokenModal}
        onClose={() => setTokenModal(false)}
        title={currentToken ? "Edit API Token" : "Add API Token"}
        footer={
          <>
            <Button variant="secondary" onClick={() => setTokenModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveToken}>
              Save
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Token Name"
            value={tokenForm.name}
            onChange={(e) => setTokenForm({ ...tokenForm, name: e.target.value })}
            placeholder="My Cloudflare Token"
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Service Type</label>
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
            label="Token Value"
            value={tokenForm.token_value}
            onChange={(e) => setTokenForm({ ...tokenForm, token_value: e.target.value })}
            placeholder="Enter API token"
            type="password"
            required
          />
        </div>
      </Modal>

      {/* Affiliate Modal */}
      <Modal
        isOpen={affiliateModal}
        onClose={() => setAffiliateModal(false)}
        title={currentAffiliate ? "Edit Affiliate Link" : "Add Affiliate Link"}
        footer={
          <>
            <Button variant="secondary" onClick={() => setAffiliateModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleSaveAffiliate}>
              Save
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label="Link Name"
            value={affiliateForm.name}
            onChange={(e) => setAffiliateForm({ ...affiliateForm, name: e.target.value })}
            placeholder="Amazon Associates"
            required
          />
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Link Type</label>
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
            <label className="block text-sm font-medium text-gray-700 mb-1">Link Template</label>
            <textarea
              value={affiliateForm.link_template}
              onChange={(e) => setAffiliateForm({ ...affiliateForm, link_template: e.target.value })}
              placeholder="https://example.com?ref=YOUR_ID"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              required
            />
            <p className="mt-1 text-xs text-gray-500">Use {"{product_id}"} for dynamic parameters</p>
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
