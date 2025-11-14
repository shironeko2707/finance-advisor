export interface Report {
  id: number;
  report_name: string;
  report_filename: string;
  report_file_path: string;
  report_file_size: number;
  report_content_type: string;
  template_filename: string;
  input_files_count: number;
  input_files_info: InputFileInfo[];
  generated_at: string;
  generated_by: number;
  generation_status: 'success' | 'failed' | 'processing';
  generation_time_seconds: number;
  is_downloaded: boolean;
  download_count: number;
  description: string;
  status: "completed" | "failed";
  user_name: string;
}

export interface InputFileInfo {
  id: number;
  original_filename: string;
  stored_filename: string;
  file_path: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
}

export interface ReportFilters {
  reportName?: string;
  template?: string;
  createDate?: string;
  creator?: string;
}

export interface ReportListResponse {
  reports: Report[];
  total: number;
  user_id: number;
}

export interface CreateReportRequest {
  reportName: string;
  template: string;
  description?: string;
}

export interface UpdateReportRequest {
  reportName?: string;
  template?: string;
  description?: string;
}

export type ReportAction = 'view' | 'download-excel' | 'download-pdf' | 'delete';

export interface DownloadReportRequest {
  reportId: number;
  format: 'excel' | 'pdf';
}