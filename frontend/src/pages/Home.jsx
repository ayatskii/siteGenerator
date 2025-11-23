import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { Card, Button } from "../components/ui";
import { HiGlobeAlt, HiTemplate, HiPhotograph, HiChartBar } from "react-icons/hi";
import api from "../services/api";

/**
 * Home/Dashboard - Main landing page for authenticated users
 * Shows overview stats and quick actions
 */
const Home = () => {
  const [stats, setStats] = useState({
    total_sites: 0,
    sites_deployed: 0,
    total_pages: 0,
    storage_used: 0
  });

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await api.get('/api/sites/statistics/');
        setStats(response.data);
      } catch (error) {
        console.error("Error fetching stats:", error);
      }
    };
    fetchStats();
  }, []);

  const quickActions = [
    {
      title: "Create New Site",
      description: "Generate a new affiliate website",
      icon: HiGlobeAlt,
      link: "/sites-list",
      color: "blue",
    },
    {
      title: "Manage Templates",
      description: "Upload and configure site templates",
      icon: HiTemplate,
      link: "/templates",
      color: "purple",
    },
    {
      title: "Media Library",
      description: "Upload and organize media files",
      icon: HiPhotograph,
      link: "/media-library",
      color: "green",
    },
    {
      title: "View Analytics",
      description: "Track site performance and metrics",
      icon: HiChartBar,
      link: "/analytics",
      color: "yellow",
    },
  ];

  const colorClasses = {
    blue: "bg-blue-50 text-blue-600",
    purple: "bg-purple-50 text-purple-600",
    green: "bg-green-50 text-green-600",
    yellow: "bg-yellow-50 text-yellow-600",
  };

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
        <p className="mt-2 text-gray-600">
          Welcome to your site management dashboard. Quick actions and overview below.
        </p>
      </div>

      {/* Quick Stats - Always 4 columns horizontal */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Total Sites</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_sites}</p>
          </div>
        </Card>
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Published Pages</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_pages}</p>
          </div>
        </Card>
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Deployed Sites</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.sites_deployed}</p>
          </div>
        </Card>
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">Storage Used</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.storage_used} MB</p>
          </div>
        </Card>
      </div>

      {/* Quick Actions - Always 4 columns horizontal */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-4 gap-6">
          {quickActions.map((action) => {
            const Icon = action.icon;
            return (
              <Link key={action.title} to={action.link}>
                <Card hoverable className="h-full">
                  <div className="flex flex-col items-center text-center p-2">
                    <div className={`w-16 h-16 rounded-lg flex items-center justify-center ${colorClasses[action.color]}`}>
                      <Icon className="w-8 h-8" />
                    </div>
                    <h3 className="mt-4 font-semibold text-gray-900">{action.title}</h3>
                    <p className="mt-1 text-sm text-gray-600">{action.description}</p>
                  </div>
                </Card>
              </Link>
            );
          })}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <Card>
          <div className="text-center py-8 text-gray-500">
            <p>No recent activity to display.</p>
            <Link to="/sites-list">
              <Button variant="primary" className="mt-4">
                Create Your First Site
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Home;