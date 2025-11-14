import React, { useState } from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { Eye, Download, Trash2, FileText, File, MoreHorizontal, Upload } from 'lucide-react';
import { useFileList } from './hooks/useFileList';
import { shouldUseFixture } from '@/config/config.ts';
import { FileSearchFilters } from './components/FileSearchFilters';
import { FileDetailModal } from './components/FileDetailModal';
import { FileUploadModal } from '@/pages/admin/FilesManagement/components/FileUploadModal.tsx';
import { Office365PreviewModal } from '@/components/Office365PreviewModal.tsx';
import type { UploadedFile } from '@/types/file';

// Local development flag - can override global config
const USE_FIXTURE = shouldUseFixture('FILES_MANAGEMENT_USE_FIXTURE', false);

export const FilesList: React.FC = () => {
  const {
    files,
    loading,
    error,
    currentPage,
    totalPages,
    pageSize,
    totalFiles,
    filters,
    updateFilters,
    clearFilters,
    availableUsers,
    availableFormats,
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    deleteFile,
    downloadFile,
    previewFile,
    refreshFiles
  } = useFileList({ useFixture: USE_FIXTURE });

  const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [fileDetailModal, setFileDetailModal] = useState<{
    isOpen: boolean;
    file: UploadedFile | null;
  }>({
    isOpen: false,
    file: null
  });
  const [previewModal, setPreviewModal] = useState<{
    isOpen: boolean;
    fileName: string;
    fileUrl: string;
    fileType: string;
  }>({
    isOpen: false,
    fileName: '',
    fileUrl: '',
    fileType: ''
  });

  const handleViewFile = (fileId: number) => {
    const file = files.find(f => f.id === fileId);
    if (file) {
      setFileDetailModal({
        isOpen: true,
        file: file
      });
    }
  };

  const handleDeleteFile = async (fileId: number) => {
    if (window.confirm('Are you sure you want to delete this file?')) {
      await deleteFile(fileId);
      setOpenActionMenu(null);
    }
  };

  const handleDownloadFile = async (fileId: number) => {
    const file = files.find(f => f.id === fileId);
    if (file) {
      await downloadFile(file);
      setOpenActionMenu(null);
    }
  };

  const handlePreviewFile = async (fileId: number) => {
    const file = files.find(f => f.id === fileId);
    if (file) {
      try {
        const previewUrl = await previewFile(file);
        setPreviewModal({
          isOpen: true,
          fileName: file.original_filename,
          fileUrl: previewUrl,
          fileType: file.file_type
        });
      } catch (error) {
        console.error('Failed to get preview URL:', error);
        // If preview fails, fallback to download or show error
      }
      setOpenActionMenu(null);
    }
  };

  const toggleActionMenu = (fileId: number) => {
    setOpenActionMenu(openActionMenu === fileId ? null : fileId);
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

  const getFileIcon = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'pdf':
        return <FileText className="w-4 h-4 text-red-600" />;
      case 'excel':
        return <FileText className="w-4 h-4 text-green-600" />;
      default:
        return <File className="w-4 h-4 text-gray-600" />;
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    // Create date object from server timestamp (GMT+0)
    const date = new Date(dateString);

    // Check if the dateString includes timezone info, if not, assume it's UTC
    const isUTC = !dateString.includes('+') && !dateString.includes('Z');

    let localDate: Date;
    if (isUTC && !dateString.endsWith('Z')) {
      // If server sends timestamp without timezone info, treat it as UTC
      localDate = new Date(dateString + 'Z');
    } else {
      localDate = date;
    }

    // Format to client's local timezone
    return localDate.toLocaleString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
      timeZone: Intl.DateTimeFormat().resolvedOptions().timeZone
    }).replace(',', '');
  };

  return (
    <div className="p-6 relative">
      {/* Breadcrumb */}
      <div className="mb-6">
        <div className="flex items-center text-sm text-gray-600 mb-4">
          <span>Analyst Tools</span>
          <span className="mx-2">/</span>
          <span>Uploaded Files</span>
        </div>
        <div className='flex justify-between'>
          <h2 className="text-lg font-medium text-gray-900">Uploaded Files List</h2>
          <Button
            variant="outline"
            className="bg-orange-500 hover:bg-orange-600 text-white"
            disabled={loading}
            onClick={() => setIsUploadModalOpen(true)}
          >
            <Upload className="w-4 h-4 mr-2" />
            Upload file
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">⚠ {error}</p>
          <Button 
            onClick={() => refreshFiles()} 
            variant="outline"
            className="mt-2 text-red-600 border-red-600 hover:bg-red-50"
            size="sm"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Search Filters */}
      <FileSearchFilters
        filters={filters}
        availableUsers={availableUsers}
        availableFormats={availableFormats}
        loading={loading}
        onFiltersChange={(field: string, value: string) => updateFilters({ [field]: value})}
        onRefreshFiles={refreshFiles}
        onClearFilters={clearFilters}
      />

      {/* Files Table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm mt-2">Loading files...</p>
        </div>
      ) : files.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-red-500 text-sm">No data found ...</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg">
          <table className="w-full table-fixed">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[5%]">
                  #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[25%]">
                  File name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[8%]">
                  Format
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[10%]">
                  Size
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wide w-[15%]">
                  Upload time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[15%]">
                  Uploaded user
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[8%]">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[8%]">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {files.map((file, index) => (
                <tr key={file.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    {(currentPage - 1) * pageSize + index + 1}
                  </td>
                  <td 
                    className="px-5 py-3 whitespace-nowrap text-sm text-gray-900 cursor-pointer hover:text-blue-600"
                    onClick={() => handleViewFile(file.id)}
                  >
                    <div className="flex items-center">
                      {getFileIcon(file.file_type)}
                      <span className="ml-2" title={file.original_filename}>
                        {file.original_filename.length > 30
                          ? `${file.original_filename.substring(0, 30)}...`
                          : file.original_filename}
                      </span>
                    </div>
                  </td>
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      file.file_type === 'pdf' 
                        ? 'bg-red-100 text-red-800' 
                        : 'bg-green-100 text-green-800'
                    }`}>
                      {file.file_type.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    {formatFileSize(file.file_size)}
                  </td>
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    {formatDate(file.uploaded_at)}
                  </td>
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    {file.uploader}
                  </td>
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                      file.status === 'success' 
                        ? 'bg-green-100 text-green-800' 
                        : file.status === 'error'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {file.status.toUpperCase()}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 relative">
                    <button 
                      onClick={() => toggleActionMenu(file.id)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title="More options"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>

                    {/* Action Dropdown Menu */}
                    {openActionMenu === file.id && (
                      <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-32">
                        
                        {/* View File */}
                        <button
                          onClick={() => {
                            handleViewFile(file.id);
                            setOpenActionMenu(null);
                          }}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Eye className="w-4 h-4 mr-2 text-blue-600" />
                          View Info
                        </button>

                        {/* Preview File */}
                        <button
                          onClick={() => handlePreviewFile(file.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <FileText className="w-4 h-4 mr-2 text-purple-600" />
                          View
                        </button>

                        {/* Download File */}
                        <button
                          onClick={() => handleDownloadFile(file.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Download className="w-4 h-4 mr-2 text-green-600" />
                          Download
                        </button>
                        
                        <hr className="my-1" />
                        
                        <button
                          onClick={() => handleDeleteFile(file.id)}
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
              <span className="text-sm text-gray-700">of {totalFiles} rows</span>
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

      {/* Upload Modal */}
      {isUploadModalOpen && (
        <FileUploadModal
          isOpen={isUploadModalOpen}
          onClose={() => setIsUploadModalOpen(false)}
          onUploadComplete={refreshFiles}
        />
      )}

      {/* File Detail Modal */}
      <FileDetailModal
        isOpen={fileDetailModal.isOpen}
        file={fileDetailModal.file}
        onClose={() => setFileDetailModal({ isOpen: false, file: null })}
        onDownload={downloadFile}
      />

      {/* Office 365 Preview Modal */}
      <Office365PreviewModal
        isOpen={previewModal.isOpen}
        fileName={previewModal.fileName}
        fileUrl={previewModal.fileUrl}
        fileType={previewModal.fileType}
        onClose={() => setPreviewModal({ isOpen: false, fileName: '', fileUrl: '', fileType: '' })}
      />
    </div>
  );
};
