import React from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { X, Download, Eye, Calendar, User, HardDrive, AlertCircle, Clock } from 'lucide-react';
import type { UploadedFile } from '@/types/file';

interface FileDetailModalProps {
  isOpen: boolean;
  file: UploadedFile | null;
  onClose: () => void;
  onDownload?: (file: UploadedFile) => Promise<void>;
}

export const FileDetailModal: React.FC<FileDetailModalProps> = ({
  isOpen,
  file,
  onClose,
  onDownload
}) => {
  if (!isOpen || !file) return null;

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    const date = new Date(dateString);
    return date.toLocaleString('en-GB', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    }).replace(',', '');
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">File Details</h3>
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
              <Eye className="w-4 h-4 mr-2 text-blue-600" />
              Basic Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">File Name</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border break-words">
                  {file.original_filename}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">File Type</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    file.file_type === 'pdf' 
                      ? 'bg-red-100 text-red-800' 
                      : 'bg-green-100 text-green-800'
                  }`}>
                    {file.file_type.toUpperCase()}
                  </span>
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">File Size</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {formatFileSize(file.file_size)}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">MIME Type</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {file.mimetype}
                </p>
              </div>
            </div>
          </div>

          {/* Upload Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Calendar className="w-4 h-4 mr-2 text-green-600" />
              Upload Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700 flex items-center">
                  <Clock className="w-3 h-3 mr-1" />
                  Upload Time
                </Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {formatDate(file.uploaded_at)}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700 flex items-center">
                  <User className="w-3 h-3 mr-1" />
                  Uploaded By
                </Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  User {file.uploaded_by}
                </p>
              </div>
            </div>
          </div>

          {/* Storage Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <HardDrive className="w-4 h-4 mr-2 text-purple-600" />
              Storage Information
            </h4>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Stored Filename</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border font-mono break-words">
                  {file.stored_filename}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">File Path</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border font-mono break-words">
                  {file.file_path}
                </p>
              </div>
            </div>
          </div>

          {/* Status Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <AlertCircle className="w-4 h-4 mr-2 text-orange-600" />
              File Status
            </h4>
            <div className="grid grid-cols-1 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Status</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${
                    file.status === 'success' 
                      ? 'bg-green-100 text-green-800' 
                      : file.status === 'error'
                      ? 'bg-red-100 text-red-800'
                      : 'bg-yellow-100 text-yellow-800'
                  }`}>
                    {file.status.charAt(0).toUpperCase() + file.status.slice(1)}
                  </span>
                </p>
              </div>
              {file.error_message && (
                <div>
                  <Label className="text-sm font-medium text-gray-700">Error Message</Label>
                  <p className="text-sm text-red-600 mt-1 p-3 bg-red-50 rounded border">
                    {file.error_message}
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
          {onDownload && (
            <Button
              onClick={async () => {
                await onDownload(file);
                onClose();
              }}
              className="bg-orange-500 hover:bg-orange-600 text-white"
            >
              <Download className="w-4 h-4 mr-2" />
              Download
            </Button>
          )}
          <Button
            onClick={onClose}
            variant="outline"
          >
            Close
          </Button>
        </div>
      </div>
    </div>
  );
};
