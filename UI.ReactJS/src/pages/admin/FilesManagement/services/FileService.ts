import { apiService } from '@/services/ApiInterceptor.ts';
import type { FileListResponse } from '@/types/file';

export class FileService {
  static async getFiles(): Promise<FileListResponse> {
    return await apiService.request<FileListResponse>(
        apiService.getApiUrl('/files/list'),
        {
            method: 'GET',
        });
  }

  static async deleteFile(fileId: number): Promise<boolean> {
    try {
      await apiService.request(
        apiService.getApiUrl(`/files/${fileId}`),
        {
          method: 'DELETE',
        }
      );
      return true;
    } catch (error) {
      console.error('Error deleting file:', error);
      return false;
    }
  }

  static async downloadFile(fileId: number): Promise<Blob> {
    try {
      return await apiService.api.downloadFile(fileId);
    } catch (error) {
      console.error('Error downloading file:', error);
      throw error;
    }
  }
}
