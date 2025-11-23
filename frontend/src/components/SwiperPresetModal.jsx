import React, { useState, useEffect } from 'react';
import { Modal, Button, Input } from './ui';
import { HiPlus, HiTrash, HiPhotograph } from 'react-icons/hi';

const SwiperPresetModal = ({ isOpen, onClose, onSave, preset }) => {
  const [formData, setFormData] = useState({
    name: '',
    button_text: 'Learn More',
    items: []
  });

  useEffect(() => {
    if (preset) {
      setFormData({
        name: preset.name,
        button_text: preset.button_text || 'Learn More',
        items: preset.items || []
      });
    } else {
      setFormData({
        name: '',
        button_text: 'Learn More',
        items: []
      });
    }
  }, [preset, isOpen]);

  const handleAddItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, { title: '', description: '', image: '' }]
    }));
  };

  const handleRemoveItem = (index) => {
    setFormData(prev => ({
      ...prev,
      items: prev.items.filter((_, i) => i !== index)
    }));
  };

  const handleItemChange = (index, field, value) => {
    const newItems = [...formData.items];
    newItems[index] = { ...newItems[index], [field]: value };
    setFormData(prev => ({ ...prev, items: newItems }));
  };

  const handleSubmit = () => {
    onSave(formData);
  };

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={preset ? "Edit Swiper Preset" : "Create Swiper Preset"}
      size="lg"
      footer={
        <>
          <Button variant="secondary" onClick={onClose}>Cancel</Button>
          <Button variant="primary" onClick={handleSubmit}>Save Preset</Button>
        </>
      }
    >
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Preset Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="e.g., Homepage Hero Slider"
            required
          />
          <Input
            label="Button Text"
            value={formData.button_text}
            onChange={(e) => setFormData({ ...formData, button_text: e.target.value })}
            placeholder="e.g., Learn More"
          />
        </div>

        <div>
          <div className="flex items-center justify-between mb-2">
            <label className="block text-sm font-medium text-gray-700">Slides</label>
            <Button size="sm" variant="outline" onClick={handleAddItem} icon={<HiPlus className="w-4 h-4" />}>
              Add Slide
            </Button>
          </div>

          <div className="space-y-4 max-h-[400px] overflow-y-auto p-1">
            {formData.items.length === 0 ? (
              <div className="text-center py-8 border-2 border-dashed border-gray-200 rounded-lg text-gray-500">
                No slides added yet. Click "Add Slide" to start.
              </div>
            ) : (
              formData.items.map((item, index) => (
                <div key={index} className="p-4 border border-gray-200 rounded-lg bg-gray-50 relative group">
                  <button
                    onClick={() => handleRemoveItem(index)}
                    className="absolute top-2 right-2 text-gray-400 hover:text-red-600 opacity-0 group-hover:opacity-100 transition-opacity"
                  >
                    <HiTrash className="w-5 h-5" />
                  </button>
                  
                  <div className="grid grid-cols-1 gap-3">
                    <Input
                      label={`Slide ${index + 1} Title`}
                      value={item.title}
                      onChange={(e) => handleItemChange(index, 'title', e.target.value)}
                      placeholder="Slide Title"
                    />
                    <div>
                      <label className="block text-xs font-medium text-gray-500 mb-1">Description</label>
                      <textarea
                        value={item.description}
                        onChange={(e) => handleItemChange(index, 'description', e.target.value)}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-blue-500 focus:border-blue-500"
                        rows={2}
                        placeholder="Slide description..."
                      />
                    </div>
                    <Input
                      label="Image URL"
                      value={item.image}
                      onChange={(e) => handleItemChange(index, 'image', e.target.value)}
                      placeholder="https://example.com/image.jpg"
                    />
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </Modal>
  );
};

export default SwiperPresetModal;
