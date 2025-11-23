import React, { useState, useEffect } from 'react';
import { Modal, Button, Input, Spinner } from './ui';
import { HiSearch, HiCheck, HiFolder, HiPhotograph } from 'react-icons/hi';
import api from '../services/api';

/**
 * Media Library Selector Modal Component
 * 
 * Allows users to select an image from their media library.
 * Supports folder navigation and search functionality.
 */
const MediaLibrarySelector = ({ isOpen, onClose, onSelect, title = "Select Image" }) => {
  const [loading, setLoading] = useState(false);
  const [assets, setAssets] = useState([]);
  const [folders, setFolders] = useState([]);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAsset, setSelectedAsset] = useState(null);

  useEffect(() => {
    if (isOpen) {
      fetchAssets();
      fetchFolders();
    }
  }, [isOpen, currentFolder]);

  const fetchAssets = async () => {
    setLoading(true);
    try {
      const params = currentFolder ? { folder: currentFolder } : {};
      const response = await api.get('/api/media/assets/', { params });
      setAssets(response.data);
    } catch (error) {
      console.error('Error fetching assets:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFolders = async () => {
    try {
      const response = await api.get('/api/media/folders/');
      setFolders(response.data);
    } catch (error) {
      console.error('Error fetching folders:', error);
    }
  };

  const handleSelect = () => {
    if (selectedAsset) {
      onSelect(selectedAsset);
      onClose();
      setSelectedAsset(null);
    }
  };

  const filteredAssets = searchQuery
    ? assets.filter(asset =>
        asset.filename.toLowerCase().includes(searchQuery.toLowerCase())
      )
    : assets;

  return (
    <Modal
      isOpen={isOpen}
      onClose={() => {
        onClose();
        setSelectedAsset(null);
      }}
      title={title}
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={() => {
            onClose();
            setSelectedAsset(null);
          }}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleSelect}
            disabled={!selectedAsset}
          >
            Select
          </Button>
        </>
      }
    >
      <div className="space-y-4">
        {/* Search Bar */}
        <Input
          type="text"
          placeholder="Search images..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          icon={<HiSearch className="w-5 h-5 text-gray-400" />}
        />

        {/* Folder Navigation */}
        {folders.length > 0 && (
          <div className="flex gap-2 flex-wrap">
            <Button
              variant={currentFolder === null ? "primary" : "outline"}
              size="sm"
              onClick={() => setCurrentFolder(null)}
              icon={<HiFolder className="w-4 h-4" />}
            >
              All Files
            </Button>
            {folders.map(folder => (
              <Button
                key={folder.id}
                variant={currentFolder === folder.id ? "primary" : "outline"}
                size="sm"
                onClick={() => setCurrentFolder(folder.id)}
                icon={<HiFolder className="w-4 h-4" />}
              >
                {folder.name}
              </Button>
            ))}
          </div>
        )}

        {/* Image Grid */}
        {loading ? (
          <div className="flex justify-center py-12">
            <Spinner size="lg" />
          </div>
        ) : filteredAssets.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <HiPhotograph className="w-16 h-16 mx-auto mb-4 opacity-50" />
            <p>No images found</p>
          </div>
        ) : (
          <div className="grid grid-cols-3 md:grid-cols-4 gap-4 max-h-96 overflow-y-auto p-2">
            {filteredAssets.map(asset => (
              <div
                key={asset.id}
                onClick={() => setSelectedAsset(asset)}
                className={`relative aspect-square cursor-pointer rounded-lg overflow-hidden border-2 transition-all ${
                  selectedAsset?.id === asset.id
                    ? 'border-blue-500 ring-2 ring-blue-200 scale-105'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                <img
                  src={asset.file || asset.file_url}
                  alt={asset.filename}
                  className="w-full h-full object-cover"
                />
                {selectedAsset?.id === asset.id && (
                  <div className="absolute inset-0 bg-blue-500 bg-opacity-20 flex items-center justify-center">
                    <HiCheck className="w-12 h-12 text-white drop-shadow-lg" />
                  </div>
                )}
                <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent p-2">
                  <p className="text-white text-xs truncate">{asset.filename}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </Modal>
  );
};

export default MediaLibrarySelector;
