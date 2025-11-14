import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { TemplateService } from '../services/TemplateService';
import { TEMPLATE_CATEGORIES } from '@/services/Constants.ts';
import type { Template, TemplateFormData } from '../types';

interface UseEditTemplateProps {
  templateId?: number;
  isEditMode: boolean;
}

export const useEditTemplate = ({ templateId, isEditMode }: UseEditTemplateProps) => {
  const navigate = useNavigate();

  // State
  const [formData, setFormData] = useState<TemplateFormData>({
    name: '',
    category: '',
    fileName: ''
  });

  const [currentTemplate, setCurrentTemplate] = useState<Template | null>(null);
  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [isPreviewOpen, setIsPreviewOpen] = useState(false);

  // Use shared template categories
  const categories = TEMPLATE_CATEGORIES;

  // Load template data for edit mode
  useEffect(() => {
    const loadTemplate = async () => {
      if (!isEditMode || !templateId) return;

      setInitialLoading(true);
      setError(null);

      try {
        const template = await TemplateService.getTemplate(templateId);
        setCurrentTemplate(template);

        // Populate form data
        setFormData({
          name: template.name,
          category: TEMPLATE_CATEGORIES.find(cat => cat.label === template.category)?.value || '',
          fileName: template.fileName || ''
        });
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load template');
      } finally {
        setInitialLoading(false);
      }
    };

    loadTemplate();
  }, [templateId, isEditMode]);

  // Handle input changes
  const handleInputChange = useCallback((field: keyof TemplateFormData, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));

    // Clear error when user starts typing
    if (error) setError(null);
    if (success) setSuccess(null);
  }, [error, success]);

  // Handle form submission
  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.name.trim() || !formData.category) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(null);

    try {
      if (isEditMode && templateId) {
        // Update existing template
        const updatedTemplate = await TemplateService.updateTemplate(templateId, {
          name: formData.name.trim(),
          category: formData.category,
          fileName: formData.fileName?.trim()
        });

        setCurrentTemplate(updatedTemplate);
        setSuccess('Template updated successfully!');
      } else {
        // Create new template
        const newTemplate = await TemplateService.createTemplate({
          name: formData.name.trim(),
          category: formData.category,
          fileName: formData.fileName?.trim()
        });

        setCurrentTemplate(newTemplate);
        setSuccess('Template created successfully!');

        // Navigate to edit mode for the newly created template
        navigate(`/admin/templates/${newTemplate.id}`);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save template');
    } finally {
      setLoading(false);
    }
  }, [isEditMode, templateId, formData, navigate]);

  // Handle cancel
  const handleCancel = useCallback(() => {
    navigate('/templates');
  }, [navigate]);

  // Handle preview
  const handlePreview = useCallback(() => {
    if (currentTemplate || formData.name) {
      setIsPreviewOpen(true);
    }
  }, [currentTemplate, formData.name]);

  // Get template file for preview
  const getTemplateFileForPreview = useCallback(() => {
    if (currentTemplate) {
      // Construct the full URL using VITE_FILE_BASE_URL + file_path, similar to Reports
      const fileBaseUrl = import.meta.env.VITE_FILE_BASE_URL || 'http://hndw-pthoang2:8000/';
      const previewUrl = currentTemplate.file_url ? `${fileBaseUrl}/${currentTemplate.file_url}` : '';

      return {
        name: currentTemplate.fileName || `${currentTemplate.name}.xlsx`,
        url: previewUrl,
        type: 'xlsx'
      };
    }

    return {
      name: formData.fileName || `${formData.name || 'template'}.xlsx`,
      url: '',
      type: 'xlsx'
    };
  }, [currentTemplate, formData.fileName, formData.name]);

  return {
    // State
    formData,
    currentTemplate,
    loading,
    initialLoading,
    error,
    success,
    isPreviewOpen,
    categories,

    // Actions
    setIsPreviewOpen,
    handleInputChange,
    handleSubmit,
    handleCancel,
    handlePreview,
    getTemplateFileForPreview
  };
};
