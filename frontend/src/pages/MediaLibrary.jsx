import React, { useState, useEffect, useRef } from "react";
import { Card, Button, Input, Modal, Badge, Spinner } from "../components/ui";
import { HiUpload, HiFolder, HiPhotograph, HiTrash, HiSearch, HiPlus, HiFolderAdd } from "react-icons/hi";
import api from "../services/api";
import { toast } from "react-toastify";

const MediaLibrary = () => {
  const [media, setMedia] = useState([]);
  const [folders, setFolders] = useState([]);
  const [currentFolder, setCurrentFolder] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [uploadModal, setUploadModal] = useState(false);
  const [folderModal, setFolderModal] = useState(false);
  const [newFolderName, setNewFolderName] = useState("");
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [urlUpload, setUrlUpload] = useState("");
  const fileInputRef = useRef(null);

  useEffect(() => {
    fetchFolders();
    fetchMedia();
  }, [currentFolder]);

  const fetchFolders = async () => {
    try {
      const response = await api.get("/api/media/folders/");
      setFolders(response.data);
    } catch (error) {
      console.error("Error fetching folders:", error);
    }
  };

  const fetchMedia = async () => {
    setLoading(true);
    try {
      const params = currentFolder ? `?folder=${currentFolder}` : "";
      const response = await api.get(`/api/media/assets/${params}`);
      console.log("Fetched media:", response.data);
      setMedia(response.data);
    } catch (error) {
      console.error("Error fetching media:", error);
      toast.error("Failed to load media");
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (e) => {
    setSelectedFiles(Array.from(e.target.files));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setSelectedFiles(Array.from(e.dataTransfer.files));
    setUploadModal(true);
  };

  const handleUpload = async () => {
    if (selectedFiles.length === 0 && !urlUpload) {
      toast.error("Please select files or enter a URL");
      return;
    }

    setLoading(true);
    try {
      if (urlUpload) {
        // URL upload
        await api.post("/api/media/assets/upload_url/", {
          url: urlUpload,
          folder: currentFolder,
        });
        toast.success("Media uploaded from URL");
      } else {
        // File upload - upload each file separately
        for (const file of selectedFiles) {
          const formData = new FormData();
          formData.append("file", file);
          formData.append("filename", file.name);
          if (currentFolder) {
            formData.append("folder", currentFolder);
          }
          
          await api.post("/api/media/assets/", formData, {
            headers: { "Content-Type": "multipart/form-data" },
          });
        }
        toast.success(`${selectedFiles.length} file(s) uploaded successfully`);
      }
      
      setUploadModal(false);
      setSelectedFiles([]);
      setUrlUpload("");
      
      // Refresh the media list
      await fetchMedia();
    } catch (error) {
      console.error("Error uploading media:", error);
      toast.error("Failed to upload media: " + (error.response?.data?.error || error.message));
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFolder = async () => {
    if (!newFolderName.trim()) {
      toast.error("Folder name is required");
      return;
    }

    try {
      await api.post("/api/media/folders/", {
        name: newFolderName,
        parent: currentFolder || null,
        site: null, // Media library folders can be site-independent
      });
      toast.success("Folder created successfully");
      setFolderModal(false);
      setNewFolderName("");
      fetchFolders();
    } catch (error) {
      console.error("Folder creation error:", error);
      toast.error("Failed to create folder: " + (error.response?.data?.parent?.[0] || error.response?.data?.site?.[0] || "Unknown error"));
    }
  };

  const handleDeleteMedia = async (id) => {
    if (!confirm("Are you sure you want to delete this media file?")) return;

    try {
      await api.delete(`/api/media/assets/${id}/`);
      toast.success("Media deleted successfully");
      fetchMedia();
    } catch (error) {
      toast.error("Failed to delete media");
    }
  };

  const filteredMedia = media.filter((item) =>
    item.filename?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Media Library</h1>
          <p className="mt-1 text-sm text-gray-600">
            Upload and manage your site images and media files
          </p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            size="sm"
            icon={<HiFolderAdd className="w-5 h-5" />}
            onClick={() => setFolderModal(true)}
          >
            New Folder
          </Button>
          <Button
            variant="primary"
            icon={<HiUpload className="w-5 h-5" />}
            onClick={() => setUploadModal(true)}
          >
            Upload Files
          </Button>
        </div>
      </div>

      {/* Search and Breadcrumb */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-2 text-sm text-gray-600">
          <button
            onClick={() => setCurrentFolder(null)}
            className="hover:text-blue-600"
          >
            <HiFolder className="w-4 h-4 inline mr-1" />
            All Files
          </button>
          {currentFolder && (
            <>
              <span>/</span>
              <span className="text-gray-900">Current Folder</span>
            </>
          )}
        </div>
        <div className="w-64">
          <div className="relative">
            <HiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search media..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
        </div>
      </div>

      {/* Folders */}
      {folders.length > 0 && (
        <div className="mb-6">
          <h3 className="text-sm font-medium text-gray-700 mb-2">Folders</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {folders.map((folder) => (
              <button
                key={folder.id}
                onClick={() => setCurrentFolder(folder.id)}
                className="flex flex-col items-center p-4 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors"
              >
                <HiFolder className="w-12 h-12 text-blue-500 mb-2" />
                <span className="text-sm font-medium text-gray-900 truncate w-full text-center">
                  {folder.name}
                </span>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Media Grid */}
      <Card>
        {loading ? (
          <div className="flex items-center justify-center py-12">
            <Spinner size="lg" />
          </div>
        ) : filteredMedia.length === 0 ? (
          <div
            onDrop={handleDrop}
            onDragOver={(e) => e.preventDefault()}
            className="text-center py-12 border-2 border-dashed border-gray-300 rounded-lg"
          >
            <HiPhotograph className="w-16 h-16 mx-auto text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {searchTerm ? "No media found" : "No media files yet"}
            </h3>
            <p className="text-gray-600 mb-4">
              {searchTerm
                ? "Try a different search term"
                : "Drag and drop files here or click upload"}
            </p>
            {!searchTerm && (
              <Button variant="primary" onClick={() => setUploadModal(true)}>
                Upload Files
              </Button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {filteredMedia.map((item) => (
              <div
                key={item.id}
                className="group relative border border-gray-200 rounded-lg overflow-hidden hover:shadow-md transition-shadow"
              >
                {/* Image */}
                <div className="aspect-square bg-gray-100 flex items-center justify-center">
                  {item.format?.startsWith("image") || item.file_url?.match(/\.(jpg|jpeg|png|gif|webp)$/i) ? (
                    <img
                      src={item.file_url}
                      alt={item.filename}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <HiPhotograph className="w-12 h-12 text-gray-400" />
                  )}
                </div>

                {/* Overlay */}
                <div className="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-50 transition-opacity flex items-center justify-center opacity-0 group-hover:opacity-100">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleDeleteMedia(item.id)}
                    className="text-white hover:text-red-500"
                  >
                    <HiTrash className="w-5 h-5" />
                  </Button>
                </div>

                {/* Filename */}
                <div className="p-2 bg-white">
                  <p className="text-xs text-gray-900 truncate" title={item.filename}>
                    {item.filename}
                  </p>
                  <p className="text-xs text-gray-500">
                    {item.size ? (item.size / 1024).toFixed(1) : '0'} KB
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>

      {/* Upload Modal */}
      <Modal
        isOpen={uploadModal}
        onClose={() => {
          setUploadModal(false);
          setSelectedFiles([]);
          setUrlUpload("");
        }}
        title="Upload Media"
        size="md"
        footer={
          <>
            <Button variant="secondary" onClick={() => setUploadModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleUpload} disabled={loading}>
              {loading ? "Uploading..." : "Upload"}
            </Button>
          </>
        }
      >
        <div className="space-y-4">
          {/* File Upload */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Upload Files
            </label>
            <input
              ref={fileInputRef}
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
            />
            <div
              onClick={() => fileInputRef.current?.click()}
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
            >
              <HiUpload className="w-12 h-12 mx-auto text-gray-400 mb-2" />
              <p className="text-sm text-gray-600">
                Drop files here or click to browse
              </p>
              {selectedFiles.length > 0 && (
                <p className="text-sm text-blue-600 mt-2">
                  {selectedFiles.length} file(s) selected
                </p>
              )}
            </div>
          </div>

          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-300"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">OR</span>
            </div>
          </div>

          {/* URL Upload */}
          <Input
            label="Upload from URL"
            value={urlUpload}
            onChange={(e) => setUrlUpload(e.target.value)}
            placeholder="https://example.com/image.jpg"
          />
        </div>
      </Modal>

      {/* Folder Modal */}
      <Modal
        isOpen={folderModal}
        onClose={() => {
          setFolderModal(false);
          setNewFolderName("");
        }}
        title="Create New Folder"
        size="sm"
        footer={
          <>
            <Button variant="secondary" onClick={() => setFolderModal(false)}>
              Cancel
            </Button>
            <Button variant="primary" onClick={handleCreateFolder}>
              Create
            </Button>
          </>
        }
      >
        <Input
          label="Folder Name"
          value={newFolderName}
          onChange={(e) => setNewFolderName(e.target.value)}
          placeholder="My Images"
          required
        />
      </Modal>
    </div>
  );
};

export default MediaLibrary;
