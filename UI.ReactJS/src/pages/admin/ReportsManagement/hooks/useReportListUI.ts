import { useState } from 'react';
import type { Report } from '../types';

interface PdfViewerState {
  isOpen: boolean;
  reportName: string;
  reportId: number;
}

interface ReportMetadataModal {
  isOpen: boolean;
  report: Report | null;
}

interface ExcelPreviewState {
  isOpen: boolean;
  fileName: string;
  fileUrl: string;
  fileType: string;
}

interface UseReportsListUIReturn {
  // Action menu state
  openActionMenu: number | null;
  setOpenActionMenu: (id: number | null) => void;
  toggleActionMenu: (reportId: number) => void;

  // PDF viewer modal
  pdfViewerState: PdfViewerState;
  setPdfViewerState: (state: PdfViewerState) => void;

  // Report metadata modal
  reportMetadataModal: ReportMetadataModal;
  setReportMetadataModal: (state: ReportMetadataModal) => void;

  // Excel preview modal
  excelPreviewState: ExcelPreviewState;
  setExcelPreviewState: (state: ExcelPreviewState) => void;

  // Action handlers
  handleViewReport: (reportId: number, reports: Report[]) => void;
  handlePreviewExcel: (reportId: number, reports: Report[]) => void;
  handleDeleteReport: (reportId: number, deleteReport: (id: number) => Promise<void>) => Promise<void>;
  handleDownloadReport: (
    reportId: number,
    format: 'excel' | 'pdf',
    reports: Report[],
    downloadReport: (id: number, format: 'excel' | 'pdf') => Promise<void>
  ) => Promise<void>;
  handleViewPdf: (reportId: number, reports: Report[]) => Promise<void>;

  // Utility functions
  generatePageNumbers: (currentPage: number, totalPages: number) => number[];
}

export const useReportListUI = (): UseReportsListUIReturn => {
  const [openActionMenu, setOpenActionMenu] = useState<number | null>(null);
  const [pdfViewerState, setPdfViewerState] = useState<PdfViewerState>({
    isOpen: false,
    reportName: '',
    reportId: 0
  });
  const [reportMetadataModal, setReportMetadataModal] = useState<ReportMetadataModal>({
    isOpen: false,
    report: null
  });
  const [excelPreviewState, setExcelPreviewState] = useState<ExcelPreviewState>({
    isOpen: false,
    fileName: '',
    fileUrl: '',
    fileType: ''
  });

  const toggleActionMenu = (reportId: number) => {
    setOpenActionMenu(openActionMenu === reportId ? null : reportId);
  };

  const handleViewReport = (reportId: number, reports: Report[]) => {
    const report = reports.find(r => r.id === reportId);
    if (report) {
      setReportMetadataModal({
        isOpen: true,
        report: report
      });
    }
  };

  const handlePreviewExcel = async (reportId: number, reports: Report[]) => {
    const report = reports.find(r => r.id === reportId);
    if (report) {
      try {
        // Get the Excel file URL for preview using VITE_FILE_BASE_URL + storage path
        const fileBaseUrl = import.meta.env.VITE_FILE_BASE_URL || 'http://hndw-pthoang2:8000/';
        const previewUrl = `${fileBaseUrl}/${report.report_file_path}`;
        setExcelPreviewState({
          isOpen: true,
          fileName: report.report_name + '.xlsx',
          fileUrl: previewUrl,
          fileType: 'xlsx'
        });
      } catch (error) {
        console.error('Failed to get Excel preview URL:', error);
      }
      setOpenActionMenu(null);
    }
  };

  const handleDeleteReport = async (reportId: number, deleteReport: (id: number) => Promise<void>) => {
    if (window.confirm('Are you sure you want to delete this report?')) {
      await deleteReport(reportId);
      setOpenActionMenu(null);
    }
  };

  const handleDownloadReport = async (
    reportId: number,
    format: 'excel' | 'pdf',
    reports: Report[],
    downloadReport: (id: number, format: 'excel' | 'pdf') => Promise<void>
  ) => {
    if (format === 'pdf') {
      // Open PDF in viewer modal instead of downloading
      const report = reports.find(r => r.id === reportId);
      if (report) {
        setPdfViewerState({
          isOpen: true,
          reportName: report.report_name,
          reportId: reportId
        });
      }
    } else {
      // Handle Excel download as before
      await downloadReport(reportId, format);
    }
    setOpenActionMenu(null);
  };

  const handleViewPdf = async (reportId: number, reports: Report[]) => {
    const report = reports.find(r => r.id === reportId);
    if (report) {
      setPdfViewerState({
        isOpen: true,
        reportName: report.report_name,
        reportId: reportId
      });
    }
  };

  const generatePageNumbers = (currentPage: number, totalPages: number): number[] => {
    const pages: number[] = [];
    const maxVisiblePages = 5;
    const halfVisible = Math.floor(maxVisiblePages / 2);

    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, currentPage + halfVisible);

    // Adjust if we're near the beginning or end
    if (endPage - startPage < maxVisiblePages - 1) {
      if (startPage === 1) {
        endPage = Math.min(totalPages, maxVisiblePages);
      } else {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  return {
    openActionMenu,
    setOpenActionMenu,
    toggleActionMenu,
    pdfViewerState,
    setPdfViewerState,
    reportMetadataModal,
    setReportMetadataModal,
    excelPreviewState,
    setExcelPreviewState,
    handleViewReport,
    handlePreviewExcel,
    handleDeleteReport,
    handleDownloadReport,
    handleViewPdf,
    generatePageNumbers
  };
};
