import React, { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { Card, Button, Badge, Table, Spinner } from "../components/ui";
import { HiPlus, HiPencil, HiTrash, HiChartBar, HiGlobe } from "react-icons/hi";
import api from "../services/api";
import { toast } from "react-toastify";

const SitesList = () => {
  const navigate = useNavigate();
  const [sites, setSites] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchSites();
  }, []);

  const fetchSites = async () => {
    try {
      const response = await api.get("/api/sites/");
      console.log("Sites data:", response.data);
      setSites(response.data);
    } catch (error) {
      console.error("Error fetching sites:", error);
      toast.error("Failed to load sites");
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (siteId) => {
    if (!confirm("Are you sure you want to delete this site?")) return;

    try {
      await api.delete(`/api/sites/${siteId}/`);
      toast.success("Site deleted successfully");
      fetchSites();
    } catch (error) {
      console.error("Error deleting site:", error);
      toast.error("Failed to delete site");
    }
  };

  const filteredSites = sites.filter((site) =>
    site.domain?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    site.brand_name?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const columns = [
    {
      header: "Domain",
      render: (site) => (
        <div className="flex items-center">
          <HiGlobe className="w-5 h-5 text-gray-400 mr-2" />
          <div>
            <div className="font-medium text-gray-900">{site.domain}</div>
            <div className="text-sm text-gray-500">{site.brand_name}</div>
          </div>
        </div>
      ),
    },
    {
      header: "Language",
      render: (site) => (
        <span className="text-sm text-gray-600">{site.language || "en-US"}</span>
      ),
    },
    {
      header: "Status",
      render: (site) => (
        <Badge variant={site.deployed ? "success" : "warning"}>
          {site.deployed ? "Deployed" : "Draft"}
        </Badge>
      ),
    },
    {
      header: "Created",
      render: (site) => (
        <span className="text-sm text-gray-600">
          {new Date(site.created_at).toLocaleDateString()}
        </span>
      ),
    },
    {
      header: "Actions",
      render: (site) => (
        <div className="flex items-center space-x-2">
          <Link to={`/sites/${site.id}`}>
            <Button variant="outline" size="sm" icon={<HiPencil className="w-4 h-4" />}>
              Edit
            </Button>
          </Link>
          <Link to={`/sites/${site.id}/analytics`}>
            <Button variant="ghost" size="sm">
              <HiChartBar className="w-4 h-4" />
            </Button>
          </Link>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleDelete(site.id)}
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
          <h1 className="text-3xl font-bold text-gray-900">Sites</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage all your generated websites
          </p>
        </div>
        <Link to="/create-site">
          <Button variant="primary" icon={<HiPlus className="w-5 h-5" />}>
            Create New Site
          </Button>
        </Link>
      </div>

      {/* Search */}
      <div className="mb-6">
        <input
          type="text"
          placeholder="Search sites by domain or brand..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="w-full max-w-md px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
        />
      </div>

      {/* Sites Table */}
      <Card>
        {filteredSites.length === 0 ? (
          <div className="text-center py-12">
            <HiGlobe className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm ? "No sites found" : "No sites yet"}
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm
                ? "Try a different search term"
                : "Get started by creating your first site"}
            </p>
            {!searchTerm && (
              <Link to="/create-site">
                <Button variant="primary">Create Your First Site</Button>
              </Link>
            )}
          </div>
        ) : (
          <Table columns={columns} data={filteredSites} />
        )}
      </Card>
    </div>
  );
};

export default SitesList;
