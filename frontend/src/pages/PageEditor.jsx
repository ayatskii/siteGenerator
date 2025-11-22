import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { toast } from 'react-toastify';

const PageEditor = () => {
    const { siteId, pageId } = useParams();
    const navigate = useNavigate();
    const [loading, setLoading] = useState(true);
    const [formData, setFormData] = useState({
        title: '',
        slug: '',
        published: false,
        meta_title: '',
        meta_description: '',
        h1_heading: '',
        use_h1_in_hero: false,
        canonical_url: '',
        custom_head_html: '',
        primary_keywords: '',
        lsi_keywords: ''
    });

    useEffect(() => {
        if (pageId !== 'new') {
            fetchPageData();
        } else {
            setLoading(false);
        }
    }, [pageId]);

    const fetchPageData = async () => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.get(`http://127.0.0.1:8000/api/sites/pages/${pageId}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setFormData(res.data);
            setLoading(false);
        } catch (err) {
            toast.error("Failed to load page data.");
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value, type, checked } = e.target;
        setFormData(prev => ({
            ...prev,
            [name]: type === 'checkbox' ? checked : value
        }));
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        try {
            const token = localStorage.getItem('token');
            const config = { headers: { Authorization: `Bearer ${token}` } };
            
            if (pageId === 'new') {
                await axios.post(`http://127.0.0.1:8000/api/sites/pages/`, { ...formData, site: siteId }, config);
                toast.success("Page created successfully!");
            } else {
                await axios.put(`http://127.0.0.1:8000/api/sites/pages/${pageId}/`, formData, config);
                toast.success("Page updated successfully!");
            }
            navigate(`/sites/${siteId}`);
        } catch (err) {
            toast.error("Failed to save page.");
        }
    };

    const handleGenerateContent = () => {
        // Stub for generation modal
        alert("Content Generation Modal would appear here with options based on keywords.");
    };

    if (loading) return <div className="p-8">Loading...</div>;

    return (
        <div className="max-w-4xl mx-auto px-4 py-8">
            <div className="flex justify-between items-center mb-6">
                <h1 className="text-2xl font-bold">{pageId === 'new' ? 'Create Page' : 'Edit Page'}</h1>
                <div className="space-x-2">
                    <button 
                        type="button"
                        onClick={() => navigate(`/sites/${siteId}`)}
                        className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                    >
                        Cancel
                    </button>
                    <button 
                        onClick={handleSubmit}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                        Save Changes
                    </button>
                </div>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6 bg-white p-6 rounded-lg shadow">
                {/* General Info */}
                <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">General Information</h2>
                    <div className="grid grid-cols-1 gap-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Page Title</label>
                            <input
                                type="text"
                                name="title"
                                value={formData.title}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Slug</label>
                            <input
                                type="text"
                                name="slug"
                                value={formData.slug}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                                required
                            />
                        </div>
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                name="published"
                                checked={formData.published}
                                onChange={handleChange}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label className="ml-2 block text-sm text-gray-900">Published</label>
                        </div>
                    </div>
                </div>

                <hr className="border-gray-200" />

                {/* SEO Settings */}
                <div>
                    <h2 className="text-lg font-medium text-gray-900 mb-4">SEO Settings</h2>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Meta Title</label>
                            <input
                                type="text"
                                name="meta_title"
                                value={formData.meta_title}
                                onChange={handleChange}
                                maxLength={60}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                            <p className="mt-1 text-xs text-gray-500">Recommended max 60 characters.</p>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Meta Description</label>
                            <textarea
                                name="meta_description"
                                value={formData.meta_description}
                                onChange={handleChange}
                                maxLength={160}
                                rows={3}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                            <p className="mt-1 text-xs text-gray-500">Recommended max 160 characters.</p>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">H1 Heading</label>
                            <input
                                type="text"
                                name="h1_heading"
                                value={formData.h1_heading}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>
                        <div className="flex items-center">
                            <input
                                type="checkbox"
                                name="use_h1_in_hero"
                                checked={formData.use_h1_in_hero}
                                onChange={handleChange}
                                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                            />
                            <label className="ml-2 block text-sm text-gray-900">Use H1 in Hero Block</label>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Canonical URL</label>
                            <input
                                type="url"
                                name="canonical_url"
                                value={formData.canonical_url}
                                onChange={handleChange}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Custom Head HTML</label>
                            <textarea
                                name="custom_head_html"
                                value={formData.custom_head_html}
                                onChange={handleChange}
                                rows={4}
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 font-mono text-sm"
                            />
                        </div>
                    </div>
                </div>

                <hr className="border-gray-200" />

                {/* Content Generation */}
                <div>
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-medium text-gray-900">Content Generation Metadata</h2>
                        <button
                            type="button"
                            onClick={handleGenerateContent}
                            className="text-sm bg-purple-100 text-purple-700 px-3 py-1 rounded-md hover:bg-purple-200"
                        >
                            ✨ Generate Content
                        </button>
                    </div>
                    <div className="space-y-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Primary Keywords</label>
                            <textarea
                                name="primary_keywords"
                                value={formData.primary_keywords}
                                onChange={handleChange}
                                rows={3}
                                placeholder="One keyword per line"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700">LSI Keywords</label>
                            <textarea
                                name="lsi_keywords"
                                value={formData.lsi_keywords}
                                onChange={handleChange}
                                rows={3}
                                placeholder="One keyword per line"
                                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
                            />
                        </div>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default PageEditor;
