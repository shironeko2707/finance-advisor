import { useState, useEffect, useCallback } from 'react';
import type { Template, TemplateFilters, TemplateListState } from '../types';
import { apiService } from '@/services/ApiInterceptor.ts';
import { TEMPLATE_CATEGORIES } from '@/services/Constants';

interface UseTemplateListOptions {
  useFixture?: boolean;
}

export const useTemplateList = ({ useFixture = false }: UseTemplateListOptions = {}) => {
  const [state, setState] = useState<TemplateListState>({
    templates: [],
    loading: false,
    error: null,
    success: null,
    currentPage: 1,
    totalPages: 1,
    pageSize: 10,
    totalTemplates: 0,
    filters: {
      search: '',
      category: '',
      isActive: '',
      createdBy: '',
      creator: ''
    }
  });

  const [creators, setCreator] = useState<Template[]>([]);

  // Apply filters to templates
  const getFilteredTemplates = useCallback((templates: Template[], filters: TemplateFilters) => {
    return templates?.filter(template => {
      const matchesSearch = !filters?.search ||
        template?.name?.trim()?.toLowerCase()?.includes(filters.search?.trim()?.toLowerCase()) ||
        template?.description?.trim()?.toLowerCase()?.includes(filters.search?.trim()?.toLowerCase()) ||
        template?.fileName?.trim()?.toLowerCase()?.includes(filters.search?.trim()?.toLowerCase());

      const matchesCategory = !filters.category || template.category === filters.category;

      const matchesCreator = !filters.createdBy || template.created_by === filters.createdBy;

      return matchesSearch && matchesCategory && matchesCreator;
    });
  }, []);

  // Get paginated templates
  const getPaginatedTemplates = useCallback((templates: Template[], page: number, pageSize: number) => {
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return templates.slice(startIndex, endIndex);
  }, []);

  const availableCreators = creators.map(item => {
    return {
      user_id: item.created_by,
      full_name: item?.creator_name?.toString() ?? "",
    }
  })

  // Load templates
  const loadTemplates = useCallback(async () => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      const res = await apiService.api.getTemplates();
      setCreator(res.templates ?? []);
      const filteredTemplates = getFilteredTemplates(res.templates, state.filters);
      const totalTemplates = filteredTemplates.length;
      const totalPages = Math.ceil(totalTemplates / state.pageSize);
      const paginatedTemplates = getPaginatedTemplates(filteredTemplates, state.currentPage, state.pageSize);

      setState(prev => ({
        ...prev,
        templates: paginatedTemplates,
        totalTemplates,
        totalPages,
        loading: false
      }));
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to load templates'
      }));
    }
  }, [state.filters, state.currentPage, state.pageSize, getFilteredTemplates, getPaginatedTemplates]);

  // Update filters
  const updateFilters = useCallback((newFilters: Partial<TemplateFilters>) => {
    setState(prev => ({
      ...prev,
      filters: { ...prev.filters, ...newFilters },
      currentPage: 1 // Reset to first page when filters change
    }));
  }, []);

  // Clear filters
  const clearFilters = useCallback(() => {
    setState(prev => ({
      ...prev,
      filters: {
        search: '',
        category: '',
        isActive: '',
        createdBy: '',
        creator: ""
      },
      currentPage: 1
    }));
  }, []);

  // Pagination functions
  const goToPage = useCallback((page: number) => {
    setState(prev => ({ ...prev, currentPage: page }));
  }, []);

  const goToNextPage = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentPage: Math.min(prev.currentPage + 1, prev.totalPages)
    }));
  }, []);

  const goToPrevPage = useCallback(() => {
    setState(prev => ({
      ...prev,
      currentPage: Math.max(prev.currentPage - 1, 1)
    }));
  }, []);

  const changePageSize = useCallback((newPageSize: number) => {
    setState(prev => ({
      ...prev,
      pageSize: newPageSize,
      currentPage: 1
    }));
  }, []);

  // Template actions
  const deleteTemplate = useCallback(async (templateId: number) => {
    setState(prev => ({ ...prev, loading: true, error: null }));

    try {
      await apiService.api.deleteTemplate(templateId);
      setState(prev => ({
        ...prev,
        loading: false,
        success: 'Template deleted successfully'
      }));
      // Reload templates after deletion
      setTimeout(() => loadTemplates(), 100);
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to delete template'
      }));
    }
  }, [loadTemplates]);

  const downloadTemplate = useCallback(async (templateId: number) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));

      if (useFixture) {
        // Keep mock implementation for fixture mode
        await new Promise(resolve => setTimeout(resolve, 500));
        const template = state.templates.find(t => t.id === templateId);
        if (template) {
          // Simulate file download
          const blob = new Blob(['Mock template content'], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement('a');
          a.href = url;
          a.download = template.fileName || `template_${templateId}.xlsx`;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);

          setState(prev => ({
            ...prev,
            loading: false,
            success: 'Template downloaded successfully'
          }));
        }
      } else {
        // Use real API call to /templates/{id}/download
        const blob = await apiService.api.downloadTemplate(templateId);

        // Get template info for proper filename
        const template = state.templates.find(t => t.id === templateId);
        const fileName = template?.fileName || `template_${templateId}.xlsx`;

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = fileName;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);

        setState(prev => ({
          ...prev,
          loading: false,
          success: 'Template downloaded successfully'
        }));
      }
    } catch (error) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error instanceof Error ? error.message : 'Failed to download template'
      }));
    }
  }, [useFixture, state.templates]);

  const refreshTemplates = useCallback(() => {
    loadTemplates();
  }, [loadTemplates]);

  const clearNotifications = useCallback(() => {
    setState(prev => ({ ...prev, error: null, success: null }));
  }, []);

  // Load templates on mount and when dependencies change
  useEffect(() => {
    loadTemplates();
  }, [loadTemplates]);

  return {
    templates: state.templates,
    loading: state.loading,
    error: state.error,
    success: state.success,
    currentPage: state.currentPage,
    totalPages: state.totalPages,
    pageSize: state.pageSize,
    totalTemplates: state.totalTemplates,
    filters: state.filters,
    updateFilters,
    clearFilters,
    availableCategories: TEMPLATE_CATEGORIES,
    availableCreators,
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    deleteTemplate,
    downloadTemplate,
    refreshTemplates,
    clearNotifications
  };
};
