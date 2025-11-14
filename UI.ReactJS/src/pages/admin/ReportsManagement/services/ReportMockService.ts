import type { 
  Report, 
  ReportFilters, 
  ReportListResponse, 
  CreateReportRequest, 
  UpdateReportRequest,
  DownloadReportRequest 
} from '../types';

// Mock data that matches the ReportsManagement types
const mockReports: Report[] = [
  {
    id: 1,
    report_name: 'UOB Financial Review Q3 2024',
    report_filename: 'uob_financial_review_q3_2024.xlsx',
    report_file_path: 'reports/2024/q3/uob_financial_review_q3_2024.xlsx',
    report_file_size: 2048576, // 2MB
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Company results',
    input_files_count: 3,
    input_files_info: [
      {
        id: 1,
        original_filename: 'balance_sheet.xlsx',
        stored_filename: 'bs_20240915_001.xlsx',
        file_path: 'uploads/2024/09/bs_20240915_001.xlsx',
        file_type: 'xlsx',
        file_size: 512000,
        uploaded_at: '2024-09-15T10:30:00Z'
      },
      {
        id: 2,
        original_filename: 'income_statement.xlsx',
        stored_filename: 'is_20240915_002.xlsx',
        file_path: 'uploads/2024/09/is_20240915_002.xlsx',
        file_type: 'xlsx',
        file_size: 384000,
        uploaded_at: '2024-09-15T10:32:00Z'
      },
      {
        id: 3,
        original_filename: 'cash_flow.xlsx',
        stored_filename: 'cf_20240915_003.xlsx',
        file_path: 'uploads/2024/09/cf_20240915_003.xlsx',
        file_type: 'xlsx',
        file_size: 256000,
        uploaded_at: '2024-09-15T10:35:00Z'
      }
    ],
    generated_at: '2024-09-15T11:00:00Z',
    generated_by: 1,
    generation_status: 'success',
    generation_time_seconds: 45,
    is_downloaded: true,
    download_count: 3
  },
  {
    id: 2,
    report_name: 'DBS Quarterly Performance Report',
    report_filename: 'dbs_quarterly_performance_q3_2024.xlsx',
    report_file_path: 'reports/2024/q3/dbs_quarterly_performance_q3_2024.xlsx',
    report_file_size: 1847296, // 1.8MB
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Quarterly Report',
    input_files_count: 2,
    input_files_info: [
      {
        id: 4,
        original_filename: 'quarterly_data.xlsx',
        stored_filename: 'qd_20240914_001.xlsx',
        file_path: 'uploads/2024/09/qd_20240914_001.xlsx',
        file_type: 'xlsx',
        file_size: 768000,
        uploaded_at: '2024-09-14T14:20:00Z'
      },
      {
        id: 5,
        original_filename: 'performance_metrics.xlsx',
        stored_filename: 'pm_20240914_002.xlsx',
        file_path: 'uploads/2024/09/pm_20240914_002.xlsx',
        file_type: 'xlsx',
        file_size: 432000,
        uploaded_at: '2024-09-14T14:25:00Z'
      }
    ],
    generated_at: '2024-09-14T15:00:00Z',
    generated_by: 2,
    generation_status: 'success',
    generation_time_seconds: 62,
    is_downloaded: false,
    download_count: 0
  },
  {
    id: 3,
    report_name: 'OCBC Risk Assessment Report',
    report_filename: 'ocbc_risk_assessment_sep_2024.xlsx',
    report_file_path: 'reports/2024/09/ocbc_risk_assessment_sep_2024.xlsx',
    report_file_size: 3145728, // 3MB
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Risk Assessment',
    input_files_count: 5,
    input_files_info: [
      {
        id: 6,
        original_filename: 'credit_data.xlsx',
        stored_filename: 'cd_20240913_001.xlsx',
        file_path: 'uploads/2024/09/cd_20240913_001.xlsx',
        file_type: 'xlsx',
        file_size: 1024000,
        uploaded_at: '2024-09-13T09:15:00Z'
      }
    ],
    generated_at: '2024-09-13T10:30:00Z',
    generated_by: 1,
    generation_status: 'processing',
    generation_time_seconds: 0,
    is_downloaded: false,
    download_count: 0
  }
];

const mockTemplates = ['Company results', 'Quarterly Report', 'Risk Assessment', 'Annual Summary'];
const mockCreators = ['John Smith', 'Jane Doe', 'Mike Johnson'];

// Mock service with actual implementations for development
class ReportServiceImpl {
  private baseUrl = '/api/reports';
  private reports: Report[] = [...mockReports];

  async getReports(filters: ReportFilters = {}, page = 1, pageSize = 10): Promise<ReportListResponse> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    let filteredReports = [...this.reports];

    // Apply filters
    if (filters.reportName) {
      filteredReports = filteredReports.filter(report =>
        report.report_name.toLowerCase().includes(filters.reportName!.toLowerCase())
      );
    }

    if (filters.template) {
      filteredReports = filteredReports.filter(report =>
        report.template_filename === filters.template
      );
    }

    if (filters.creator) {
      // Note: In real implementation, you'd filter by creator name, not ID
      // For now, we'll use the generated_by ID as a simple filter
      const creatorId = filters.creator === 'John Smith' ? 1 : filters.creator === 'Jane Doe' ? 2 : 3;
      filteredReports = filteredReports.filter(report =>
        report.generated_by === creatorId
      );
    }

    if (filters.createDate) {
      filteredReports = filteredReports.filter(report =>
        report.generated_at.includes(filters.createDate!)
      );
    }

    // Apply pagination
    const startIndex = (page - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    const paginatedReports = filteredReports.slice(startIndex, endIndex);

    return {
      reports: paginatedReports,
      total: filteredReports.length,
      user_id: 1 // Mock user ID
    };
  }

  async getReportById(id: string): Promise<Report> {
    await new Promise(resolve => setTimeout(resolve, 200));

    const reportId = parseInt(id);
    const report = this.reports.find(r => r.id === reportId);

    if (!report) {
      throw new Error(`Report with ID ${id} not found`);
    }

    return report;
  }

  async createReport(request: CreateReportRequest): Promise<Report> {
    await new Promise(resolve => setTimeout(resolve, 500));

    const newReport: Report = {
      id: Math.max(...this.reports.map(r => r.id)) + 1,
      report_name: request.reportName,
      report_filename: `${request.reportName.toLowerCase().replace(/\s+/g, '_')}.xlsx`,
      report_file_path: `reports/2024/09/${request.reportName.toLowerCase().replace(/\s+/g, '_')}.xlsx`,
      report_file_size: Math.floor(Math.random() * 3000000) + 500000, // Random size between 500KB-3.5MB
      report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      template_filename: request.template,
      input_files_count: 0,
      input_files_info: [],
      generated_at: new Date().toISOString(),
      generated_by: 1,
      generation_status: 'success',
      generation_time_seconds: Math.floor(Math.random() * 60) + 10,
      is_downloaded: false,
      download_count: 0
    };

    this.reports.unshift(newReport);
    return newReport;
  }

  async updateReport(id: string, request: UpdateReportRequest): Promise<Report> {
    await new Promise(resolve => setTimeout(resolve, 300));

    const reportId = parseInt(id);
    const reportIndex = this.reports.findIndex(r => r.id === reportId);

    if (reportIndex === -1) {
      throw new Error(`Report with ID ${id} not found`);
    }

    // Update the report
    if (request.reportName) {
      this.reports[reportIndex].report_name = request.reportName;
      this.reports[reportIndex].report_filename = `${request.reportName.toLowerCase().replace(/\s+/g, '_')}.xlsx`;
    }

    if (request.template) {
      this.reports[reportIndex].template_filename = request.template;
    }

    return this.reports[reportIndex];
  }

  async deleteReport(id: string): Promise<void> {
    await new Promise(resolve => setTimeout(resolve, 200));

    const reportId = parseInt(id);
    const reportIndex = this.reports.findIndex(r => r.id === reportId);

    if (reportIndex === -1) {
      throw new Error(`Report with ID ${id} not found`);
    }

    this.reports.splice(reportIndex, 1);
  }

  async downloadReport(request: DownloadReportRequest): Promise<Blob> {
    await new Promise(resolve => setTimeout(resolve, 1000));

    // Create a mock Excel blob for download
    console.log(request);
    const mockContent = 'Mock Excel file content for report download';
    return new Blob([mockContent], {
      type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    });
  }

  async generateReportUrl(reportId: string, format: 'excel' | 'pdf'): Promise<string> {
    await new Promise(resolve => setTimeout(resolve, 300));
    // For development, return a mock URL
    return `${this.baseUrl}/${reportId}/download?format=${format}&token=mock-token`;
  }

  // Additional helper methods for the UI
  async getAvailableTemplates(): Promise<string[]> {
    await new Promise(resolve => setTimeout(resolve, 100));
    return [...mockTemplates];
  }

  async getAvailableCreators(): Promise<string[]> {
    await new Promise(resolve => setTimeout(resolve, 100));
    return [...mockCreators];
  }
}

export const ReportMockService = new ReportServiceImpl();