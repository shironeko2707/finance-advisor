import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { Upload, X } from 'lucide-react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Select, SelectItem } from '@/components/atomic/select.tsx';
import { Office365PreviewModal } from '@/components/Office365PreviewModal';
import { useEditTemplate } from './hooks/useEditTemplate';

export const TemplateForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const isEditMode = Boolean(id);

  // File upload state
  const [replacementFile, setReplacementFile] = useState<File | null>(null);

  // Use the custom hook for all template logic
  const {
    formData,
    currentTemplate,
    loading,
    initialLoading,
    error,
    success,
    isPreviewOpen,
    setIsPreviewOpen,
    handleInputChange,
    handleSubmit,
    handleCancel,
    handlePreview,
    getTemplateFileForPreview,
    categories
  } = useEditTemplate({ templateId: id ? parseInt(id, 10) : undefined, isEditMode });

  // File upload handlers
  const handleReplacementFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setReplacementFile(file);
    }
  };

  const removeReplacementFile = () => {
    setReplacementFile(null);
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  if (initialLoading && isEditMode) {
    return (
      <div className="p-6 max-w-full">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading template...</p>
          </div>
        </div>
      </div>
    );
  }

  const templateFileForPreview = getTemplateFileForPreview();

  return (
    <div className="p-6 max-w-full">
      {/* Breadcrumb */}
      <div className="mb-6">
        <div className="flex items-center text-sm text-gray-600 mb-4">
          <span>Analyst Tools</span>
          <span className="mx-2">/</span>
          <span>Templates</span>
        </div>
        <h2 className="text-xl font-medium text-gray-900">
          {isEditMode ? 'Edit template' : 'Create new template'}
        </h2>
      </div>

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm">✅ {success}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">⚠ {error}</p>
        </div>
      )}

      {/* Form Section - Compact */}
      <div className="mb-6 bg-white rounded-lg border border-gray-200 p-4">
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div>
              <Label className="text-sm text-gray-700 mb-2 block">
                Template name *
              </Label>
              <Input
                value={formData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                placeholder="Enter template name"
                className="h-9"
                required
                disabled={loading}
              />
            </div>

            <div>
              <Label className="text-sm text-gray-700 mb-2 block">
                Template category *
              </Label>
              <Select
                value={formData.category}
                onValueChange={(value) => handleInputChange('category', value)}
                placeholder="Please select"
                disabled={loading}
              >
                {categories.map(category => (
                  <SelectItem key={category.value} value={category.value}>
                    {category.label}
                  </SelectItem>
                ))}
              </Select>
            </div>

            <div className="flex space-x-2">
              <Button
                type="button" 
                variant="outline"
                onClick={handleCancel}
                className="px-6"
                disabled={loading}
              >
                Cancel
              </Button>
              <Button 
                type="submit"
                className="bg-orange-500 hover:bg-orange-600 px-6 text-white"
                disabled={loading}
              >
                {loading ? 'Saving...' : 'Save'}
              </Button>
            </div>
          </div>
        </form>
      </div>

      {/* Current Template Display */}
      {(formData.name || currentTemplate) && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <div className="flex items-center justify-between">
            <div className="flex items-center">
              <span className="text-sm text-blue-700">📄</span>
              <span className="ml-2 text-sm text-blue-800">
                Current file template: {currentTemplate?.fileName}
                {currentTemplate?.version && (
                  <span className="ml-2 text-xs text-blue-600">v{currentTemplate.version}</span>
                )}
              </span>
            </div>
            <Button
              size="sm"
              variant="outline"
              onClick={handlePreview}
              className="text-blue-600 border-blue-600 hover:bg-blue-100"
            >
              Preview
            </Button>
          </div>
        </div>
      )}

      {/* File Upload Section for Template Replacement */}
      {isEditMode && (
        <div className="mb-6 bg-white rounded-lg border border-gray-200 p-6">
          <Label className="text-base font-medium text-gray-900 mb-2 block">
            Replace with enhanced file template (optional)
          </Label>

          {/* Warning Label */}
          <div className="mb-4 p-2 bg-yellow-50 border border-yellow-200 rounded">
            <p className="text-xs text-yellow-800 font-medium">
              ⚠️ Warning: Check file carefully because it will overwrite the existing one
            </p>
          </div>

          {/* File Upload Area */}
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50 hover:bg-gray-100 transition-colors">
            <div className="flex flex-col items-center">
              <Upload className="w-10 h-10 text-blue-600 mb-3" />
              <p className="text-base text-gray-700 mb-2">Drop your template file or start uploading</p>
              <label htmlFor="templateReplace" className="cursor-pointer">
                <Button
                  variant="outline"
                  className="border-blue-600 text-blue-600 hover:bg-blue-50"
                  asChild
                >
                  <span>Browse template</span>
                </Button>
                <input
                  id="templateReplace"
                  type="file"
                  className="hidden"
                  accept=".xlsx,.xls"
                  onChange={handleReplacementFileUpload}
                />
              </label>
            </div>
          </div>

          {/* Uploaded Replacement File Display */}
          {replacementFile && (
            <div className="mt-4">
              <Label className="text-sm font-medium text-gray-700 mb-2 block">New template file:</Label>
              <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                    <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                      <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                  <div>
                    <p className="font-medium text-gray-900">{replacementFile.name}</p>
                    <p className="text-sm text-gray-500">{formatFileSize(replacementFile.size)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    <span className="text-sm text-gray-600">Ready</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={removeReplacementFile}
                    className="text-red-500 hover:text-red-700 hover:bg-red-50"
                  >
                    <X className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Office365 Preview Modal */}
      <Office365PreviewModal
        isOpen={isPreviewOpen}
        onClose={() => setIsPreviewOpen(false)}
        fileName={templateFileForPreview.name}
        fileUrl={templateFileForPreview.url}
        fileType={templateFileForPreview.type}
      />
    </div>
  );
};
