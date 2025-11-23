import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import MediaLibrarySelector from "../components/MediaLibrarySelector";

const CreateSite = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [tokens, setTokens] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [affiliateLinks, setAffiliateLinks] = useState([]);
  const [mediaSelectorOpen, setMediaSelectorOpen] = useState(false);
  const [mediaSelectorTarget, setMediaSelectorTarget] = useState(null); // 'logo' or 'favicon'

  // Form State
  const [formData, setFormData] = useState({
    domain: "",
    cloudflare_token_id: null,
    brand_name: "",
    language: "en-US",
    geo_targeting: "",
    affiliate_link_id: null,
    template_id: null,
    fingerprint_type: "random_class",
    allow_indexing: true,
    redirect_404_to_homepage: false,
    force_www: false,
    page_speed_optimization: false,
    logo_url: "",
    favicon_url: "",
    copyright_year: new Date().getFullYear(),
    pages_structure: [],
    footer_images: [],
    header_cta_config: {},
    microdata_settings: {},
  });

  // Fetch initial data
  useEffect(() => {
    const fetchData = async () => {
      try {
        const tokenRes = await axios.get("http://localhost:8000/api/tokens/");
        const templateRes = await axios.get(
          "http://localhost:8000/api/templates/"
        );
        // const affiliateRes = await axios.get('http://localhost:8000/api/affiliates/'); // Assuming endpoint exists

        setTokens(tokenRes.data.filter((t) => t.service_type === "cloudflare"));
        setTemplates(templateRes.data);
        // setAffiliateLinks(affiliateRes.data);
      } catch (error) {
        console.error("Error fetching data", error);
      }
    };
    fetchData();
  }, []);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleTokenSelect = (tokenId) => {
    setFormData((prev) => ({ ...prev, cloudflare_token_id: tokenId }));
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert("Copied to clipboard!");
  };

  const handleMediaSelect = (asset) => {
    const assetUrl = asset.file || asset.file_url;
    if (mediaSelectorTarget === 'logo') {
      setFormData(prev => ({ ...prev, logo_url: assetUrl }));
    } else if (mediaSelectorTarget === 'favicon') {
      setFormData(prev => ({ ...prev, favicon_url: assetUrl }));
    }
    setMediaSelectorOpen(false);
    setMediaSelectorTarget(null);
  };


  const handleSubmit = async () => {
    setLoading(true);
    try {
      const response = await axios.post(
        "http://localhost:8000/api/sites/create_site/",
        formData,
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );
      if (response.data.status === "success") {
        alert("Site created successfully!");
        navigate("/pages"); // Redirect to pages view
      }
    } catch (error) {
      console.error("Error creating site", error);
      alert(
        "Failed to create site: " +
          (error.response?.data?.error || error.message)
      );
    } finally {
      setLoading(false);
    }
  };

  // Render Steps
  const renderStep1 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">
        Step 1: Domain & Token Selection
      </h2>

      <div>
        <label className="block text-sm font-medium text-gray-300">
          Domain Name
        </label>
        <input
          type="text"
          name="domain"
          value={formData.domain}
          onChange={handleInputChange}
          placeholder="example.com"
          className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
        />
        <p className="text-xs text-gray-400 mt-1">
          Enter domain without protocol (http/https)
        </p>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Select Cloudflare Token
        </label>
        <div className="overflow-hidden shadow ring-1 ring-black ring-opacity-5 sm:rounded-lg">
          <table className="min-w-full divide-y divide-gray-700">
            <thead className="bg-gray-800">
              <tr>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider"
                >
                  Select
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider"
                >
                  Token Name
                </th>
                <th
                  scope="col"
                  className="px-6 py-3 text-left text-xs font-medium text-gray-300 uppercase tracking-wider"
                >
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-gray-700 divide-y divide-gray-600">
              {tokens.map((token) => (
                <tr key={token.id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <input
                      type="radio"
                      name="cloudflare_token_id"
                      checked={formData.cloudflare_token_id === token.id}
                      onChange={() => handleTokenSelect(token.id)}
                      className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300"
                    />
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-200">
                    {token.name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <button
                      onClick={() =>
                        copyToClipboard(
                          "ns1.cloudflare.com\nns2.cloudflare.com"
                        )
                      }
                      className="text-indigo-400 hover:text-indigo-300"
                    >
                      Copy NS Records
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={() => setStep(2)}
          disabled={!formData.domain || !formData.cloudflare_token_id}
          className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          Continue Site Configuration
        </button>
      </div>
    </div>
  );

  const renderStep2 = () => (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-white">
        Step 2: Site Configuration
      </h2>

      {/* Brand Settings */}
      <div className="bg-gray-800 p-4 rounded-md">
        <h3 className="text-lg font-medium text-white mb-4">Brand Settings</h3>
        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
          <div className="sm:col-span-3">
            <label className="block text-sm font-medium text-gray-300">
              Brand Name
            </label>
            <input
              type="text"
              name="brand_name"
              value={formData.brand_name}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            />
          </div>
          <div className="sm:col-span-3">
            <label className="block text-sm font-medium text-gray-300">
              Language
            </label>
            <select
              name="language"
              value={formData.language}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            >
              <option value="en-US">English (US)</option>
              <option value="es-ES">Spanish</option>
              <option value="fr-FR">French</option>
              {/* Add more languages */}
            </select>
          </div>

          {/* Logo */}
          <div className="sm:col-span-3">
            <label className="block text-sm font-medium text-gray-300">
              Logo URL
            </label>
            <div className="mt-1 flex gap-2">
              <input
                type="text"
                name="logo_url"
                value={formData.logo_url}
                onChange={handleInputChange}
                placeholder="https://..."
                className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
              />
              <button
                type="button"
                onClick={() => {
                  setMediaSelectorTarget('logo');
                  setMediaSelectorOpen(true);
                }}
                className="inline-flex items-center px-3 py-2 border border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-300 bg-gray-700 hover:bg-gray-600"
              >
                Browse
              </button>
            </div>
          </div>

          {/* Favicon */}
          <div className="sm:col-span-3">
            <label className="block text-sm font-medium text-gray-300">
              Favicon URL
            </label>
            <div className="mt-1 flex gap-2">
              <input
                type="text"
                name="favicon_url"
                value={formData.favicon_url}
                onChange={handleInputChange}
                placeholder="https://..."
                className="block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
              />
              <button
                type="button"
                onClick={() => {
                  setMediaSelectorTarget('favicon');
                  setMediaSelectorOpen(true);
                }}
                className="inline-flex items-center px-3 py-2 border border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-300 bg-gray-700 hover:bg-gray-600"
              >
                Browse
              </button>
            </div>
            <p className="text-xs text-gray-400 mt-1">SVG recommended for auto-generation</p>
          </div>

          {/* Copyright Year */}
          <div className="sm:col-span-3">
            <label className="block text-sm font-medium text-gray-300">
              Copyright Year
            </label>
            <input
              type="number"
              name="copyright_year"
              value={formData.copyright_year}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            />
          </div>
        </div>
      </div>

      {/* Template Selection */}
      <div className="bg-gray-800 p-4 rounded-md">
        <h3 className="text-lg font-medium text-white mb-4">
          Template & Fingerprint
        </h3>
        <div className="grid grid-cols-1 gap-y-6 gap-x-4 sm:grid-cols-6">
          <div className="sm:col-span-3">
            <label className="block text-sm font-medium text-gray-300">
              Template
            </label>
            <select
              name="template_id"
              value={formData.template_id || ""}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            >
              <option value="">Select a Template</option>
              {templates.map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          </div>
          <div className="sm:col-span-3">
            <label className="block text-sm font-medium text-gray-300">
              Fingerprint Type
            </label>
            <select
              name="fingerprint_type"
              value={formData.fingerprint_type}
              onChange={handleInputChange}
              className="mt-1 block w-full rounded-md border-gray-600 bg-gray-700 text-white shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm p-2"
            >
              <option value="random_class">Random Class Names</option>
              <option value="preset_scheme">Preset Naming Scheme</option>
              <option value="wordpress">WordPress Footprint</option>
              <option value="other_cms">Other CMS Footprint</option>
            </select>
          </div>
        </div>
      </div>

      {/* SEO & Cloudflare */}
      <div className="bg-gray-800 p-4 rounded-md">
        <h3 className="text-lg font-medium text-white mb-4">
          SEO & Cloudflare Rules
        </h3>
        <div className="space-y-4">
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                name="allow_indexing"
                type="checkbox"
                checked={formData.allow_indexing}
                onChange={handleInputChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <label className="font-medium text-gray-300">
                Allow Search Engine Indexing
              </label>
              <p className="text-gray-500">
                If unchecked, adds noindex meta tag.
              </p>
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                name="redirect_404_to_homepage"
                type="checkbox"
                checked={formData.redirect_404_to_homepage}
                onChange={handleInputChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <label className="font-medium text-gray-300">
                Redirect 404 to Homepage
              </label>
            </div>
          </div>
          <div className="flex items-start">
            <div className="flex items-center h-5">
              <input
                name="force_www"
                type="checkbox"
                checked={formData.force_www}
                onChange={handleInputChange}
                className="focus:ring-indigo-500 h-4 w-4 text-indigo-600 border-gray-300 rounded"
              />
            </div>
            <div className="ml-3 text-sm">
              <label className="font-medium text-gray-300">
                Force WWW Version
              </label>
            </div>
          </div>
        </div>
      </div>

      <div className="flex justify-between">
        <button
          onClick={() => setStep(1)}
          className="py-2 px-4 border border-gray-600 shadow-sm text-sm font-medium rounded-md text-gray-300 hover:bg-gray-700"
        >
          Back
        </button>
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {loading ? "Creating Site..." : "Create Site"}
        </button>
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-900 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {step === 1 && renderStep1()}
        {step === 2 && renderStep2()}

        {/* Media Library Selector Modal */}
        <MediaLibrarySelector
          isOpen={mediaSelectorOpen}
          onClose={() => {
            setMediaSelectorOpen(false);
            setMediaSelectorTarget(null);
          }}
          onSelect={handleMediaSelect}
          title={`Select ${mediaSelectorTarget === 'logo' ? 'Logo' : 'Favicon'}`}
        />
      </div>
    </div>
  );
};

export default CreateSite;

