import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, Button, Input, Badge, Modal } from '../components/ui';
import { HiPlus, HiTrash, HiArrowUp, HiArrowDown, HiSave, HiEye, HiSparkles, HiDuplicate } from 'react-icons/hi';
import { DragDropContext, Droppable, Draggable } from "react-beautiful-dnd";
import { useTranslation } from "react-i18next";
import api from '../services/api';
import { toast } from 'react-toastify';
import GenerationModal from "../components/GenerationModal";

const PageEditor = () => {
  const { siteId, pageId } = useParams();
  const navigate = useNavigate();
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [generationModalOpen, setGenerationModalOpen] = useState(false);
  
  const [pageData, setPageData] = useState({
    title: '',
    slug: '',
    published: false,
    meta_title: '',
    meta_description: '',
    h1_heading: '',
  });
  
  const [blocks, setBlocks] = useState([]);
  const [blockModal, setBlockModal] = useState(false);

  useEffect(() => {
    if (!siteId || siteId === 'undefined') {
      navigate('/sites-list');
      return;
    }

    if (pageId !== 'new') {
      fetchPageData();
      fetchBlocks();
    } else {
      setLoading(false);
    }
  }, [pageId, siteId]);

  const fetchPageData = async () => {
    try {
      const res = await api.get(`/api/pages/${pageId}/`);
      setPageData(res.data);
    } catch (error) {
      toast.error(t('pageEditor.loadError'));
    }
  };

  const fetchBlocks = async () => {
    try {
      const res = await api.get(`/api/blocks/?page_id=${pageId}`);
      setBlocks(res.data.sort((a, b) => a.order - b.order));
    } catch (error) {
      console.error("Failed to load blocks", error);
    } finally {
      setLoading(false);
    }
  };

  const handlePageChange = (e) => {
    const { name, value, type, checked } = e.target;
    setPageData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSavePage = async () => {
    setSaving(true);
    try {
      if (pageId === 'new') {
        const res = await api.post(`/api/pages/`, { ...pageData, site: siteId });
        toast.success(t('pageEditor.saveSuccess'));
        navigate(`/sites/${siteId}/pages/${res.data.id}`);
      } else {
        await api.put(`/api/pages/${pageId}/`, pageData);
        
        // Save all blocks
        for (const block of blocks) {
          if (block.id) {
            await api.put(`/api/blocks/${block.id}/`, block);
          } else {
            await api.post(`/api/blocks/`, { ...block, page: pageId });
          }
        }
        
        toast.success(t('pageEditor.saveSuccess'));
      }
    } catch (error) {
      toast.error(t('pageEditor.saveError'));
    } finally {
      setSaving(false);
    }
  };

  const addBlock = (type) => {
    const newBlock = {
      block_type: type,
      order: blocks.length,
      content: getDefaultContent(type),
    };
    setBlocks([...blocks, newBlock]);
    setBlockModal(false);
  };

  const getDefaultContent = (type) => {
    const defaults = {
      hero: { title: 'Hero Title', subtitle: 'Hero subtitle', cta_text: 'Get Started', cta_link: '#' },
      article: { heading: 'Article Heading', body: 'Article content goes here...' },
      image: { image_url: '', alt_text: '', caption: '' },
      text_image: { heading: '', text: '', image_url: '', image_position: 'right' },
      cta: { heading: 'Call to Action', text: 'Description', button_text: 'Click Here', button_link: '#' },
      faq: { questions: [{ question: 'Question?', answer: 'Answer' }] },
    };
    return defaults[type] || {};
  };

  const onDragEnd = (result) => {
    if (!result.destination) return;
    
    const items = Array.from(blocks);
    const [reorderedItem] = items.splice(result.source.index, 1);
    items.splice(result.destination.index, 0, reorderedItem);
    
    // Update order property
    const updatedItems = items.map((item, index) => ({
      ...item,
      order: index
    }));
    
    setBlocks(updatedItems);
  };

  const deleteBlock = (index) => {
    if (!confirm(t('pageEditor.deleteBlockConfirm'))) return;
    setBlocks(blocks.filter((_, i) => i !== index));
  };

  const updateBlockContent = (index, field, value) => {
    const newBlocks = [...blocks];
    newBlocks[index].content = { ...newBlocks[index].content, [field]: value };
    setBlocks(newBlocks);
  };

  const handlePreview = async () => {
    try {
      await handleSavePage();
      const response = await api.get(`/api/pages/${pageId}/preview/`);
      const previewWindow = window.open('', '_blank');
      previewWindow.document.write(response.data);
      previewWindow.document.close();
    } catch (error) {
      console.error("Preview failed", error);
      toast.error(t('pageEditor.previewError'));
    }
  };

  const blockTypes = [
    { type: 'hero', label: t('pageEditor.blockHero'), icon: '🎯' },
    { type: 'article', label: t('pageEditor.blockArticle'), icon: '📝' },
    { type: 'image', label: t('pageEditor.blockImage'), icon: '🖼️' },
    { type: 'text_image', label: t('pageEditor.blockTextImage'), icon: '📄' },
    { type: 'cta', label: t('pageEditor.blockCta'), icon: '🎯' },
    { type: 'faq', label: t('pageEditor.blockFaq'), icon: '❓' },
    { type: 'custom', label: t('pageEditor.blockCustom'), icon: 'code' },
    { type: 'swiper', label: t('pageEditor.blockSwiper'), icon: 'view_carousel' },
  ];

  const renderBlockEditor = (block, index) => {
    const { block_type, content } = block;

    switch (block_type) {
      case 'hero':
        return (
          <div className="space-y-3">
            <Input
              label={t('pageEditor.blockTitle')}
              value={content.title || ''}
              onChange={(e) => updateBlockContent(index, 'title', e.target.value)}
            />
            <Input
              label={t('pageEditor.blockSubtitle')}
              value={content.subtitle || ''}
              onChange={(e) => updateBlockContent(index, 'subtitle', e.target.value)}
            />
            <div className="grid grid-cols-2 gap-3">
              <Input
                label={t('pageEditor.blockCtaText')}
                value={content.cta_text || ''}
                onChange={(e) => updateBlockContent(index, 'cta_text', e.target.value)}
              />
              <Input
                label={t('pageEditor.blockCtaLink')}
                value={content.cta_link || ''}
                onChange={(e) => updateBlockContent(index, 'cta_link', e.target.value)}
              />
            </div>
          </div>
        );

      case 'article':
        return (
          <div className="space-y-3">
            <Input
              label={t('pageEditor.blockHeading')}
              value={content.heading || ''}
              onChange={(e) => updateBlockContent(index, 'heading', e.target.value)}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('pageEditor.blockContent')}</label>
              <textarea
                value={content.body || ''}
                onChange={(e) => updateBlockContent(index, 'body', e.target.value)}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
          </div>
        );

      case 'image':
        return (
          <div className="space-y-3">
            <Input
              label={t('pageEditor.blockImageUrl')}
              value={content.image_url || ''}
              onChange={(e) => updateBlockContent(index, 'image_url', e.target.value)}
            />
            <Input
              label={t('pageEditor.blockAltText')}
              value={content.alt_text || ''}
              onChange={(e) => updateBlockContent(index, 'alt_text', e.target.value)}
            />
            <Input
              label={t('pageEditor.blockCaption')}
              value={content.caption || ''}
              onChange={(e) => updateBlockContent(index, 'caption', e.target.value)}
            />
          </div>
        );

      case 'text_image':
        return (
          <div className="space-y-3">
            <Input
              label={t('pageEditor.blockHeading')}
              value={content.heading || ''}
              onChange={(e) => updateBlockContent(index, 'heading', e.target.value)}
            />
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('pageEditor.blockText')}</label>
              <textarea
                value={content.text || ''}
                onChange={(e) => updateBlockContent(index, 'text', e.target.value)}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              />
            </div>
            <Input
              label={t('pageEditor.blockImageUrl')}
              value={content.image_url || ''}
              onChange={(e) => updateBlockContent(index, 'image_url', e.target.value)}
            />
            <div>
               <label className="block text-sm font-medium text-gray-700 mb-1">{t('pageEditor.blockImagePosition')}</label>
               <select
                 value={content.image_position || 'right'}
                 onChange={(e) => updateBlockContent(index, 'image_position', e.target.value)}
                 className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
               >
                 <option value="left">Left</option>
                 <option value="right">Right</option>
               </select>
            </div>
          </div>
        );

      case 'cta':
        return (
          <div className="space-y-3">
            <Input
              label={t('pageEditor.blockHeading')}
              value={content.heading || ''}
              onChange={(e) => updateBlockContent(index, 'heading', e.target.value)}
            />
            <Input
              label={t('pageEditor.blockText')}
              value={content.text || ''}
              onChange={(e) => updateBlockContent(index, 'text', e.target.value)}
            />
            <div className="grid grid-cols-2 gap-3">
              <Input
                label={t('pageEditor.blockButtonText')}
                value={content.button_text || ''}
                onChange={(e) => updateBlockContent(index, 'button_text', e.target.value)}
              />
              <Input
                label={t('pageEditor.blockButtonLink')}
                value={content.button_link || ''}
                onChange={(e) => updateBlockContent(index, 'button_link', e.target.value)}
              />
            </div>
          </div>
        );

      case 'faq':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('pageEditor.blockQuestions')}</label>
              <textarea
                value={JSON.stringify(content.questions || [], null, 2)}
                onChange={(e) => {
                  try {
                    const questions = JSON.parse(e.target.value);
                    updateBlockContent(index, 'questions', questions);
                  } catch (err) {
                  }
                }}
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
              />
              <p className="text-xs text-gray-500 mt-1">{t('pageEditor.blockQuestionsHint')}</p>
            </div>
          </div>
        );

      case 'custom':
        return (
          <div className="space-y-3">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">{t('pageEditor.blockCustomHtml')}</label>
              <textarea
                value={content.html || ''}
                onChange={(e) => updateBlockContent(index, 'html', e.target.value)}
                rows={8}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                placeholder="<div>Your custom HTML here</div>"
              />
            </div>
          </div>
        );

      case 'swiper':
        return (
          <div className="space-y-3">
            <p className="text-sm text-gray-600">{t('pageEditor.blockPending')}</p>
             <Input
              label={t('pageEditor.blockPresetId')}
              value={content.preset_id || ''}
              onChange={(e) => updateBlockContent(index, 'preset_id', e.target.value)}
            />
          </div>
        );

      default:
        return <p className="text-sm text-gray-500">Block type: {block_type}</p>;
    }
  };

  if (loading) {
    return <div className="flex justify-center py-12">{t('common.loading')}</div>;
  }

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            {pageId === 'new' ? t('pageEditor.createPage') : t('pageEditor.editPage')}
          </h1>
          <p className="text-sm text-gray-600">{t('pageEditor.configure')}</p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline" onClick={() => navigate(`/sites/${siteId}`)}>
            {t('pageEditor.cancel')}
          </Button>
          <Button variant="secondary" icon={<HiEye className="w-5 h-5" />} onClick={handlePreview} disabled={saving || pageId === 'new'}>
            {t('pageEditor.preview')}
          </Button>
          <Button variant="primary" icon={<HiSparkles className="w-5 h-5" />} onClick={() => setGenerationModalOpen(true)} disabled={saving || pageId === 'new'}>
            {t('pageEditor.generate')}
          </Button>
          <Button variant="success" icon={<HiSave className="w-5 h-5" />} onClick={handleSavePage} disabled={saving}>
            {saving ? t('pageEditor.saving') : t('pageEditor.save')}
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Blocks Editor (Left Column) */}
        <div className="lg:col-span-2 space-y-6">
          <DragDropContext onDragEnd={onDragEnd}>
            <Droppable droppableId="blocks">
              {(provided) => (
                <div
                  {...provided.droppableProps}
                  ref={provided.innerRef}
                  className="space-y-4"
                >
                  {blocks.map((block, index) => (
                    <Draggable key={index} draggableId={`block-${index}`} index={index}>
                      {(provided) => (
                        <div
                          ref={provided.innerRef}
                          {...provided.draggableProps}
                          className="bg-white shadow rounded-lg border border-gray-200"
                        >
                          <div
                            {...provided.dragHandleProps}
                            className="px-4 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between rounded-t-lg"
                          >
                            <div className="flex items-center space-x-3">
                              <span className="text-gray-400 cursor-move">☰</span>
                              <span className="font-medium text-gray-700 capitalize">
                                {block.block_type.replace('_', ' ')} Block
                              </span>
                              <Badge variant="gray">#{index + 1}</Badge>
                            </div>
                            <div className="flex items-center space-x-2">
                              <button
                                onClick={() => deleteBlock(index)}
                                className="text-red-600 hover:text-red-800 p-1"
                              >
                                <HiTrash className="w-5 h-5" />
                              </button>
                            </div>
                          </div>
                          <div className="p-4">
                            {renderBlockEditor(block, index)}
                          </div>
                        </div>
                      )}
                    </Draggable>
                  ))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </DragDropContext>

          <button
            onClick={() => setBlockModal(true)}
            className="w-full py-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-500 hover:border-blue-500 hover:text-blue-500 transition-colors flex items-center justify-center space-x-2"
          >
            <HiPlus className="w-5 h-5" />
            <span>{t('pageEditor.addContentBlock')}</span>
          </button>
        </div>

        {/* Page Settings (Right Column) */}
        <div className="lg:col-span-1">
          <Card title={t('pageEditor.pageSettings')}>
            <div className="space-y-4">
              <Input
                label={t('pageEditor.title')}
                name="title"
                value={pageData.title}
                onChange={handlePageChange}
                required
              />
              <Input
                label={t('pageEditor.slug')}
                name="slug"
                value={pageData.slug}
                onChange={handlePageChange}
                placeholder="page-url"
              />
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="published"
                  name="published"
                  checked={pageData.published}
                  onChange={handlePageChange}
                  className="h-4 w-4 text-blue-600 rounded border-gray-300"
                />
                <label htmlFor="published" className="text-sm font-medium text-gray-700">
                  {t('pageEditor.published')}
                </label>
              </div>
              
              <hr className="border-gray-200" />
              <h3 className="font-medium text-gray-900">{t('pageEditor.seoSettings')}</h3>
              
              <Input
                label={t('pageEditor.metaTitle')}
                name="meta_title"
                value={pageData.meta_title || ''}
                onChange={handlePageChange}
              />
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">{t('pageEditor.metaDescription')}</label>
                <textarea
                  name="meta_description"
                  value={pageData.meta_description || ''}
                  onChange={handlePageChange}
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                />
              </div>
              <Input
                label={t('pageEditor.h1Heading')}
                name="h1_heading"
                value={pageData.h1_heading || ''}
                onChange={handlePageChange}
              />
            </div>
          </Card>
        </div>
      </div>

      <GenerationModal
        isOpen={generationModalOpen}
        onClose={() => setGenerationModalOpen(false)}
        pageId={pageId}
        blocks={blocks}
        onGenerateComplete={() => {
            fetchBlocks();
        }}
      />

      <Modal
        isOpen={blockModal}
        onClose={() => setBlockModal(false)}
        title={t('pageEditor.addBlockTitle')}
        size="md"
      >
        <div className="grid grid-cols-2 gap-3">
          {blockTypes.map(({ type, label, icon }) => (
            <button
              key={type}
              onClick={() => addBlock(type)}
              className="p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors text-left"
            >
              <div className="text-2xl mb-2">{icon}</div>
              <div className="font-medium text-gray-900">{label}</div>
            </button>
          ))}
        </div>
      </Modal>
    </div>
  );
};

export default PageEditor;
