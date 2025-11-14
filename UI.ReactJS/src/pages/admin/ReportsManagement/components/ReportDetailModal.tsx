import React from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Files, Layout, FileText, X } from 'lucide-react';
import type { Report } from '../types/report';

interface ReportDetailModalProps {
  isOpen: boolean;
  report: Report | null;
  onClose: () => void;
}

export const ReportDetailModal: React.FC<ReportDetailModalProps> = ({
  isOpen,
  report,
  onClose
}) => {
  if (!isOpen || !report) {
    return null;
  }

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'success':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      case 'processing':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">Report Details</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Files className="w-4 h-4 mr-2 text-blue-600" />
              Basic Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Report Name</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {report.report_name}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Report ID</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border font-mono">
                  {report.id}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">File Name</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {report.report_filename}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">File Size</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {formatFileSize(report.report_file_size)}
                </p>
              </div>
            </div>
          </div>

          {/* Template Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Layout className="w-4 h-4 mr-2 text-purple-600" />
              Template Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Template</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {report.template_filename}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Status</Label>
                <div className="mt-1">
                  <span className={`inline-flex px-2 py-1 text-sm rounded ${getStatusColor(report.generation_status)}`}>
                    {report.generation_status}
                  </span>
                </div>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Generated At</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {new Date(report.generated_at).toLocaleString()}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Generation Time</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {report.generation_time_seconds}s
                </p>
              </div>
            </div>
          </div>

          {/* Input Files Information */}
          {report.input_files_info && report.input_files_info.length > 0 && (
            <div>
              <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
                <FileText className="w-4 h-4 mr-2 text-indigo-600" />
                Input Files
              </h4>
              <div className="space-y-3">
                {report.input_files_info.map((file, index) => (
                  <div key={file.id} className="p-3 bg-gray-50 rounded border">
                    <div className="flex justify-between items-center text-sm">
                      <div className="flex-1 mr-4">
                        <span className="font-medium text-gray-700">File {index + 1}:</span>
                        <span className="text-gray-900 ml-1">{file.original_filename}</span>
                      </div>
                      <div className="text-xs text-gray-600 whitespace-nowrap">
                        {formatFileSize(file.file_size)}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Modal Footer */}
        <div className="flex justify-end p-6 border-t border-gray-200 space-x-3">
          <Button
            variant="outline"
            onClick={onClose}
            className="text-gray-700 border-gray-300 hover:bg-gray-50"
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};
