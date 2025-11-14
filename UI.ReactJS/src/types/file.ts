export interface UploadedFile {
  id: number;
  original_filename: string;
  stored_filename: string;
  file_type: 'excel' | 'pdf';
  file_path: string;
  file_size: number;
  mimetype: string;
  uploaded_at: string;
  uploaded_by: number;
  uploader: string;
  status: 'success' | 'error' | 'pending';
  error_message?: string | null;
}

export interface FileListResponse {
  files: UploadedFile[];
  total: number;
  user_id: number;
}

export interface FileFilters {
  search: string;
  uploadedUser: string;
}

export interface FileUploadProgress {
  id: string;
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
}

export interface FileAction {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  className?: string;
  disabled?: boolean;
}

export interface FileUploadResponse {
  total_files: number;
  successful_uploads: number;
  failed_uploads: number;
  files: UploadedFileResult[];
  overall_status: 'success' | 'partial' | 'failed';
}

export interface UploadedFileResult {
  filename: string;
  original_filename: string;
  file_type: string;
  file_size: number;
  status: 'success' | 'error';
  message: string;
  file_path?: string;
  uploaded_at?: string;
  error_details?: string;
}
