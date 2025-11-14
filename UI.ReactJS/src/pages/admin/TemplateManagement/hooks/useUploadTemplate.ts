import { useState } from 'react';
import { apiService } from '@/services/ApiInterceptor';

interface UploadState {
  uploading: boolean;
  error: string | null;
  success: boolean;
}

interface UploadPayload {
  file: File;
  name: string;
  category: string;
  version: string;
}

export const useUploadTemplate = () => {
  const [uploadState, setUploadState] = useState<UploadState>({
    uploading: false,
    error: null,
    success: false,
  });

  const uploadTemplate = async (payload: UploadPayload) => {
    setUploadState({ uploading: true, error: null, success: false });

    const formData = new FormData();
    formData.append('file', payload.file);
    formData.append('name', payload.name);
    formData.append('category', payload.category);
    formData.append('version', payload.version);

    try {
      await apiService.api.uploadTemplate(formData);
      setUploadState({ uploading: false, error: null, success: true });
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'An unknown error occurred';
      setUploadState({ uploading: false, error: errorMessage, success: false });
    }
  };

  const resetUploadState = () => {
    setUploadState({
      uploading: false,
      error: null,
      success: false,
    });
  };

  return {
    ...uploadState,
    uploadTemplate,
    resetUploadState,
  };
};