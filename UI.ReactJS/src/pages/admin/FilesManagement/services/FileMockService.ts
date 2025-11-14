import type { UploadedFile, FileListResponse } from '@/types/file';

// Mock data that matches the API response format
const mockFiles: UploadedFile[] = [
  {
    file_type: "excel",
    stored_filename: "726ad0b4-869e-4860-927e-f51c4ae609cd.xlsx",
    mimetype: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    uploaded_at: "2025-08-21T07:42:43.665597",
    error_message: null,
    id: 1,
    original_filename: "240826-UOB Financial Review-FullInput.xlsx",
    file_path: "storage/uploads\\726ad0b4-869e-4860-927e-f51c4ae609cd.xlsx",
    file_size: 39260,
    uploaded_by: 1,
    status: "success"
  },
  {
    file_type: "pdf",
    stored_filename: "c0d7b665-87e4-4753-bed9-6989adf38012.pdf",
    mimetype: "application/pdf",
    uploaded_at: "2025-08-21T07:42:43.699023",
    error_message: null,
    id: 2,
    original_filename: "UOB - selected-financial-statements-2024-english 1.pdf",
    file_path: "storage/uploads\\c0d7b665-87e4-4753-bed9-6989adf38012.pdf",
    file_size: 178349,
    uploaded_by: 1,
    status: "success"
  },
  {
    file_type: "excel",
    stored_filename: "7712344a-5417-4d5e-89a6-4e35bdba312a.xlsx",
    mimetype: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    uploaded_at: "2025-08-21T08:34:36.542173",
    error_message: null,
    id: 3,
    original_filename: "240826-UOB Financial Review-FullInput.xlsx",
    file_path: "storage/uploads\\7712344a-5417-4d5e-89a6-4e35bdba312a.xlsx",
    file_size: 39260,
    uploaded_by: 1,
    status: "success"
  },
  {
    file_type: "pdf",
    stored_filename: "294511c7-2103-4db9-a9a4-a228165166cc.pdf",
    mimetype: "application/pdf",
    uploaded_at: "2025-08-21T08:34:36.568115",
    error_message: null,
    id: 4,
    original_filename: "UOB - selected-financial-statements-2024-english 1.pdf",
    file_path: "storage/uploads\\294511c7-2103-4db9-a9a4-a228165166cc.pdf",
    file_size: 178349,
    uploaded_by: 1,
    status: "success"
  },
  {
    file_type: "excel",
    stored_filename: "2cceadbe-9e44-4416-935c-278421a50d07.xlsx",
    mimetype: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    uploaded_at: "2025-08-23T06:59:50.536851",
    error_message: null,
    id: 5,
    original_filename: "Xiaomi 1Q2025 Result-250528 Template.xlsx",
    file_path: "storage/uploads\\2cceadbe-9e44-4416-935c-278421a50d07.xlsx",
    file_size: 52952,
    uploaded_by: 999999,
    status: "success"
  }
];

export class FileMockService {
  static async getFiles(): Promise<FileListResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500));

    return {
      files: mockFiles,
      total: mockFiles.length,
      user_id: 999999
    };
  }

  static async deleteFile(fileId: number): Promise<boolean> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));

    const index = mockFiles.findIndex(f => f.id === fileId);
    if (index > -1) {
      mockFiles.splice(index, 1);
      return true;
    }
    return false;
  }
}
