import React, { useState, useEffect } from 'react';
import api from '../services/api';
import { toast } from 'react-toastify';
import { useTranslation } from 'react-i18next';

const PromptManager = () => {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState('text'); // 'text' or 'image'
    const [prompts, setPrompts] = useState([]);
    const [imagePrompts, setImagePrompts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [isEditing, setIsEditing] = useState(false);
    const [currentPrompt, setCurrentPrompt] = useState(null);
    
    // Form State for Text Prompts
    const [formData, setFormData] = useState({
        name: '',
        description: '',
        target_type: 'article',
        ai_model: 'gpt-4',
        temperature: 0.7,
        template: '',
        output_format: 'html',
        input_variables: []
    });

    // Form State for Image Prompts
    const [imageFormData, setImageFormData] = useState({
        name: '',
        description: '',
        provider: 'dall-e',
        template: '',
        style: 'photorealistic',
        dimensions: '1024x1024',
        format: 'png'
    });

    const targetTypes = [
        { value: 'article', label: 'Article' },
        { value: 'title', label: 'Title' },
        { value: 'description', label: 'Description' },
        { value: 'h1', label: 'H1 Heading' },
        { value: 'faq', label: 'FAQ' },
        { value: 'hero', label: 'Hero Section' },
    ];

    const aiModels = [
        { value: 'gpt-4', label: 'GPT-4' },
        { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
        { value: 'grok-beta', label: 'Grok Beta' },
        { value: 'claude-3-opus', label: 'Claude 3 Opus' },
    ];

    const fetchPrompts = React.useCallback(async () => {
        try {
            const res = await api.get('/api/prompts/');
            setPrompts(res.data);
            
            // Fetch image prompts
            const imgRes = await api.get('/api/prompts/image/');
            setImagePrompts(imgRes.data);
            
            setLoading(false);
        } catch (err) {
            console.error(err);
            toast.error(t('prompts.loadError'));
            setLoading(false);
        }
    }, [t]);

    useEffect(() => {
        fetchPrompts();
    }, [fetchPrompts]);

    const handleEdit = (prompt) => {
        setCurrentPrompt(prompt);
        setFormData({
            name: prompt.name,
            description: prompt.description,
            target_type: prompt.target_type,
            ai_model: prompt.ai_model,
            temperature: prompt.temperature || 0.7,
            template: prompt.template,
            output_format: prompt.output_format,
            input_variables: prompt.input_variables || []
        });
        setIsEditing(true);
    };

    const handleCreate = () => {
        setCurrentPrompt(null);
        setFormData({
            name: '',
            description: '',
            target_type: 'article',
            ai_model: 'gpt-4',
            temperature: 0.7,
            template: '',
            output_format: 'html',
            input_variables: []
        });
        setIsEditing(true);
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            // Extract variables from template
            const variables = [];
            const regex = /{{(.*?)}}/g;
            let match;
            while ((match = regex.exec(formData.template)) !== null) {
                variables.push(match[1].trim());
            }
            const dataToSave = { ...formData, input_variables: [...new Set(variables)] };

            if (currentPrompt) {
                await api.put(`/api/prompts/${currentPrompt.id}/`, dataToSave);
                toast.success(t('prompts.promptUpdated'));
            } else {
                await api.post('/api/prompts/', dataToSave);
                toast.success(t('prompts.promptCreated'));
            }
            setIsEditing(false);
            fetchPrompts();
        } catch (err) {
            console.error(err);
            toast.error(t('prompts.saveError'));
        }
    };

    if (loading) return <div className="p-8">{t('common.loading')}</div>;

    return (
        <div className="max-w-6xl mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">{t('prompts.title')}</h1>
                {!isEditing && (
                    <button 
                        onClick={handleCreate}
                        className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                    >
                        {t('prompts.createNew')}
                    </button>
                )}
            </div>

            {isEditing ? (
                <div className="bg-white shadow rounded-lg p-6">
                    <h2 className="text-xl font-semibold mb-4">{currentPrompt ? t('prompts.editPrompt') : t('prompts.newPrompt')}</h2>
                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label className="block text-sm font-medium text-gray-700">{t('prompts.name')}</label>
                                <input
                                    type="text"
                                    name="name"
                                    value={formData.name}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                    required
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">{t('prompts.targetType')}</label>
                                <select
                                    name="target_type"
                                    value={formData.target_type}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                >
                                    {targetTypes.map(t => (
                                        <option key={t.value} value={t.value}>{t.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">{t('prompts.aiModel')}</label>
                                <select
                                    name="ai_model"
                                    value={formData.ai_model}
                                    onChange={handleChange}
                                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                >
                                    {aiModels.map(m => (
                                        <option key={m.value} value={m.value}>{m.label}</option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700">{t('prompts.temperature')} ({formData.temperature})</label>
                                <input
                                    type="range"
                                    name="temperature"
                                    min="0"
                                    max="1"
                                    step="0.1"
                                    value={formData.temperature}
                                    onChange={handleChange}
                                    className="mt-1 block w-full"
                                />
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700">{t('prompts.description')}</label>
                            <input
                                type="text"
                                name="description"
                                value={formData.description}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">
                                {t('prompts.template')}
                                <span className="text-xs text-gray-500 ml-2">{t('prompts.templateHelp')}</span>
                            </label>
                            <textarea
                                name="template"
                                value={formData.template}
                                onChange={handleChange}
                                rows={10}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 font-mono text-sm"
                                required
                            />
                        </div>

                        <div className="flex justify-end space-x-3">
                            <button
                                type="button"
                                onClick={() => setIsEditing(false)}
                                className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                            >
                                {t('prompts.cancel')}
                            </button>
                            <button
                                type="submit"
                                className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                            >
                                {t('prompts.savePrompt')}
                            </button>
                        </div>
                    </form>
                </div>
            ) : (
                <div className="bg-white shadow overflow-hidden sm:rounded-md">
                    <ul className="divide-y divide-gray-200">
                        {prompts.map(prompt => (
                            <li key={prompt.id} className="px-6 py-4 hover:bg-gray-50 flex justify-between items-center">
                                <div>
                                    <h3 className="text-lg font-medium text-gray-900">{prompt.name}</h3>
                                    <div className="text-sm text-gray-500">
                                        <span className="mr-4">{t('prompts.type')}: {prompt.target_type}</span>
                                        <span>{t('prompts.model')}: {prompt.ai_model}</span>
                                    </div>
                                    <p className="text-sm text-gray-500 mt-1">{prompt.description}</p>
                                </div>
                                <button
                                    onClick={() => handleEdit(prompt)}
                                    className="text-indigo-600 hover:text-indigo-900"
                                >
                                    {t('prompts.edit')}
                                </button>
                            </li>
                        ))}
                        {prompts.length === 0 && (
                            <li className="px-6 py-4 text-center text-gray-500">{t('prompts.noPrompts')}</li>
                        )}
                    </ul>
                </div>
            )}
        </div>
    );
};

export default PromptManager;
