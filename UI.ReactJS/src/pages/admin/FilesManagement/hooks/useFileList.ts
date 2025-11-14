import { useState, useEffect } from 'react';
import type { UploadedFile, FileListResponse } from '@/types/file';
import { FileService, FileMockService } from '../services';

interface FileFilters {
  fileName?: string;
  fileFormat?: string;
  uploadedUser?: string;
}

interface UseFileListOptions {
  useFixture?: boolean;
}

interface UseFileListReturn {
  files: UploadedFile[];
  loading: boolean;
  error: string | null;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalFiles: number;

  // Filter state
  filters: FileFilters;
  filteredFiles: UploadedFile[];

  // Actions
  refreshFiles: () => Promise<void>;
  deleteFile: (fileId: number) => Promise<void>;
  downloadFile: (file: UploadedFile) => Promise<void>;
  previewFile: (file: UploadedFile) => Promise<string>;

  // Pagination
  goToPage: (page: number) => void;
  goToNextPage: () => void;
  goToPrevPage: () => void;
  changePageSize: (size: number) => void;

  // Filtering
  updateFilters: (newFilters: Partial<FileFilters>) => void;
  clearFilters: () => void;

  // Data for filters
  availableUsers: {
    user_id: number;
    full_name: string;
  }[];
  availableFormats: string[];
}

export const useFileList = (options: UseFileListOptions = {}): UseFileListReturn => {
  const { useFixture = false } = options;

  const [allFiles, setAllFiles] = useState<UploadedFile[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);

  // Filter state
  const [filters, setFilters] = useState<FileFilters>({
    fileName: '',
    fileFormat: '',
    uploadedUser: ''
  });

  // Filter files based on current filters
  const filteredFiles = allFiles.filter(file => {
    return (
      (!filters.fileName || file.original_filename.trim().toLowerCase().includes(filters.fileName.trim().toLowerCase())) &&
      (!filters.fileFormat || file.file_type === filters.fileFormat.toLowerCase()) &&
      (!filters.uploadedUser || file.uploaded_by.toString() === filters.uploadedUser)
    );
  });

  // Pagination calculations
  const totalFiles = filteredFiles.length;
  const totalPages = Math.ceil(totalFiles / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const files = filteredFiles.slice(startIndex, endIndex);

  // Get available options for filters - convert uploaded_by to string for display
  const availableUsers = allFiles.map(file => {
    return {
      user_id: file.uploaded_by,
      full_name: file.uploader.toString(),
    }
  })
  const availableFormats = Array.from(new Set(allFiles.map(file => file.file_type))).sort();

  const loadFiles = async () => {
    try {
      setLoading(true);
      setError(null);

      let fileData: FileListResponse;
      if (useFixture) {
        fileData = await FileMockService.getFiles();
      } else {
        fileData = await FileService.getFiles();
      }

      setAllFiles(fileData.files);
      setCurrentPage(1); // Reset to first page when loading new data
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load files');
      console.error('Error loading files:', err);
    } finally {
      setLoading(false);
    }
  };

  const refreshFiles = async () => {
    await loadFiles();
  };

  const deleteFile = async (fileId: number) => {
    try {
      setError(null);
      let success: boolean;

      if (useFixture) {
        success = await FileMockService.deleteFile(fileId);
      } else {
        success = await FileService.deleteFile(fileId);
      }

      if (success) {
        // Remove file from local state
        setAllFiles(prevFiles => prevFiles.filter(f => f.id !== fileId));

        // Adjust current page if necessary
        const newTotalFiles = allFiles.length - 1;
        const newTotalPages = Math.ceil(newTotalFiles / pageSize);
        if (currentPage > newTotalPages && newTotalPages > 0) {
          setCurrentPage(newTotalPages);
        }
      } else {
        setError('Failed to delete file');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete file');
      console.error('Error deleting file:', err);
      throw err;
    }
  };

  const downloadFile = async (file: UploadedFile) => {
    try {
      setError(null);
      if (!useFixture) {
        const blob = await FileService.downloadFile(file.id);

        // Create download link
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = file.original_filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        window.URL.revokeObjectURL(url);
      } else {
        // Mock download - create a dummy file
        const content = `Mock file content for ${file.original_filename}`;
        const blob = new Blob([content], {
          type: file.mimetype
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = file.original_filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download file');
      console.error('Error downloading file:', err);
      throw err;
    }
  };

  const previewFile = async (file: UploadedFile): Promise<string> => {
    try {
      setError(null);
      if (!useFixture) {
        // Create preview URL using VITE_AUTH_BASE_URL + file_path
        const fileBaseUrl = import.meta.env.VITE_FILE_BASE_URL || 'http://hndw-pthoang2:8000';
        const previewUrl = `${fileBaseUrl}/${file.file_path}`;
        return previewUrl;
      } else {
        // Mock preview URL for development
        return new Promise((resolve) => {
          setTimeout(() => {
            resolve(`https://mock.preview.url/${file.id}`);
          }, 1000);
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to preview file');
      console.error('Error previewing file:', err);
      throw err;
    }
  };

  // Pagination functions
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  };

  const changePageSize = (size: number) => {
    setPageSize(size);
    setCurrentPage(1); // Reset to first page
  };

  // Filter functions
  const updateFilters = (newFilters: Partial<FileFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setFilters({
      fileName: '',
      fileFormat: '',
      uploadedUser: ''
    });
    setCurrentPage(1);
  };

  // Load files on mount or when fixture option changes
  useEffect(() => {
    const loadData = async () => {
      await loadFiles();
    };
    loadData();
  }, [useFixture]); // loadFiles is not needed in dependencies as it's stable

  return {
    files,
    loading,
    error,
    currentPage,
    totalPages,
    pageSize,
    totalFiles,
    filters,
    filteredFiles,
    refreshFiles,
    deleteFile,
    downloadFile,
    previewFile,
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    updateFilters,
    clearFilters,
    availableUsers,
    availableFormats
  };
};
