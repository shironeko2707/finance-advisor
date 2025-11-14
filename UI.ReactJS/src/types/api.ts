// API response types

export interface LoginResponse {
  access_token?: string;
  token?: string;
  token_type?: string;
  expires_in?: number;
  user_id?: string | number;
  id?: string | number;
  username?: string;
  role?: string;
  user?: {
    id?: string | number;
    username?: string;
    email?: string;
    role?: string;
  };
}

export interface OtpResponse {
  success: boolean;
  message?: string;
  reset_token?: string;
}

export interface ResetPasswordResponse {
  success: boolean;
  message?: string;
}

// File Upload API types
export interface FileUploadResult {
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: 'success' | 'failed';
  message: string;
  file_path: string;
  uploaded_at: string;
}

export interface TemplateUploadResult {
  filename: string;
  original_filename: string;
  file_type: 'excel';
  file_size: number;
  status: 'success' | 'failed';
  message: string;
  file_path: string;
  uploaded_at: string;
}

export interface FileUploadsResult {
  total_files: number;
  successful_uploads: number;
  failed_uploads: number;
  files: FileUploadResult[];
  overall_status: 'success' | 'failed' | 'partial';
}

export interface GeneratedReportResult {
  report_id: number;
  filename?: string;
  original_filename?: string;
  generated_file_path?: string;
  download_url?: string;
  view_url?: string;
  file_size?: number;
  status?: 'success' | 'failed';
  message?: string;
  generated_at?: string;
}

export interface UploadWithTemplateSyncResponse {
  template_upload: TemplateUploadResult;
  file_uploads: FileUploadsResult;
  generated_report: GeneratedReportResult;
  status: string;
  message: string;
}
