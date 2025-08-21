/**
 * Knowledge Item Row Component
 * Full implementation with CRUD operations
 */

import React, { useState } from 'react';
import KnowledgeKeywordInput from './KnowledgeKeywordInput';

interface KnowledgeItem {
  id?: string;
  title: string;
  content: string;
  keywords: string[];
  category?: string;
  priority?: number;
}

interface KnowledgeItemRowProps {
  item: KnowledgeItem;
  onUpdate: (item: KnowledgeItem) => void;
  onDelete: () => void;
  disabled?: boolean;
}

export default function KnowledgeItemRow({ 
  item, 
  onUpdate, 
  onDelete,
  disabled = false
}: KnowledgeItemRowProps) {
  const [isEditing, setIsEditing] = useState(!item.title); // Auto-edit mode for new items
  const [editedItem, setEditedItem] = useState<KnowledgeItem>(item);
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const validateItem = (): boolean => {
    const newErrors: { [key: string]: string } = {};
    
    if (!editedItem.title.trim()) {
      newErrors.title = 'Title is required';
    } else if (editedItem.title.length < 3) {
      newErrors.title = 'Title must be at least 3 characters';
    } else if (editedItem.title.length > 100) {
      newErrors.title = 'Title must be less than 100 characters';
    }
    
    if (!editedItem.content.trim()) {
      newErrors.content = 'Content is required';
    } else if (editedItem.content.length < 10) {
      newErrors.content = 'Content must be at least 10 characters';
    } else if (editedItem.content.length > 1000) {
      newErrors.content = 'Content must be less than 1000 characters';
    }
    
    if (editedItem.keywords.length === 0) {
      newErrors.keywords = 'At least one keyword is required';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleEdit = () => {
    setIsEditing(true);
    setEditedItem(item);
  };

  const handleSave = () => {
    if (validateItem()) {
      onUpdate(editedItem);
      setIsEditing(false);
      setErrors({});
    }
  };

  const handleCancel = () => {
    setEditedItem(item);
    setIsEditing(false);
    setErrors({});
  };

  const handleDelete = () => {
    if (window.confirm('Are you sure you want to delete this knowledge item?')) {
      onDelete();
    }
  };

  const handleFieldChange = (field: keyof KnowledgeItem, value: any) => {
    setEditedItem({ ...editedItem, [field]: value });
    // Clear error for this field when user starts typing
    if (errors[field]) {
      setErrors({ ...errors, [field]: '' });
    }
  };

  if (isEditing) {
    return (
      <div className="knowledge-item-row border border-gray-200 rounded-lg p-4 bg-gray-50">
        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Title <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              value={editedItem.title}
              onChange={(e) => handleFieldChange('title', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 ${
                errors.title ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="Enter knowledge item title"
              required
              minLength={3}
              maxLength={100}
            />
            {errors.title && (
              <p className="text-red-500 text-xs mt-1">{errors.title}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Content <span className="text-red-500">*</span>
            </label>
            <textarea
              value={editedItem.content}
              onChange={(e) => handleFieldChange('content', e.target.value)}
              className={`w-full px-3 py-2 border rounded-md focus:ring-2 focus:ring-blue-500 ${
                errors.content ? 'border-red-500' : 'border-gray-300'
              }`}
              rows={3}
              placeholder="Enter the knowledge content"
              required
              minLength={10}
              maxLength={1000}
            />
            {errors.content && (
              <p className="text-red-500 text-xs mt-1">{errors.content}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Keywords <span className="text-red-500">*</span>
            </label>
            <KnowledgeKeywordInput
              value={editedItem.keywords.join(', ')}
              onChange={(keywords) => handleFieldChange('keywords', keywords)}
              error={errors.keywords}
            />
            {errors.keywords && (
              <p className="text-red-500 text-xs mt-1">{errors.keywords}</p>
            )}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={editedItem.category || 'general'}
                onChange={(e) => handleFieldChange('category', e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
              >
                <option value="general">General</option>
                <option value="fundamentals">Fundamentals</option>
                <option value="advanced">Advanced</option>
                <option value="troubleshooting">Troubleshooting</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Priority
              </label>
              <input
                type="number"
                value={editedItem.priority || 1}
                onChange={(e) => handleFieldChange('priority', parseInt(e.target.value))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500"
                min={1}
                max={10}
              />
            </div>
          </div>

          <div className="flex justify-end gap-2">
            <button
              onClick={handleCancel}
              className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700"
            >
              Save
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="knowledge-item-row border border-gray-200 rounded-lg p-4 bg-white hover:bg-gray-50 transition-colors">
      <div className="flex justify-between items-start">
        <div className="flex-1">
          <h4 className="font-medium text-gray-900">{item.title || 'Untitled'}</h4>
          <p className="text-sm text-gray-600 mt-1 line-clamp-2">{item.content}</p>
          <div className="mt-2 flex flex-wrap gap-1">
            {item.keywords.map((keyword, index) => (
              <span
                key={index}
                className="inline-block px-2 py-1 text-xs bg-blue-100 text-blue-700 rounded-full"
              >
                {keyword}
              </span>
            ))}
          </div>
          <div className="mt-2 text-xs text-gray-500">
            Category: {item.category || 'general'} | Priority: {item.priority || 1}
          </div>
        </div>
        
        <div className="flex gap-2 ml-4">
          <button
            onClick={handleEdit}
            className="px-3 py-1 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-md"
          >
            Edit
          </button>
          <button
            onClick={handleDelete}
            className="px-3 py-1 text-sm font-medium text-red-600 hover:bg-red-50 rounded-md"
          >
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}