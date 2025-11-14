import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/atomic/button.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Edit, X, File, User, Calendar } from 'lucide-react';
import { mapCategoryToLabel } from '@/services/Constants.ts';
import type { Template } from '../types';

interface TemplateDetailModalProps {
  isOpen: boolean;
  template: Template | null;
  onClose: () => void;
}

export const TemplateDetailModal: React.FC<TemplateDetailModalProps> = ({
  isOpen,
  template,
  onClose
}) => {
  const navigate = useNavigate();

  if (!isOpen || !template) {
    return null;
  }

  const handleEditTemplate = () => {
    navigate(`/templates/${template.id}/edit`);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Template Details</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <File className="w-4 h-4 mr-2 text-blue-600" />
              Basic Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Template Name</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {template.name}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Template ID</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border font-mono">
                  {template.id}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">File Name</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {template.fileName}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Category</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {mapCategoryToLabel(template.category)}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Version</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  v{template.version}
                </p>
              </div>
            </div>
          </div>

          {/* User Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <User className="w-4 h-4 mr-2 text-purple-600" />
              User Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Created By</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {template.creator_name}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Last Modified By</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {template.modifier_name}
                </p>
              </div>
            </div>
          </div>

          {/* Statistics & Status */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Calendar className="w-4 h-4 mr-2 text-orange-600" />
              Statistics
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Created Date</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {template.updated_at ||
                    <span className="text-gray-500 italic">Not available</span>
                  }
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Last Modified</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {template.updated_at}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-200 bg-gray-50">
          <Button
            variant="outline"
            onClick={onClose}
          >
            Close
          </Button>
          <Button
            onClick={handleEditTemplate}
            className="bg-orange-500 hover:bg-orange-600 text-white"
          >
            <Edit className="w-4 h-4 mr-2" />
            Edit Template
          </Button>
        </div>
      </div>
    </div>
  );
};
