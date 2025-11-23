import React, { useState, useEffect, useRef } from "react";
import { Card, Button, Badge, Table, Modal, Input, Spinner } from "../components/ui";
import { HiUpload, HiTemplate, HiTrash, HiPencil, HiDownload, HiCheckCircle, HiPlus, HiEye } from "react-icons/hi";
import { useTranslation } from "react-i18next";
import api from "../services/api";
import { toast } from "react-toastify";

const Templates = () => {
  const { t } = useTranslation();
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(true);
  const [uploadModal, setUploadModal] = useState(false);
  const [editModal, setEditModal] = useState(false);
  const [detailsModal, setDetailsModal] = useState(false);
  const [currentTemplate, setCurrentTemplate] = useState(null);
  const [uploadFile, setUploadFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const fileInputRef = useRef(null);

  const [createModal, setCreateModal] = useState(false);
  const [templateForm, setTemplateForm] = useState({
    name: "",
    description: "",
    type: "MONOLITHIC",
    content: "<html>\n  <body>\n    <h1>{{ page_title }}</h1>\n    <div>{{ content }}</div>\n  </body>\n</html>",
    is_default: false,
  });

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    setLoading(true);
    try {
      const response = await api.get("/api/templates/");
      setTemplates(response.data);
    } catch (error) {
      console.error("Error fetching templates:", error);
      toast.error(t('templates.loadError') || "Failed to load templates");
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (!file.name.endsWith('.zip')) {
        toast.error(t('templates.selectZip'));
        return;
      }
      setUploadFile(file);
      setTemplateForm({ ...templateForm, name: file.name.replace('.zip', '') });
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      toast.error(t('templates.selectFile'));
      return;
    }

    if (!templateForm.name.trim()) {
      toast.error(t('templates.enterName'));
      return;
    }

    const formData = new FormData();
    formData.append("file", uploadFile);
    formData.append("name", templateForm.name);
    formData.append("description", templateForm.description);
    formData.append("is_default", templateForm.is_default);

    try {
      await api.post("/api/templates/upload/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
        onUploadProgress: (progressEvent) => {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percentCompleted);
        },
      });

      toast.success(t('templates.uploadSuccess'));
      setUploadModal(false);
      setUploadFile(null);
      setUploadProgress(0);
      setTemplateForm({ name: "", description: "", is_default: false });
      fetchTemplates();
    } catch (error) {
      console.error("Error uploading template:", error);
      toast.error(t('templates.uploadError'));
    }
  };

  const handleSetDefault = async (id) => {
    try {
      await api.patch(`/api/templates/${id}/set_default/`);
      toast.success(t('templates.setDefaultSuccess'));
      fetchTemplates();
    } catch (error) {
      toast.error(t('templates.setDefaultError'));
    }
  };

  const handleDelete = async (id) => {
    if (!confirm(t('templates.deleteConfirm'))) return;

    try {
      await api.delete(`/api/templates/${id}/`);
      toast.success(t('templates.deleteSuccess'));
      fetchTemplates();
    } catch (error) {
      toast.error(t('templates.deleteError'));
    }
  };

  const handleUpdateTemplate = async () => {
    try {
      await api.patch(`/api/templates/${currentTemplate.id}/`, {
        name: templateForm.name,
        description: templateForm.description,
        content: templateForm.content,
      });
      toast.success(t('templates.updateSuccess'));
      setEditModal(false);
      setCurrentTemplate(null);
      setTemplateForm({ name: "", description: "", is_default: false });
      fetchTemplates();
    } catch (error) {
      toast.error(t('templates.updateError'));
    }
  };

  const handleCreate = async () => {
    try {
      const config = {
        name: templateForm.name,
        type: templateForm.type,
        description: templateForm.description,
        variables: [], // Default empty variables
        fingerprint: {}
      };

      await api.post("/api/templates/", {
        name: templateForm.name,
        type: templateForm.type,
        description: templateForm.description,
        content: templateForm.content,
        config: config,
        is_default: templateForm.is_default
      });
      
      toast.success(t('templates.createSuccess'));
      setCreateModal(false);
      setTemplateForm({ name: "", description: "", type: "MONOLITHIC", content: "", is_default: false });
      fetchTemplates();
    } catch (error) {
      console.error("Error creating template:", error);
      toast.error(t('templates.createError'));
    }
  };

  const columns = [
    {
      header: t('templates.template'),
      render: (template) => (
        <div className="flex items-center">
          <HiTemplate className="w-5 h-5 text-blue-500 mr-3" />
          <div>
            <div className="font-medium text-gray-900">{template.name}</div>
            {template.description && (
              <div className="text-sm text-gray-500">{template.description}</div>
            )}
          </div>
        </div>
      ),
    },
    {
      header: t('templates.type'),
      render: (template) => (
        <span className="text-sm text-gray-600">{template.template_type || "General"}</span>
      ),
    },
    {
      header: t('templates.status'),
      render: (template) => (
        <div className="flex items-center space-x-2">
          {template.is_default && (
            <Badge variant="success" size="sm">
              <HiCheckCircle className="w-3 h-3 mr-1 inline" />
              {t('templates.default')}
            </Badge>
          )}
          <Badge variant="primary" size="sm">{t('templates.active')}</Badge>
        </div>
      ),
    },
    {
      header: t('templates.uploaded'),
      render: (template) => (
        <span className="text-sm text-gray-600">
          {new Date(template.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      header: t('templates.actions'),
      render: (template) => (
        <div className="flex items-center space-x-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setCurrentTemplate(template);
              setDetailsModal(true);
            }}
            title={t('templates.viewDetails')}
          >
            <HiEye className="w-4 h-4 text-gray-600" />
          </Button>
          {!template.is_default && (
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleSetDefault(template.id)}
            >
              {t('templates.setDefault')}
            </Button>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={() => {
              setCurrentTemplate(template);
              setTemplateForm({
                name: template.name,
                description: template.description || "",
                content: template.content || "",
                is_default: template.is_default,
              });
              setEditModal(true);
            }}
          >
            <HiPencil className="w-4 h-4" />
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleDelete(template.id)}
            disabled={template.is_default}
          >
            <HiTrash className="w-4 h-4 text-red-600" />
          </Button>
        </div>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Spinner size="lg" />
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">{t('templates.title')}</h1>
          <p className="mt-1 text-sm text-gray-600">
            {t('templates.subtitle')}
          </p>
        </div>
        <div className="flex space-x-3">
          <Button
            variant="outline"
            icon={<HiPlus className="w-5 h-5" />}
            onClick={() => setCreateModal(true)}
          >
            {t('templates.createTemplate')}
          </Button>
          <Button
            variant="primary"
            icon={<HiUpload className="w-5 h-5" />}
            onClick={() => setUploadModal(true)}
          >
            {t('templates.uploadTemplate')}
          </Button>
        </div>
      </div>

      {/* Templates Table */}
      <Card>
        {templates.length === 0 ? (
          <div className="text-center py-12">
            <HiTemplate className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {t('templates.noTemplatesYet')}
            </h3>
            <p className="text-gray-600 mb-4">
              {t('templates.uploadFirst')}
            </p>
            <Button variant="primary" onClick={() => setUploadModal(true)}>
              {t('templates.uploadTemplate')}
            </Button>
          </div>
        ) : (
          <Table columns={columns} data={templates} />
        )}
      </Card>

      {/* Details Modal */}
      <Modal
        isOpen={detailsModal}
        onClose={() => {
          setDetailsModal(false);
          setCurrentTemplate(null);
        }}
        title={t('templates.detailsTitle')}
        size="lg"
        footer={
          <Button variant="primary" onClick={() => setDetailsModal(false)}>
            {t('common.close')}
          </Button>
        }
      >
        {currentTemplate && (
          <div className="space-y-6">
            <div>
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">{t('templates.generalInfo')}</h4>
              <div className="grid grid-cols-2 gap-4 bg-gray-50 p-4 rounded-lg">
                <div>
                  <span className="text-xs text-gray-500 block">{t('common.name')}</span>
                  <span className="font-medium">{currentTemplate.name}</span>
                </div>
                <div>
                  <span className="text-xs text-gray-500 block">{t('templates.type')}</span>
                  <span className="font-medium">{currentTemplate.type}</span>
                </div>
                <div className="col-span-2">
                  <span className="text-xs text-gray-500 block">{t('templates.description')}</span>
                  <span className="text-sm">{currentTemplate.description || "No description"}</span>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">{t('templates.availableVariables')}</h4>
              {currentTemplate.available_variables && currentTemplate.available_variables.length > 0 ? (
                <div className="flex flex-wrap gap-2">
                  {currentTemplate.available_variables.map((v, i) => (
                    <Badge key={i} variant="gray" size="sm">{v}</Badge>
                  ))}
                </div>
              ) : (
                <p className="text-sm text-gray-500 italic">{t('templates.noVariables')}</p>
              )}
            </div>

            <div>
              <h4 className="text-sm font-medium text-gray-500 uppercase tracking-wider mb-2">{t('templates.fingerprintConfig')}</h4>
              <div className="bg-gray-900 text-gray-100 p-4 rounded-lg overflow-x-auto">
                <pre className="text-xs font-mono">
                  {JSON.stringify(currentTemplate.fingerprint_config || {}, null, 2)}
                </pre>
              </div>
            </div>
          </div>
        )}
      </Modal>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModal}
        onClose={() => {
          setUploadModal(false);
          setUploadFile(null);
          setUploadProgress(0);
          setTemplateForm({ name: "", description: "", is_default: false });
        }}
        title={t('templates.uploadModalTitle')}
        size="md"
        footer={
          <>
            <Button
              variant="secondary"
              onClick={() => {
                setUploadModal(false);
                setUploadFile(null);
                setUploadProgress(0);
              }}
            >
              {t('common.cancel')}
            </Button>
            <Button
              variant="primary"
              onClick={handleUpload}
              disabled={!uploadFile || uploadProgress > 0}
            >
              {uploadProgress > 0 ? `${t('templates.uploading')} ${uploadProgress}%` : t('templates.uploadTemplate')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              {t('templates.zipFile')}
            </label>
            <input
              ref={fileInputRef}
              type="file"
              accept=".zip"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div
              onClick={() => fileInputRef.current?.click()}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <HiUpload className="w-12 h-12 mx-auto text-gray-400 mb-2" />
              <p className="text-sm text-gray-600">
                {uploadFile ? uploadFile.name : t('templates.clickToSelect')}
              </p>
              <p className="text-xs text-gray-500 mt-1">
                {t('templates.mustInclude')}
              </p>
            </div>
          </div>

          {uploadProgress > 0 && (
            <div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          <Input
            label={t('templates.templateName')}
            value={templateForm.name}
            onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
            placeholder="My Awesome Template"
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('templates.description')}</label>
            <textarea
              value={templateForm.description}
              onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
              placeholder={t('templates.descriptionPlaceholder')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="is_default"
              checked={templateForm.is_default}
              onChange={(e) => setTemplateForm({ ...templateForm, is_default: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="is_default" className="ml-2 text-sm text-gray-700">
              {t('templates.setAsDefault')}
            </label>
          </div>
        </div>
      </Modal>

      {/* Edit Modal */}
      <Modal
        isOpen={editModal}
        onClose={() => {
          setEditModal(false);
          setCurrentTemplate(null);
          setTemplateForm({ name: "", description: "", is_default: false });
        }}
        title={t('templates.editTitle')}
        size="md"
        footer={
          <>
            <Button variant="secondary" onClick={() => setEditModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" onClick={handleUpdateTemplate}>
              {t('common.save')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label={t('templates.templateName')}
            value={templateForm.name}
            onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('templates.description')}</label>
            <textarea
              value={templateForm.description}
              onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
              placeholder={t('templates.descriptionPlaceholder')}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('templates.contentHtml')}
            </label>
            <textarea
              value={templateForm.content}
              onChange={(e) => setTemplateForm({ ...templateForm, content: e.target.value })}
              rows={10}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
            <p className="mt-1 text-xs text-gray-500">
              {t('templates.editRawHtml')}
            </p>
          </div>
        </div>
      </Modal>
      {/* Create Modal */}
      <Modal
        isOpen={createModal}
        onClose={() => {
          setCreateModal(false);
          setTemplateForm({ name: "", description: "", type: "MONOLITHIC", content: "<html>\n  <body>\n    <h1>{{ page_title }}</h1>\n    <div>{{ content }}</div>\n  </body>\n</html>", is_default: false });
        }}
        title={t('templates.createTitle')}
        size="lg"
        footer={
          <>
            <Button variant="secondary" onClick={() => setCreateModal(false)}>
              {t('common.cancel')}
            </Button>
            <Button variant="primary" onClick={handleCreate}>
              {t('templates.createTemplate')}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          <Input
            label={t('templates.templateName')}
            value={templateForm.name}
            onChange={(e) => setTemplateForm({ ...templateForm, name: e.target.value })}
            placeholder="My New Template"
            required
          />

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('templates.type')}</label>
            <select
              value={templateForm.type}
              onChange={(e) => setTemplateForm({ ...templateForm, type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="MONOLITHIC">{t('templates.monolithic')}</option>
              <option value="SECTIONAL">{t('templates.sectional')}</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('templates.description')}</label>
            <textarea
              value={templateForm.description}
              onChange={(e) => setTemplateForm({ ...templateForm, description: e.target.value })}
              placeholder={t('templates.descriptionPlaceholder')}
              rows={2}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('templates.initialContent')}
            </label>
            <textarea
              value={templateForm.content}
              onChange={(e) => setTemplateForm({ ...templateForm, content: e.target.value })}
              rows={10}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
            <p className="mt-1 text-xs text-gray-500">
              {t('templates.useVariables')}
            </p>
          </div>

          <div className="flex items-center">
            <input
              type="checkbox"
              id="create_is_default"
              checked={templateForm.is_default}
              onChange={(e) => setTemplateForm({ ...templateForm, is_default: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label htmlFor="create_is_default" className="ml-2 text-sm text-gray-700">
              {t('templates.setAsDefault')}
            </label>
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default Templates;
