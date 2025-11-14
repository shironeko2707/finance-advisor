import { apiService } from '@/services/ApiInterceptor.ts';
import type { FileUploadResponse } from '@/types/file';

export class FileUploadService {
  static async uploadMultipleFiles(files: File[]): Promise<FileUploadResponse> {
    const formData = new FormData();

    // Add all files to the form data
    files.forEach((file) => {
      formData.append('files', file);
    });

    try {
      const url = apiService.getApiUrl('/files/upload/multiple');
      const response = await fetch(url, {
        method: 'POST',
        headers: apiService.getFileUploadHeaders(true),
        body: formData
      });

      if (!response.ok) {
        throw new Error(`Upload failed: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      // Handle API errors and return a failed response
      console.error('File upload failed:', error);

      return {
        total_files: files.length,
        successful_uploads: 0,
        failed_uploads: files.length,
        files: files.map(file => ({
          filename: '',
          original_filename: file.name,
          file_type: this.getFileType(file),
          file_size: file.size,
          status: 'error' as const,
          message: 'Upload failed due to network error',
          error_details: error instanceof Error ? error.message : 'Unknown error'
        })),
        overall_status: 'failed' as const
      };
    }
  }

  private static getFileType(file: File): string {
    const extension = file.name.split('.').pop()?.toLowerCase() || 'unknown';
    if (['pdf'].includes(extension)) return 'pdf';
    if (['xlsx', 'xls', 'xlsm'].includes(extension)) return 'excel';
    return 'unknown';
  }

  static isValidFileType(file: File): boolean {
    const validTypes = [
      'application/pdf',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-excel.sheet.macroEnabled.12'
    ];
    const fileExtensionMatch = file.name.toLowerCase().match(/\.(pdf|xlsx?|xlsm)$/);
    return validTypes.includes(file.type) || Boolean(fileExtensionMatch);
  }
}
