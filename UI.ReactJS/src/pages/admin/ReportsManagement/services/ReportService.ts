import { apiService } from '@/services/ApiInterceptor.ts';
import type { Report, ReportListResponse, ReportFilters } from '../types';

export class ReportService {
  /**
   * Get reports from the API
   */
  static async getReports(): Promise<ReportListResponse> {
    try {
      const response = await apiService.api.getReports();
      return response as ReportListResponse;
    } catch (error) {
      console.error('Failed to fetch reports:', error);
      throw new Error('Failed to fetch reports');
    }
  }

  /**
   * Delete a report by ID
   */
  static async deleteReport(reportId: number): Promise<void> {
    try {
      await apiService.api.deleteReport(reportId);
    } catch (error) {
      console.error('Failed to delete report:', error);
      throw new Error('Failed to delete report');
    }
  }

  /**
   * Download a report file
   */
  static async downloadReport(reportId: number): Promise<Blob> {
    try {
      const blob = await apiService.api.downloadReport(reportId);
      return blob;
    } catch (error) {
      console.error('Failed to download report:', error);
      throw new Error('Failed to download report');
    }
  }

  /**
   * Get PDF content for viewing
   */
  static async getPdfReport(reportId: number): Promise<Blob> {
    try {
      const blob = await apiService.api.getPdfReport(reportId);
      return blob;
    } catch (error) {
      console.error('Failed to get PDF report:', error);
      throw new Error('Failed to get PDF report');
    }
  }

  /**
   * Helper function to filter reports client-side
   * (since the API doesn't support server-side filtering yet)
   */
  static filterReports(reports: Report[], filters: ReportFilters): Report[] {
    return reports.filter(report => {
      const matchesName = !filters.reportName || 
        report.report_name.toLowerCase().includes(filters.reportName.toLowerCase());
      
      const matchesTemplate = !filters.template || 
        report.template_filename.toLowerCase().includes(filters.template.toLowerCase());
      
      const matchesDate = !filters.createDate || 
        report.generated_at.startsWith(filters.createDate);
      
      const matchesCreator = !filters.creator || 
        report.generated_by.toString() === filters.creator;
      
      return matchesName && matchesTemplate && matchesDate && matchesCreator;
    });
  }

  /**
   * Get unique template names for filter options
   */
  static getAvailableTemplates(reports: Report[]): string[] {
    const templates = reports.map(report => report.template_filename);
    return [...new Set(templates)].sort();
  }

  /**
   * Get unique creator IDs for filter options
   */
  static getAvailableCreators(reports: Report[]): string[] {
    const creators = reports.map(report => report.generated_by.toString());
    return [...new Set(creators)].sort();
  }

  /**
   * Format file size for display
   */
  static formatFileSize(bytes: number): string {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  /**
   * Format date for display
   */
  static formatDate(isoString: string): string {
    try {
      const date = new Date(isoString);
      return date.toLocaleString();
    } catch (error) {
      return isoString;
    }
  }

  /**
   * Get display name for status
   */
  static getStatusDisplay(status: string): { text: string; color: string } {
    switch (status) {
      case 'success':
        return { text: 'Completed', color: 'text-green-600' };
      case 'processing':
        return { text: 'Processing', color: 'text-yellow-600' };
      case 'failed':
        return { text: 'Failed', color: 'text-red-600' };
      default:
        return { text: status, color: 'text-gray-600' };
    }
  }
}
