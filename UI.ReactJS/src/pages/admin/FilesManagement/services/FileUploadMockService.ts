import type { FileUploadResponse, UploadedFileResult } from '@/types/file';

export class FileUploadMockService {
  static async uploadMultipleFiles(files: File[]): Promise<FileUploadResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1500 + Math.random() * 1000));

    const uploadResults: UploadedFileResult[] = files.map((file, index) => {
      // Simulate some upload failures occasionally
      const isSuccess = Math.random() > 0.1; // 90% success rate
      console.log(index);

      const result: UploadedFileResult = {
        filename: `${this.generateUUID()}.${this.getFileExtension(file.name)}`,
        original_filename: file.name,
        file_type: this.getFileType(file),
        file_size: file.size,
        status: isSuccess ? 'success' : 'error',
        message: isSuccess ? 'File uploaded successfully' : 'Upload failed due to server error',
        uploaded_at: new Date().toISOString()
      };

      if (isSuccess) {
        result.file_path = `storage/uploads\\${result.filename}`;
      } else {
        result.error_details = 'Simulated upload error for testing';
      }

      return result;
    });

    const successful_uploads = uploadResults.filter(r => r.status === 'success').length;
    const failed_uploads = uploadResults.filter(r => r.status === 'error').length;

    return {
      total_files: files.length,
      successful_uploads,
      failed_uploads,
      files: uploadResults,
      overall_status: failed_uploads === 0 ? 'success' :
                     successful_uploads === 0 ? 'failed' : 'partial'
    };
  }

  private static generateUUID(): string {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
      const r = Math.random() * 16 | 0;
      const v = c == 'x' ? r : (r & 0x3 | 0x8);
      return v.toString(16);
    });
  }

  private static getFileExtension(filename: string): string {
    return filename.split('.').pop()?.toLowerCase() || 'unknown';
  }

  private static getFileType(file: File): string {
    const extension = this.getFileExtension(file.name);
    if (['pdf'].includes(extension)) return 'pdf';
    if (['xlsx', 'xls', 'xlsm'].includes(extension)) return 'excel';
    return 'unknown';
  }
}
