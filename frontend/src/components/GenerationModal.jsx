import React, { useState, useEffect } from 'react';
import { Modal, Button } from '../components/ui';
import api from '../services/api';
import { toast } from 'react-toastify';

const GenerationModal = ({ isOpen, onClose, pageId, blocks, onGenerateComplete }) => {
    const [prompts, setPrompts] = useState([]);
    const [selectedBlocks, setSelectedBlocks] = useState({}); // { blockId: { promptId, targetField } }
    const [generating, setGenerating] = useState(false);

    useEffect(() => {
        if (isOpen) {
            fetchPrompts();
            // Initialize selection
            const initialSelection = {};
            blocks.forEach(block => {
                // Default target field based on block type
                let targetField = 'body';
                if (block.type === 'hero') targetField = 'headline'; // or subtitle?
                if (block.type === 'article') targetField = 'body';
                if (block.type === 'cta') targetField = 'text';
                if (block.type === 'faq') targetField = 'items'; // Special handling needed for FAQ?
                
                initialSelection[block.id] = {
                    selected: false,
                    promptId: '',
                    targetField: targetField
                };
            });
            setSelectedBlocks(initialSelection);
        }
    }, [isOpen, blocks]);

    const fetchPrompts = async () => {
        try {
            const res = await api.get('/api/prompts/');
            setPrompts(res.data);
        } catch (error) {
            console.error("Failed to fetch prompts", error);
            toast.error("Failed to load prompts");
        }
    };

    const handleSelectionChange = (blockId, field, value) => {
        setSelectedBlocks(prev => ({
            ...prev,
            [blockId]: {
                ...prev[blockId],
                [field]: value
            }
        }));
    };

    const handleGenerate = async () => {
        const generations = Object.entries(selectedBlocks)
            .filter(([_, data]) => data.selected && data.promptId)
            .map(([blockId, data]) => ({
                block_id: parseInt(blockId),
                prompt_id: parseInt(data.promptId),
                target_field: data.targetField
            }));

        if (generations.length === 0) {
            toast.warning("Please select at least one block and a prompt");
            return;
        }

        setGenerating(true);
        try {
            const res = await api.post('/api/prompts/generate/', {
                page_id: pageId,
                generations: generations
            });

            if (res.data.status === 'completed') {
                const successCount = res.data.results.length;
                const errorCount = res.data.errors.length;
                
                if (successCount > 0) toast.success(`Generated content for ${successCount} blocks`);
                if (errorCount > 0) toast.warning(`${errorCount} blocks failed to generate`);
                
                onGenerateComplete();
                onClose();
            }
        } catch (error) {
            console.error("Generation failed", error);
            toast.error("Generation failed");
        } finally {
            setGenerating(false);
        }
    };

    return (
        <Modal
            isOpen={isOpen}
            onClose={onClose}
            title="Generate AI Content"
            size="lg"
            footer={
                <>
                    <Button variant="secondary" onClick={onClose} disabled={generating}>Cancel</Button>
                    <Button variant="primary" onClick={handleGenerate} disabled={generating}>
                        {generating ? 'Generating...' : 'Generate Selected'}
                    </Button>
                </>
            }
        >
            <div className="space-y-4">
                <p className="text-sm text-gray-500">Select blocks to generate content for. Ensure you have set up your API tokens in Settings.</p>
                
                <div className="border rounded-md divide-y">
                    {blocks.map(block => (
                        <div key={block.id} className="p-4 flex items-start space-x-4 hover:bg-gray-50">
                            <input
                                type="checkbox"
                                checked={selectedBlocks[block.id]?.selected || false}
                                onChange={(e) => handleSelectionChange(block.id, 'selected', e.target.checked)}
                                className="mt-1 h-4 w-4 text-blue-600 rounded border-gray-300"
                            />
                            <div className="flex-1">
                                <div className="flex justify-between">
                                    <span className="font-medium text-gray-900 capitalize">{block.type} Block</span>
                                    <span className="text-xs text-gray-500">ID: {block.id}</span>
                                </div>
                                <p className="text-sm text-gray-500 truncate mb-2">
                                    {block.content?.title || block.content?.heading || "No title"}
                                </p>
                                
                                {selectedBlocks[block.id]?.selected && (
                                    <div className="grid grid-cols-2 gap-3 mt-2">
                                        <div>
                                            <label className="block text-xs font-medium text-gray-700 mb-1">Prompt</label>
                                            <select
                                                value={selectedBlocks[block.id]?.promptId}
                                                onChange={(e) => handleSelectionChange(block.id, 'promptId', e.target.value)}
                                                className="block w-full text-sm border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                            >
                                                <option value="">Select a prompt...</option>
                                                {prompts.map(p => (
                                                    <option key={p.id} value={p.id}>{p.name} ({p.target_type})</option>
                                                ))}
                                            </select>
                                        </div>
                                        <div>
                                            <label className="block text-xs font-medium text-gray-700 mb-1">Target Field</label>
                                            <select
                                                value={selectedBlocks[block.id]?.targetField}
                                                onChange={(e) => handleSelectionChange(block.id, 'targetField', e.target.value)}
                                                className="block w-full text-sm border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500"
                                            >
                                                {/* Dynamic options based on block type could go here */}
                                                <option value="body">Body / Content</option>
                                                <option value="heading">Heading</option>
                                                <option value="title">Title</option>
                                                <option value="text">Text</option>
                                                <option value="html">Custom HTML</option>
                                            </select>
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </Modal>
    );
};

export default GenerationModal;
