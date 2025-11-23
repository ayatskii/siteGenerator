import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { HiPencil, HiTrash, HiDuplicate, HiEye, HiExternalLink, HiPlus, HiSave } from "react-icons/hi";
import { useTranslation } from "react-i18next";
import { Tabs } from "../components/ui";
import api from "../services/api";
import { toast } from "react-toastify";
import AnalyticsDashboard from "../components/analytics/AnalyticsDashboard";

const CustomCodeEditor = ({ site, setSite, siteId }) => {
    const { t } = useTranslation();
    const [activeTab, setActiveTab] = useState('css');

    const tabs = [
        { id: 'css', label: 'CSS', placeholder: t('siteDashboard.customCss'), field: 'custom_css' },
        { id: 'js', label: 'JavaScript', placeholder: t('siteDashboard.customJs'), field: 'custom_js' },
        { id: 'head', label: 'Head HTML', placeholder: t('siteDashboard.customHead'), field: 'custom_head_html' },
        { id: 'body', label: 'Body HTML', placeholder: t('siteDashboard.customBody'), field: 'custom_body_html' },
    ];

    const activeField = tabs.find(t => t.id === activeTab);

    const handleSave = async () => {
        try {
            await api.patch(`/api/sites/${siteId}/`, {
                custom_css: site.custom_css,
                custom_js: site.custom_js,
                custom_head_html: site.custom_head_html,
                custom_body_html: site.custom_body_html
            });
            toast.success(t('siteDashboard.codeSaved'));
        } catch (err) {
            toast.error(t('siteDashboard.codeError'));
        }
    };

    return (
        <div className="p-6">
            <div className="flex space-x-4 mb-4 border-b border-gray-200">
                {tabs.map(tab => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`pb-2 px-1 text-sm font-medium ${
                            activeTab === tab.id
                                ? 'border-b-2 border-blue-500 text-blue-600'
                                : 'text-gray-500 hover:text-gray-700'
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                        {t('siteDashboard.customCode')} - {activeField.label}
                    </label>
                    <textarea
                        value={site?.[activeField.field] || ''}
                        onChange={(e) => setSite({...site, [activeField.field]: e.target.value})}
                        rows={15}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm bg-gray-50"
                        placeholder={activeField.placeholder}
                    />
                </div>
                <div className="flex justify-end">
                    <button
                        onClick={handleSave}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center"
                    >
                        <HiSave className="w-5 h-5 mr-2" />
                        {t('siteDashboard.saveChanges')}
                    </button>
                </div>
            </div>
        </div>
    );
};

const SiteDashboard = () => {
    const { siteId } = useParams();
    const navigate = useNavigate();
    const { t } = useTranslation();
    const [site, setSite] = useState(null);
    const [pages, setPages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        if (!siteId || siteId === 'undefined') {
            navigate('/sites-list');
            return;
        }

        const fetchSiteData = async () => {
            try {
                const token = localStorage.getItem('token');
                const config = { headers: { Authorization: `Bearer ${token}` } };
                
                // Fetch site details
                const siteRes = await api.get(`/api/sites/${siteId}/`);
                setSite(siteRes.data);
    
                // Fetch pages
                const pagesRes = await api.get(`/api/pages/?site_id=${siteId}`);
                setPages(pagesRes.data);
                
                setLoading(false);
            } catch (err) {
                console.error("Error fetching data:", err);
                setError(t('siteDashboard.loadError'));
                setLoading(false);
            }
        };

        fetchSiteData();
    }, [siteId]);

    const handleDeletePage = async (pageId) => {
        if (!window.confirm(t('siteDashboard.deletePageConfirm'))) return;

        try {
            const token = localStorage.getItem('token');
            await api.delete(`/api/pages/${pageId}/`);
            setPages(pages.filter(p => p.id !== pageId));
        } catch (err) {
            console.error(err);
            alert(t('siteDashboard.deletePageError'));
        }
    };

    const [deploying, setDeploying] = useState(false);

    const handleDeploy = async () => {
        if (!window.confirm(t('siteDashboard.deployConfirm'))) return;
        
        setDeploying(true);
        try {
            const res = await api.post('/api/deployments/deploy/', { site_id: siteId });
            toast.success(t('siteDashboard.deploySuccess'));
            // Refresh site data to show new status
            const siteRes = await api.get(`/api/sites/${siteId}/`);
            setSite(siteRes.data);
        } catch (err) {
            console.error("Deployment failed:", err);
            toast.error(t('siteDashboard.deployError'));
        } finally {
            setDeploying(false);
        }
    };

    const handleDuplicatePage = async (pageId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await api.post(`/api/pages/${pageId}/duplicate/`);
            setPages([...pages, res.data]);
        } catch (err) {
            console.error(err);
            alert(t('siteDashboard.duplicateError'));
        }
    };

    const [downloading, setDownloading] = useState(false);

    const handleDownload = async () => {
        setDownloading(true);
        try {
            // 1. Trigger deployment/generation
            const res = await api.post('/api/deployments/deploy/', { site_id: siteId });
            toast.success(t('siteDashboard.downloadSuccess'));
            
            if (res.data.download_url) {
                // 2. Fetch the file as a blob with authentication
                const downloadRes = await api.get(res.data.download_url, { 
                    responseType: 'blob' 
                });
                
                // 3. Create a URL for the blob
                const url = window.URL.createObjectURL(new Blob([downloadRes.data]));
                const link = document.createElement('a');
                link.href = url;
                
                // 4. Extract filename from header or default
                const contentDisposition = downloadRes.headers['content-disposition'];
                let fileName = `${site.domain}.zip`;
                if (contentDisposition) {
                    const fileNameMatch = contentDisposition.match(/filename="?(.+)"?/);
                    if (fileNameMatch.length === 2)
                        fileName = fileNameMatch[1];
                }
                
                link.setAttribute('download', fileName);
                document.body.appendChild(link);
                link.click();
                
                // 5. Cleanup
                link.parentNode.removeChild(link);
                window.URL.revokeObjectURL(url);
            }
        } catch (err) {
            console.error("Download failed:", err);
            toast.error(t('siteDashboard.downloadError'));
        } finally {
            setDownloading(false);
        }
    };

    if (loading) return <div className="p-8 text-center">{t('siteDashboard.loading')}</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">{site?.name}</h1>
                    <p className="text-gray-500">{site?.domain}</p>
                </div>
                <div className="flex space-x-3">
                    <button 
                        onClick={handleDownload}
                        disabled={downloading}
                        className="bg-gray-600 hover:bg-gray-700 text-white px-4 py-2 rounded-md flex items-center"
                    >
                        {downloading ? (
                            <>
                                <span className="animate-spin mr-2">⏳</span>
                                {t('siteDashboard.generating')}
                            </>
                        ) : (
                            <>
                                <HiDuplicate className="w-5 h-5 mr-2" />
                                {t('siteDashboard.downloadSource')}
                            </>
                        )}
                    </button>
                    <button 
                        onClick={handleDeploy}
                        disabled={deploying}
                        className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md flex items-center"
                    >
                        {deploying ? (
                            <>
                                <span className="animate-spin mr-2">⏳</span>
                                {t('siteDashboard.deploying')}
                            </>
                        ) : (
                            <>
                                <HiExternalLink className="w-5 h-5 mr-2" />
                                {t('siteDashboard.deploySite')}
                            </>
                        )}
                    </button>
                    <button 
                        onClick={() => navigate(`/sites/${siteId}/pages/new`)}
                        className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md flex items-center"
                    >
                        <HiPlus className="w-5 h-5 mr-2" />
                        {t('siteDashboard.createNewPage')}
                    </button>
                </div>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <Tabs tabs={[
                    {
                        label: t('siteDashboard.pages'),
                        content: (
                            <>
                                <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                                    <h3 className="text-lg leading-6 font-medium text-gray-900">{t('siteDashboard.pages')}</h3>
                                </div>
                                <ul className="divide-y divide-gray-200">
                                    {pages.map((page) => (
                                        <li key={page.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                                            <div className="flex items-center justify-between">
                                                <div className="flex-1 min-w-0">
                                                    <div className="flex items-center">
                                                        <p className="text-sm font-medium text-blue-600 truncate">{page.title}</p>
                                                        <span className={`ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${page.published ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                                            {page.published ? t('siteDashboard.published') : t('siteDashboard.draft')}
                                                        </span>
                                                    </div>
                                                    <div className="mt-2 flex">
                                                        <div className="flex items-center text-sm text-gray-500">
                                                            <span className="truncate">/{page.slug}</span>
                                                        </div>
                                                        <div className="ml-6 flex items-center text-sm text-gray-500">
                                                            <span>{t('siteDashboard.updated')}: {new Date(page.updated_at).toLocaleDateString()}</span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex space-x-2">
                                                    <Link 
                                                        to={`/sites/${siteId}/pages/${page.id}`}
                                                        className="text-indigo-600 hover:text-indigo-900 px-3 py-1 border border-indigo-600 rounded-md text-sm"
                                                    >
                                                        {t('common.edit')}
                                                    </Link>
                                                    <button 
                                                        onClick={() => handleDuplicatePage(page.id)}
                                                        className="text-gray-600 hover:text-gray-900 px-3 py-1 border border-gray-300 rounded-md text-sm"
                                                    >
                                                        {t('siteDashboard.duplicate')}
                                                    </button>
                                                    <button 
                                                        onClick={() => handleDeletePage(page.id)}
                                                        className="text-red-600 hover:text-red-900 px-3 py-1 border border-red-300 rounded-md text-sm"
                                                    >
                                                        {t('siteDashboard.delete')}
                                                    </button>
                                                </div>
                                            </div>
                                        </li>
                                    ))}
                                </ul>
                            </>
                        )
                    },
                    {
                        label: t('siteDashboard.customCode'),
                        content: (
                            <CustomCodeEditor site={site} setSite={setSite} siteId={siteId} />
                        )
                    },
                    {
                        label: t('siteDashboard.templateConfig'),
                        content: (
                            <div className="p-6">
                                <p className="text-gray-500 mb-4">{t('siteDashboard.configDesc')}</p>
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-sm font-medium text-gray-700 mb-1">{t('siteDashboard.configLabel')}</label>
                                        <textarea
                                            value={JSON.stringify(site?.template_config || {}, null, 2)}
                                            onChange={(e) => {
                                                try {
                                                    const config = JSON.parse(e.target.value);
                                                    setSite({...site, template_config: config});
                                                } catch (err) {
                                                    // Ignore parse errors
                                                }
                                            }}
                                            rows={10}
                                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                                        />
                                    </div>
                                    <div className="flex justify-end">
                                        <button
                                            onClick={async () => {
                                                try {
                                                    await api.patch(`/api/sites/${siteId}/`, {
                                                        template_config: site.template_config
                                                    });
                                                    toast.success(t('siteDashboard.configSaved'));
                                                } catch (err) {
                                                    toast.error(t('siteDashboard.configError'));
                                                }
                                            }}
                                            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
                                        >
                                            {t('siteDashboard.saveConfig')}
                                        </button>
                                    </div>
                                </div>
                            </div>
                        )
                    },
                    {
                        label: t('siteDashboard.analytics'),
                        content: (
                            <div className="p-6">
                                <AnalyticsDashboard siteId={siteId} />
                            </div>
                        )
                    }
                ]} />
            </div>
        </div>
    );
};

export default SiteDashboard;
