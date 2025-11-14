import { useState, useEffect } from 'react';
import type { Report, ReportFilters } from '../types';
import { mockReports, availableTemplates, availableCreators } from '../services/datafix.ts';
import { ReportMockService, ReportService } from '../services';
import { convertTimestamp } from '@/utils/common.ts';

interface UseReportListOptions {
  useFixture?: boolean;
}

interface UseReportListReturn {
  reports: Report[];
  loading: boolean;
  error: string | null;
  success: string | null;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalReports: number;
  availableUsers: {
    user_id: number;
    full_name: string;
  }[];
  
  // Filter state
  filters: ReportFilters;
  filteredReports: Report[];
  
  // Actions
  refreshReports: () => Promise<void>;
  deleteReport: (reportId: number) => Promise<void>;
  downloadReport: (reportId: number, format: 'excel' | 'pdf') => Promise<void>;
  
  // Pagination
  goToPage: (page: number) => void;
  goToNextPage: () => void;
  goToPrevPage: () => void;
  changePageSize: (size: number) => void;
  
  // Filtering
  updateFilters: (newFilters: Partial<ReportFilters>) => void;
  clearFilters: () => void;
  
  // Data for filters
  availableTemplates: string[];
  availableCreators: string[];
}

export const useReportList = (options: UseReportListOptions = {}): UseReportListReturn => {
  const { useFixture = false } = options;
  
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(10);
  
  // Filter state
  const [filters, setFilters] = useState<ReportFilters>({
    reportName: '',
    template: '',
    createDate: '',
    creator: ''
  });

  // Filter reports based on current filters
  const filteredReports = reports.filter(report => {
    return (
      (!filters.reportName || report.report_name?.trim()?.toLowerCase()?.includes(filters.reportName?.trim()?.toLowerCase())) &&
      (!filters.template || report.template_filename?.trim()?.toLowerCase()?.includes(filters.template?.trim()?.toLowerCase())) &&
      (!filters.creator || report.generated_by?.toString() === filters.creator) &&
      (!filters.createDate || (report.generated_at && convertTimestamp(report.generated_at, true) === filters.createDate))
    );
  });

  // Pagination calculations
  const totalReports = filteredReports.length;
  const totalPages = Math.ceil(totalReports / pageSize);
  const startIndex = (currentPage - 1) * pageSize;
  const endIndex = startIndex + pageSize;
  const paginatedReports = filteredReports.slice(startIndex, endIndex);

  const availableUsers = reports.map(item => {
    return {
      user_id: item.generated_by,
      full_name: item.user_name.toString(),
    }
  })

  const loadReports = async () => {
    try {
      setLoading(true);
      setError(null);
      
      let reportData: Report[];
      
      if (useFixture) {
        // Simulate API delay for realistic testing
        await new Promise(resolve => setTimeout(resolve, 500));
        reportData = [...mockReports]; // Copy to avoid mutations
      } else {
        const response = await ReportService.getReports();
        reportData = response.reports;
      }
      
      setReports(reportData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load reports');
      console.error('Error loading reports:', err);
    } finally {
      setLoading(false);
    }
  };

  const deleteReport = async (reportId: number) => {
    try {
      setError(null);
      
      if (useFixture) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 300));
        
        setReports(prev => prev.filter(report => report.id !== reportId));
        
        // Also update the original mock data for consistency
        const reportIndex = mockReports.findIndex(report => report.id === reportId);
        if (reportIndex !== -1) {
          mockReports.splice(reportIndex, 1);
        }
      } else {
        await ReportService.deleteReport(reportId);
        setReports(prev => prev.filter(report => report.id !== reportId));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete report');
      console.error('Error deleting report:', err);
    }
  };

  const downloadReport = async (reportId: number, format: 'excel' | 'pdf') => {
    try {
      setError(null);
      
      if (useFixture) {
        // For development, just show a success message
        await new Promise(resolve => setTimeout(resolve, 1000));
        
        // Create a mock download link
        const downloadUrl = await ReportMockService.generateReportUrl(reportId.toString(), format);
        
        // In a real implementation, you might:
        // 1. Open the download URL in a new tab
        // 2. Trigger a file download
        // 3. Show a download progress indicator
        
        console.log(`Mock download: ${downloadUrl}`);
        alert(`Mock download started for ${format.toUpperCase()} format`);
      } else {
        const blob = await ReportService.downloadReport(reportId);
        
        // Find the report to get the filename
        const report = reports.find(r => r.id === reportId);
        const filename = report?.report_filename || `report-${reportId}.xlsx`;
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Update download count if needed
        setReports(prev => prev.map(report => 
          report.id === reportId 
            ? { ...report, is_downloaded: true, download_count: report.download_count + 1 }
            : report
        ));
        setSuccess("Download successfully");
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to download report');
      console.error('Error downloading report:', err);
    }
  };

  const refreshReports = async () => {
    await loadReports();
  };

  // Pagination functions
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  };

  const changePageSize = (size: number) => {
    setPageSize(size);
    setCurrentPage(1); // Reset to first page when changing page size
  };

  // Filter functions
  const updateFilters = (newFilters: Partial<ReportFilters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(1); // Reset to first page when filtering
  };

  const clearFilters = () => {
    setFilters({
      reportName: '',
      template: '',
      createDate: '',
      creator: ''
    });
    setCurrentPage(1);
  };

  // Calculate dynamic filter options from reports
  const dynamicAvailableTemplates = useFixture 
    ? availableTemplates 
    : ReportService.getAvailableTemplates(reports);
    
  const dynamicAvailableCreators = useFixture 
    ? availableCreators 
    : ReportService.getAvailableCreators(reports);

  // Load reports on mount and when filters change
  useEffect(() => {
    loadReports();
  }, [useFixture]); // Only reload when useFixture changes, not filters (we filter client-side for mock data)

  return {
    reports: paginatedReports,
    loading,
    error,
    success,
    availableUsers,
    currentPage,
    totalPages,
    pageSize,
    totalReports,
    
    filters,
    filteredReports,
    
    refreshReports,
    deleteReport,
    downloadReport,
    
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    
    updateFilters,
    clearFilters,
    
    availableTemplates: dynamicAvailableTemplates,
    availableCreators: dynamicAvailableCreators,
  };
};