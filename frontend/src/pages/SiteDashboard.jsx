import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const SiteDashboard = () => {
    const { siteId } = useParams();
    const navigate = useNavigate();
    const [site, setSite] = useState(null);
    const [pages, setPages] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        fetchSiteData();
    }, [siteId]);

    const fetchSiteData = async () => {
        try {
            const token = localStorage.getItem('token');
            const config = { headers: { Authorization: `Bearer ${token}` } };
            
            // Fetch site details
            const siteRes = await axios.get(`http://127.0.0.1:8000/api/sites/${siteId}/`, config);
            setSite(siteRes.data);

            // Fetch pages
            const pagesRes = await axios.get(`http://127.0.0.1:8000/api/sites/pages/?site_id=${siteId}`, config);
            setPages(pagesRes.data);
            
            setLoading(false);
        } catch (err) {
            console.error("Error fetching data:", err);
            setError("Failed to load site data.");
            setLoading(false);
        }
    };

    const handleDeletePage = async (pageId) => {
        if (!window.confirm("Are you sure you want to delete this page?")) return;

        try {
            const token = localStorage.getItem('token');
            await axios.delete(`http://127.0.0.1:8000/api/sites/pages/${pageId}/`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setPages(pages.filter(p => p.id !== pageId));
        } catch (err) {
            alert("Failed to delete page.");
        }
    };

    const handleDuplicatePage = async (pageId) => {
        try {
            const token = localStorage.getItem('token');
            const res = await axios.post(`http://127.0.0.1:8000/api/sites/pages/${pageId}/duplicate/`, {}, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setPages([...pages, res.data]);
        } catch (err) {
            alert("Failed to duplicate page.");
        }
    };

    if (loading) return <div className="p-8 text-center">Loading...</div>;
    if (error) return <div className="p-8 text-red-500">{error}</div>;

    return (
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="flex justify-between items-center mb-6">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900">{site?.name}</h1>
                    <p className="text-gray-500">{site?.domain}</p>
                </div>
                <button 
                    onClick={() => navigate(`/sites/${siteId}/pages/new`)} // TODO: Implement create page
                    className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md"
                >
                    Create New Page
                </button>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6 border-b border-gray-200">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Pages</h3>
                </div>
                <ul className="divide-y divide-gray-200">
                    {pages.map((page) => (
                        <li key={page.id} className="px-4 py-4 sm:px-6 hover:bg-gray-50">
                            <div className="flex items-center justify-between">
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center">
                                        <p className="text-sm font-medium text-blue-600 truncate">{page.title}</p>
                                        <span className={`ml-2 px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${page.published ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}`}>
                                            {page.published ? 'Published' : 'Draft'}
                                        </span>
                                    </div>
                                    <div className="mt-2 flex">
                                        <div className="flex items-center text-sm text-gray-500">
                                            <span className="truncate">/{page.slug}</span>
                                        </div>
                                        <div className="ml-6 flex items-center text-sm text-gray-500">
                                            <span>Updated: {new Date(page.updated_at).toLocaleDateString()}</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="flex space-x-2">
                                    <Link 
                                        to={`/sites/${siteId}/pages/${page.id}`}
                                        className="text-indigo-600 hover:text-indigo-900 px-3 py-1 border border-indigo-600 rounded-md text-sm"
                                    >
                                        Edit
                                    </Link>
                                    <button 
                                        onClick={() => handleDuplicatePage(page.id)}
                                        className="text-gray-600 hover:text-gray-900 px-3 py-1 border border-gray-300 rounded-md text-sm"
                                    >
                                        Duplicate
                                    </button>
                                    <button 
                                        onClick={() => handleDeletePage(page.id)}
                                        className="text-red-600 hover:text-red-900 px-3 py-1 border border-red-300 rounded-md text-sm"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
};

export default SiteDashboard;
