import React, { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { useTranslation } from "react-i18next";
import { Card, Button } from "../components/ui";
import { HiGlobeAlt, HiTemplate, HiPhotograph, HiChartBar } from "react-icons/hi";
import api from "../services/api";

/**
 * Home/Dashboard - Main landing page for authenticated users
 * Shows overview stats and quick actions
 */
const Home = () => {
  const { t } = useTranslation();
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
      title: t('home.actions.createSite'),
      description: t('home.actions.createSiteDesc'),
      icon: HiGlobeAlt,
      link: "/sites-list",
      color: "blue",
    },
    {
      title: t('home.actions.manageTemplates'),
      description: t('home.actions.manageTemplatesDesc'),
      icon: HiTemplate,
      link: "/templates",
      color: "purple",
    },
    {
      title: t('home.actions.mediaLibrary'),
      description: t('home.actions.mediaLibraryDesc'),
      icon: HiPhotograph,
      link: "/media-library",
      color: "green",
    },
    {
      title: t('home.actions.viewAnalytics'),
      description: t('home.actions.viewAnalyticsDesc'),
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
        <h1 className="text-3xl font-bold text-gray-900">{t('home.title')}</h1>
        <p className="mt-2 text-gray-600">
          {t('home.welcome')}
        </p>
      </div>

      {/* Quick Stats - Always 4 columns horizontal */}
      <div className="grid grid-cols-4 gap-6 mb-8">
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">{t('home.totalSites')}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_sites}</p>
          </div>
        </Card>
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">{t('home.publishedPages')}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.total_pages}</p>
          </div>
        </Card>
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">{t('home.deployedSites')}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.sites_deployed}</p>
          </div>
        </Card>
        <Card padding="md" hoverable>
          <div className="text-center">
            <p className="text-sm font-medium text-gray-600">{t('home.storageUsed')}</p>
            <p className="text-3xl font-bold text-gray-900 mt-2">{stats.storage_used} MB</p>
          </div>
        </Card>
      </div>

      {/* Quick Actions - Always 4 columns horizontal */}
      <div>
        <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('home.quickActions')}</h2>
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
        <h2 className="text-xl font-semibold text-gray-900 mb-4">{t('home.recentActivity')}</h2>
        <Card>
          <div className="text-center py-8 text-gray-500">
            <p>{t('home.noActivity')}</p>
            <Link to="/sites-list">
              <Button variant="primary" className="mt-4">
                {t('home.createFirstSite')}
              </Button>
            </Link>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default Home;