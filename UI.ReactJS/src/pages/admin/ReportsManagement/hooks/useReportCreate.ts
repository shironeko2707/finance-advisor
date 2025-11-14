import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { apiService } from '@/services/ApiInterceptor.ts';
import { getFileBaseUrl } from '@/config/config';
import type { UploadWithTemplateSyncResponse } from '@/types/api';
import { useInputValidation } from '@/components/hooks/useInputValidation';

export interface InputFile {
  id: string;
  file: File;
  status: 'uploaded' | 'processing' | 'success' | 'error';
}

export interface TemplateFile {
  id: string;
  file: File;
  status: 'uploaded' | 'processing' | 'success' | 'error';
}

export interface FormData {
  report_name: string;
  template_id: string;
  file_ids: number[];
}

export interface ExcelPreviewState {
  isOpen: boolean;
  fileName: string;
  fileUrl: string;
  fileType: string;
}

export const useReportCreate = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<FormData>({
    report_name: '',
    template_id: '',
    file_ids: []
  });
  const [templateFile, setTemplateFile] = useState<TemplateFile | null>(null);
  const [inputFiles, setInputFiles] = useState<InputFile[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string>('');
  const [generatedReport, setGeneratedReport] = useState<UploadWithTemplateSyncResponse | null>(null);
  const [showSuccessModal, setShowSuccessModal] = useState(false);

  // Use the generic input validation hook
  const { createValidatedFieldOnChange } = useInputValidation();

  // Add state for Office365 preview modal
  const [excelPreviewState, setExcelPreviewState] = useState<ExcelPreviewState>({
    isOpen: false,
    fileName: '',
    fileUrl: '',
    fileType: ''
  });

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);

    files.forEach(file => {
      // Validate file type
      const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.ms-excel', // .xls
        'text/csv', // .csv
        'application/pdf' // .pdf
      ];

      if (!allowedTypes.includes(file.type)) {
        alert(`File "${file.name}" is not supported. Please upload Excel, CSV, or PDF files only.`);
        return;
      }

      const newFile: InputFile = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        file,
        status: 'uploaded'
      };

      setInputFiles(prev => [...prev, newFile]);
    });

    // Reset input
    event.target.value = '';
  };

  const handleTemplateUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);

    files.forEach(file => {
      // Validate template file type (should be Excel only)
      const allowedTypes = [
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', // .xlsx
        'application/vnd.ms-excel' // .xls
      ];

      if (!allowedTypes.includes(file.type)) {
        alert(`Template file "${file.name}" is not supported. Please upload Excel files (.xlsx or .xls) only.`);
        return;
      }

      const newTemplateFile: TemplateFile = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        file,
        status: 'uploaded'
      };
      setTemplateFile(newTemplateFile);
    });

    // Reset input
    event.target.value = '';
  };

  const removeFile = (fileId: string) => {
    setInputFiles(prev => prev.filter(f => f.id !== fileId));
  };

  const removeTemplateFile = () => {
    setTemplateFile(null);
  };

  const handleDownloadReport = async () => {
    if (!generatedReport || !generatedReport.generated_report) {
      alert('No report available for download');
      return;
    }

    try {
      const reportData = generatedReport.generated_report;
      console.log('Report data for download:', reportData);

      // Check if we have a report ID to use the proper API
      if (reportData.report_id) {
        // Use the same API service as ReportsList
        console.log('Downloading report via API service with ID:', reportData.report_id);

        const blob = await apiService.api.downloadReport(reportData.report_id);

        // Create download link using blob
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = reportData.filename || reportData.original_filename || `report-${formData.report_name}.xlsx`;

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        // Clean up the URL object
        window.URL.revokeObjectURL(url);

        console.log('Download completed via API for file:', link.download);
      } else if (reportData.generated_file_path) {
        // Fallback to direct file download if no ID available
        console.log('No report ID available, falling back to direct file download');

        const fileBaseUrl = getFileBaseUrl();
        const filePath = reportData.generated_file_path;
        const downloadUrl = `${fileBaseUrl}/${filePath}`;

        console.log('Downloading report via direct file access:');
        console.log('- File Base URL:', fileBaseUrl);
        console.log('- File Path:', filePath);
        console.log('- Complete Download URL:', downloadUrl);

        // Create a link element to trigger download
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = reportData.filename || reportData.original_filename || `report-${formData.report_name}.xlsx`;
        link.target = '_blank';

        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);

        console.log('Download initiated for file:', link.download);
      } else {
        alert('Download URL not available in the response');
      }
    } catch (error) {
      console.error('Download failed:', error);
      alert('Failed to download report. Please try again.');
    }
  };

  const handleViewReport = () => {
    if (!generatedReport || !generatedReport.generated_report) {
      alert('No report available for viewing');
      return;
    }

    try {
      const reportData = generatedReport.generated_report;

      if (reportData.generated_file_path) {
        const fileBaseUrl = getFileBaseUrl();
        const filePath = reportData.generated_file_path;
        const viewUrl = `${fileBaseUrl}/${filePath}`;

        // Use Office 365 preview modal similar to ReportsList
        setExcelPreviewState({
          isOpen: true,
          fileName: reportData.filename || reportData.original_filename || `${formData.report_name}.xlsx`,
          fileUrl: viewUrl,
          fileType: 'xlsx'
        });
      } else {
        alert('View URL not available in the response');
      }
    } catch (error) {
      console.error('View failed:', error);
      alert('Failed to view report. Trying download instead.');
      handleDownloadReport();
    }
  };

  const handleCloseSuccessModal = () => {
    setShowSuccessModal(false);
    setGeneratedReport(null);
    navigate('/reports');
  };

  const handleCreateReport = async () => {
    if (!formData.report_name.trim()) {
      alert('Report name is required.');
      return;
    }

    if (!formData.template_id && !templateFile) {
      alert('Either a template ID or a template file must be provided.');
      return;
    }

    if (formData.file_ids.length === 0 && inputFiles.length === 0) {
      alert('Either file IDs or input files must be provided.');
      return;
    }

    setLoading(true);
    setUploadProgress('Preparing files for upload...');

    try {
      // Prepare files for upload
      const inputFilesArray = inputFiles.map(fileWrapper => fileWrapper.file);

      // Determine which template to use
      const templateToUpload = templateFile ? templateFile.file : undefined;
      const templateIdToUse = templateFile ? undefined : (formData.template_id || undefined);

      // Determine which files to use
      const filesToUpload = inputFiles.length > 0 ? inputFilesArray : [];
      const fileIdsToUse = inputFiles.length > 0 ? undefined : formData.file_ids;

      setUploadProgress('Uploading template and files...');

      const response: UploadWithTemplateSyncResponse = await apiService.api.uploadWithTemplateSync(
        formData.report_name,
        templateIdToUse,
        templateToUpload,
        fileIdsToUse,
        filesToUpload,
      );

      setUploadProgress('Processing upload results...');

      // Check if upload was successful
      if (response.status === 'success' && response.template_upload.status === 'success') {
        setUploadProgress('Upload completed successfully!');
        setGeneratedReport(response);
        setShowSuccessModal(true);

        // Don't navigate immediately, let user view/download first
      } else {
        // Handle partial success or errors
        const errorMessages = [];

        if (response.template_upload.status !== 'success') {
          errorMessages.push(`Template upload failed: ${response.template_upload.message}`);
        }

        if (response.file_uploads.failed_uploads > 0) {
          const failedFiles = response.file_uploads.files
            .filter(file => file.status === 'failed')
            .map(file => `${file.original_filename}: ${file.message}`)
            .join('\n');
          errorMessages.push(`Failed file uploads:\n${failedFiles}`);
        }

        if (errorMessages.length > 0) {
          alert(`Upload completed with errors:\n${errorMessages.join('\n\n')}`);
        }
      }
    } catch (error) {
      console.error('Failed to create report:', error);
      setUploadProgress('Upload failed');
      alert(`Failed to create report: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(false);
      setUploadProgress('');
    }
  };

  const navigateToReports = () => {
    navigate('/reports');
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const isFormValid = () => {
    const isReportNameValid = formData.report_name.trim() !== '';
    const isTemplateValid = formData.template_id !== '' || templateFile !== null;
    const isFilesValid = formData.file_ids.length > 0 || inputFiles.length > 0;

    return isReportNameValid && isTemplateValid && isFilesValid;
  };

  const closeExcelPreview = () => {
    setExcelPreviewState({ ...excelPreviewState, isOpen: false });
  };

  return {
    // State
    formData,
    setFormData,
    templateFile,
    inputFiles,
    loading,
    uploadProgress,
    generatedReport,
    showSuccessModal,
    excelPreviewState,

    // Handlers
    handleFileUpload,
    handleTemplateUpload,
    removeFile,
    removeTemplateFile,
    handleDownloadReport,
    handleViewReport,
    handleCloseSuccessModal,
    handleCreateReport,
    navigateToReports,
    closeExcelPreview,

    // Utils
    formatFileSize,
    isFormValid,
    createValidatedFieldOnChange,
  };
};
