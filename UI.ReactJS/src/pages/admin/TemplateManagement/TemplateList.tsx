import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/atomic/button.tsx';
import { Eye, Edit, Trash2, Download, FileText, MoreHorizontal, Upload } from 'lucide-react';
import { useTemplateList } from './hooks/useTemplateList.ts';
import { shouldUseFixture } from '@/config/config.ts';
import { TemplateSearchFilters } from './components/TemplateSearchFilters';
import type { Template } from './types';
import { UploadTemlateModal } from './components/UploadTemlateModal';
import { TemplateDetailModal } from './components/TemplateDetailModal';
import { convertTimestamp } from '@/utils/common';
import { mapCategoryToLabel } from '@/services/Constants.ts';

// Local development flag - can override global config
const USE_FIXTURE = shouldUseFixture('USE_FIXTURE', false);

export const TemplateList: React.FC = () => {
  const navigate = useNavigate();
  const {
    templates,
    loading,
    error,
    success,
    currentPage,
    totalPages,
    pageSize,
    totalTemplates,
    filters,
    updateFilters,
    clearFilters,
    availableCategories,
    availableCreators,
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    deleteTemplate,
    downloadTemplate,
    refreshTemplates,
    clearNotifications
  } = useTemplateList({ useFixture: USE_FIXTURE });

  const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);
  const [showUploadModal, setShowUploadModal] = useState(false);
  const [templateDetailModal, setTemplateDetailModal] = useState<{
    isOpen: boolean;
    template: Template | null;
  }>({
    isOpen: false,
    template: null
  });

  const actionMenuRef = useRef<HTMLDivElement | null>(null);

  // Auto-dismiss success notifications after 3 seconds
  React.useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        clearNotifications();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [success, clearNotifications]);

  // Close action menu if clicked outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (actionMenuRef.current && !actionMenuRef.current.contains(event.target as Node)) {
        setOpenActionMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [actionMenuRef]);

  const handleViewTemplate = (templateId: number) => {
    const template = templates.find(t => t.id === templateId);
    if (template) {
      setTemplateDetailModal({
        isOpen: true,
        template: template
      });
    }
    setOpenActionMenu(null);
  };

  const handleEditTemplate = (templateId: number) => {
    navigate(`/templates/${templateId}/edit`);
    setOpenActionMenu(null);
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (window.confirm('Are you sure you want to delete this template?')) {
      await deleteTemplate(templateId);
      setOpenActionMenu(null);
    }
  };

  const handleDownloadTemplate = async (templateId: number) => {
    await downloadTemplate(templateId);
    setOpenActionMenu(null);
  };

  const handleViewInfo = (templateId: number) => {
    navigate(`/templates/${templateId}`);
    setOpenActionMenu(null);
  };

  const toggleActionMenu = (templateId: number) => {
    setOpenActionMenu(openActionMenu === templateId ? null : templateId);
  };

  const generatePageNumbers = () => {
    const pages: number[] = [];
    const maxVisiblePages = 5;
    const halfVisible = Math.floor(maxVisiblePages / 2);

    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, currentPage + halfVisible);

    // Adjust if we're near the beginning or end
    if (endPage - startPage < maxVisiblePages - 1) {
      if (startPage === 1) {
        endPage = Math.min(totalPages, maxVisiblePages);
      } else {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  return (
    <div className="p-6">
      <UploadTemlateModal
        isOpen={showUploadModal}
        onClose={() => {
          setShowUploadModal(false)
        }}
        onUploadSuccess={React.useCallback(() => {
          setShowUploadModal(false);
          refreshTemplates();
        }, [refreshTemplates])}
      />
      {/* Breadcrumb */}
      <div className="mb-6">
        <div className="flex items-center text-sm text-gray-600 mb-4">
          <span>Analyst Tools</span>
          <span className="mx-2">/</span>
          <span>Templates</span>
        </div>
        <div className='flex justify-between'>
          <h2 className="text-lg font-medium text-gray-900">Template List</h2>
          {/* Action Buttons */}
          <div className="flex gap-3">
            <Button
              onClick={() => setShowUploadModal(true)}
              className="bg-orange-500 hover:bg-orange-600 text-white"
              disabled={loading}
            >
              <Upload className="w-4 h-4 mr-2" />
              Upload template
            </Button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">⚠ {error}</p>
          <Button
            onClick={() => refreshTemplates()}
            variant="outline"
            className="mt-2 text-red-600 border-red-600 hover:bg-red-50"
            size="sm"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm">✅ {success}</p>
        </div>
      )}

      {/* Search Filters */}
      <TemplateSearchFilters
        filters={filters}
        availableCategories={availableCategories}
        availableCreators={availableCreators}
        loading={loading}
        onFiltersChange={updateFilters}
        onRefreshTemplates={refreshTemplates}
        onClearFilters={clearFilters}
      />

      {/* Templates Table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm mt-2">Loading templates...</p>
        </div>
      ) : templates.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-red-500 text-sm">No data found</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg">
          <table className="w-full table-fixed">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[5%]">
                  #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider flex-grow w-[30%] ">
                  Template Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider flex-grow w-[25%]">
                  Template Category
                </th>
                {/* <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[15%]">
                  Modifier
                </th> */}
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[20%]">
                  Creator
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[20%]">
                  Upload Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[10%]">
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {templates.map((template, index) => (
                <tr key={template.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {(currentPage - 1) * pageSize + index + 1}
                  </td>
                  <td
                    className="px-6 py-4 text-sm text-gray-900 cursor-pointer hover:text-blue-600 overflow-hidden whitespace-nowrap"
                    onClick={() => handleViewTemplate(template.id)}
                  >
                    <div className="font-medium" title={template.name}>
                      {template.name.toString().length > 30
                      ? `${template.name.substring(0, 30)}...`
                      : template.name}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 overflow-hidden text-ellipsis">
                    {mapCategoryToLabel(template.category)}
                  </td>
                  {/* <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {template.modifier_name}
                  </td> */}
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {template.creator_name}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {convertTimestamp(template.updated_at)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 relative">
                    <button
                      onClick={() => toggleActionMenu(template.id)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title="More options"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>

                    {/* Action Dropdown Menu */}
                    {openActionMenu === template.id && (
                      <div ref={actionMenuRef} className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-40">

                        {/* View Info */}
                        <button
                          onClick={() => handleViewTemplate(template.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Eye className="w-4 h-4 mr-2 text-blue-600" />
                          View Info
                        </button>

                        {/* View */}
                        <button
                          onClick={() => handleViewInfo(template.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <FileText className="w-4 h-4 mr-2 text-green-600" />
                          View
                        </button>

                        {/* Edit */}
                        <button
                          onClick={() => handleEditTemplate(template.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Edit className="w-4 h-4 mr-2 text-yellow-600" />
                          Edit
                        </button>

                        {/* Download */}
                        <button
                          onClick={() => handleDownloadTemplate(template.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Download className="w-4 h-4 mr-2 text-blue-600" />
                          Download
                        </button>

                        <hr className="my-1" />

                        {/* Delete */}
                        <button
                          onClick={() => handleDeleteTemplate(template.id)}
                          className="flex items-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="bg-white px-6 py-3 border-t border-gray-200 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-700">Rows per page:</span>
              <select
                className="border border-gray-300 rounded px-2 py-1 text-sm"
                value={pageSize}
                onChange={(e) => changePageSize(parseInt(e.target.value))}
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
              <span className="text-sm text-gray-700">of {totalTemplates} rows</span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                className={`p-1 ${currentPage === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-400 hover:text-gray-600 cursor-pointer'}`}
                onClick={goToPrevPage}
                disabled={currentPage === 1}
                title="Previous page"
              >
                ‹
              </button>

              {generatePageNumbers().map(pageNum => (
                <button
                  key={pageNum}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${pageNum === currentPage
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                    }`}
                  onClick={() => goToPage(pageNum)}
                >
                  {pageNum}
                </button>
              ))}

              <button
                className={`p-1 ${currentPage === totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-400 hover:text-gray-600 cursor-pointer'}`}
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
                title="Next page"
              >
                ›
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Template Detail Modal */}
      <TemplateDetailModal
        isOpen={templateDetailModal.isOpen}
        template={templateDetailModal.template}
        onClose={() => setTemplateDetailModal({ isOpen: false, template: null })}
      />
    </div>
  );
};
