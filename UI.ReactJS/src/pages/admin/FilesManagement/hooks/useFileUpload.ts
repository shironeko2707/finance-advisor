import { useState, useCallback } from 'react';
import { FileUploadMockService, FileUploadService } from '../services';
import type { FileUploadResponse, FileUploadProgress } from '@/types/file';

interface UseFileUploadProps {
  useFixture?: boolean;
}

export const useFileUpload = ({ useFixture = false }: UseFileUploadProps = {}) => {
  const [uploadFiles, setUploadFiles] = useState<FileUploadProgress[]>([]);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResponse, setUploadResponse] = useState<FileUploadResponse | null>(null);

  // Determine which service to use based on fixture flag
  const uploadService = useFixture ? FileUploadMockService : FileUploadService;

  const addFiles = useCallback((files: File[]) => {
    // Filter files by type only (size validation is now done in component)
    const validFiles = files.filter(file => FileUploadService.isValidFileType(file));

    const newUploadFiles: FileUploadProgress[] = validFiles.map(file => ({
      id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
      file,
      progress: 0,
      status: 'pending'
    }));

    setUploadFiles(prev => [...prev, ...newUploadFiles]);
  }, []);

  const removeFile = useCallback((id: string) => {
    setUploadFiles(prev => prev.filter(f => f.id !== id));
  }, []);

  const clearFiles = useCallback(() => {
    setUploadFiles([]);
    setUploadResponse(null);
  }, []);

  const simulateProgress = useCallback(async (fileId: string) => {
    // Update status to uploading
    setUploadFiles(prev => prev.map(f =>
      f.id === fileId ? { ...f, status: 'uploading' as const } : f
    ));

    // Simulate progress for UI feedback
    for (let progress = 0; progress <= 90; progress += 10) {
      await new Promise(resolve => setTimeout(resolve, 100));
      setUploadFiles(prev => prev.map(f =>
        f.id === fileId ? { ...f, progress } : f
      ));
    }
  }, []);

  const performUpload = useCallback(async (): Promise<FileUploadResponse> => {
    if (uploadFiles.length === 0) {
      throw new Error('No files to upload');
    }

    setIsUploading(true);
    setUploadResponse(null);

    try {
      // Start progress simulation for all files
      const progressPromises = uploadFiles.map(f => simulateProgress(f.id));

      // Get actual files to upload
      const filesToUpload = uploadFiles.map(f => f.file);

      // Start actual upload
      const [response] = await Promise.all([
        uploadService.uploadMultipleFiles(filesToUpload),
        Promise.all(progressPromises)
      ]);

      // Update file statuses based on response
      setUploadFiles(prev => prev.map((f, index) => {
        const result = response.files[index];
        return {
          ...f,
          progress: 100,
          status: result?.status === 'success' ? 'completed' as const : 'error' as const
        };
      }));

      setUploadResponse(response);
      return response;

    } catch (error) {
      console.error('Upload failed:', error);

      // Mark all files as failed
      setUploadFiles(prev => prev.map(f => ({
        ...f,
        status: 'error' as const
      })));

      const errorResponse: FileUploadResponse = {
        total_files: uploadFiles.length,
        successful_uploads: 0,
        failed_uploads: uploadFiles.length,
        files: uploadFiles.map(f => ({
          filename: '',
          original_filename: f.file.name,
          file_type: f.file.name.split('.').pop()?.toLowerCase() || 'unknown',
          file_size: f.file.size,
          status: 'error' as const,
          message: 'Upload failed',
          error_details: error instanceof Error ? error.message : 'Unknown error'
        })),
        overall_status: 'failed' as const
      };

      setUploadResponse(errorResponse);
      throw error;

    } finally {
      setIsUploading(false);
    }
  }, [uploadFiles, uploadService, simulateProgress]);

  const canUpload = uploadFiles.length > 0 && !isUploading;
  const allCompleted = uploadFiles.length > 0 && uploadFiles.every(f => f.status === 'completed');
  const hasErrors = uploadFiles.some(f => f.status === 'error');

  return {
    uploadFiles,
    isUploading,
    uploadResponse,
    canUpload,
    allCompleted,
    hasErrors,
    addFiles,
    removeFile,
    clearFiles,
    performUpload
  };
};
