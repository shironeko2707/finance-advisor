import React, { useState, useCallback, useRef } from 'react';
import { Upload, X, File, AlertCircle, CheckCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/atomic/dialog.tsx';
import { Button } from '@/components/atomic/button.tsx';
import { useFileUpload } from '@/pages/admin/FilesManagement/hooks/useFileUpload.ts';
import { shouldUseFixture } from '@/config/config.ts';
import type { FileUploadProgress } from '@/types/file.ts';
import { cn } from '@/components/lib/utils.ts';

// Local development flag - can override global config
const USE_FIXTURE = shouldUseFixture('USE_FIXTURE', false);

interface FileUploadModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadComplete: () => void;
}

export const FileUploadModal: React.FC<FileUploadModalProps> = ({
  isOpen,
  onClose,
  onUploadComplete
}) => {
  const {
    uploadFiles,
    isUploading,
    uploadResponse,
    canUpload,
    allCompleted,
    hasErrors,
    addFiles,
    removeFile,
    clearFiles,
    performUpload
  } = useFileUpload({ useFixture: USE_FIXTURE });

  const [isDragOver, setIsDragOver] = useState(false);
  const [fileSizeErrors, setFileSizeErrors] = useState<string[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const validateAndAddFiles = useCallback((files: File[]) => {
    const MAX_FILE_SIZE = 100 * 1024 * 1024; // 100MB in bytes
    const errors: string[] = [];

    // Check for file size violations
    const oversizedFiles = files.filter(file => file.size > MAX_FILE_SIZE);
    oversizedFiles.forEach(file => {
      errors.push(`File "${file.name}" is too large (${(file.size / (1024 * 1024)).toFixed(1)}MB). Only .pdf, .xlsx files up to 100MB are supported.`);
    });

    // Update error state
    setFileSizeErrors(errors);

    // Only add files that pass validation (both size and type will be checked in hook)
    const validSizeFiles = files.filter(file => file.size <= MAX_FILE_SIZE);
    if (validSizeFiles.length > 0) {
      addFiles(validSizeFiles);
      // Clear errors when valid files are successfully added
      if (errors.length === 0) {
        setFileSizeErrors([]);
      }
    }
  }, [addFiles]);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    const files = Array.from(e.dataTransfer.files);
    validateAndAddFiles(files);
  }, [validateAndAddFiles]);

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    validateAndAddFiles(files);
  };

  const handleUpload = async () => {
    try {
      await performUpload();

      // Wait a moment to show completion, then close
      setTimeout(() => {
        onUploadComplete();
        handleClose();
      }, 2000);
    } catch (error) {
      console.error('Upload failed:', error);
    }
  };

  const handleClose = () => {
    clearFiles();
    setFileSizeErrors([]); // Clear file size errors when closing
    setIsDragOver(false);
    onClose();
  };

  const getStatusColor = (status: FileUploadProgress['status']) => {
    switch (status) {
      case 'pending': return 'bg-gray-200';
      case 'uploading': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-200';
    }
  };

  const getStatusIcon = (status: FileUploadProgress['status']) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-600" />;
      default: return null;
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={handleClose}>
      <DialogContent className="max-w-2xl bg-white !bg-opacity-100">
        <DialogHeader>
          <DialogTitle>File(s) Upload</DialogTitle>
        </DialogHeader>

        <div className="space-y-4">
          <p className="text-sm text-gray-600">
            Add your documents here. Supported formats: PDF, Excel (.xlsx, .xls, .xlsm). Maximum file size: 100MB.
            {USE_FIXTURE && (
              <span className="ml-2 px-2 py-1 bg-yellow-100 text-yellow-800 text-xs rounded">
                MOCK MODE
              </span>
            )}
          </p>

          {/* File Size Errors */}
          {fileSizeErrors.length > 0 && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <div className="flex items-center mb-2">
                <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
                <h4 className="font-medium text-sm text-red-800">File Size Errors</h4>
              </div>
              <ul className="text-sm text-red-700 space-y-1">
                {fileSizeErrors.map((error, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-red-600 mr-2">•</span>
                    {error}
                  </li>
                ))}
              </ul>
              <Button
                variant="outline"
                size="sm"
                onClick={() => setFileSizeErrors([])}
                className="mt-3 text-red-600 border-red-300 hover:bg-red-50"
              >
                Dismiss
              </Button>
            </div>
          )}

          {/* Upload Results Summary */}
          {uploadResponse && (
            <div className={cn(
              "p-4 rounded-lg border",
              uploadResponse.overall_status === 'success' ? "bg-green-50 border-green-200" :
              uploadResponse.overall_status === 'failed' ? "bg-red-50 border-red-200" :
              "bg-yellow-50 border-yellow-200"
            )}>
              <h4 className="font-medium text-sm mb-2">Upload Results</h4>
              <div className="text-sm space-y-1">
                <p>Total files: {uploadResponse.total_files}</p>
                <p className="text-green-600">Successful: {uploadResponse.successful_uploads}</p>
                {uploadResponse.failed_uploads > 0 && (
                  <p className="text-red-600">Failed: {uploadResponse.failed_uploads}</p>
                )}
              </div>
            </div>
          )}

          {/* Drop Zone */}
          <div
            className={cn(
              "border-2 border-dashed rounded-lg p-8 text-center transition-colors",
              isDragOver ? "border-blue-500 bg-blue-50" : "border-gray-300",
              "hover:border-blue-400 hover:bg-gray-50"
            )}
            onDragEnter={handleDragEnter}
            onDragLeave={handleDragLeave}
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <Upload className="mx-auto h-12 w-12 text-blue-500 mb-4" />
            <p className="text-gray-600 mb-2">
              Drag your file(s) to start uploading
            </p>
            <p className="text-gray-500 text-sm mb-4">OR</p>
            <Button 
              variant="outline" 
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="border-blue-600 text-blue-600 hover:bg-blue-50"
            >
              Browse files
            </Button>
          </div>

          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".xlsx,.xls,.xlsm,.pdf"
            onChange={handleFileInputChange}
            className="hidden"
          />

          <p className="text-xs text-gray-500">
            Only support .xlsx, .xls, .xlsm, .pdf files
          </p>

          {/* File List */}
          {uploadFiles.length > 0 && (
            <div className="space-y-2 max-h-64 overflow-y-auto">
              {uploadFiles.map((uploadFile) => (
                <div
                  key={uploadFile.id}
                  className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                >
                  <div className="flex items-center flex-1 min-w-0">
                    <File className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {uploadFile.file.name}
                        </p>
                        {getStatusIcon(uploadFile.status)}
                      </div>
                      <p className="text-xs text-gray-500">
                        {(uploadFile.file.size / 1024).toFixed(1)} KB
                      </p>
                      
                      {/* Progress bar */}
                      {uploadFile.status === 'uploading' && (
                        <div className="mt-2">
                          <div className="bg-gray-200 rounded-full h-2">
                            <div
                              className={cn("h-2 rounded-full transition-all", getStatusColor(uploadFile.status))}
                              style={{ width: `${uploadFile.progress}%` }}
                            />
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            {uploadFile.progress}% progress
                          </p>
                        </div>
                      )}
                      
                      {uploadFile.status === 'completed' && (
                        <p className="text-xs text-green-600 mt-1">Upload completed</p>
                      )}
                      
                      {uploadFile.status === 'error' && (
                        <p className="text-xs text-red-600 mt-1 flex items-center">
                          <AlertCircle className="h-3 w-3 mr-1" />
                          Upload failed
                        </p>
                      )}
                    </div>
                  </div>

                  {uploadFile.status === 'pending' && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(uploadFile.id)}
                      className="ml-2"
                    >
                      <X className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose} disabled={isUploading}>
            {allCompleted ? 'Close' : 'Cancel'}
          </Button>
          <Button 
            onClick={handleUpload} 
            disabled={!canUpload}
            className={cn(
              "text-white",
              hasErrors ? "bg-red-500 hover:bg-red-600" :
              allCompleted ? "bg-green-500 hover:bg-green-600" :
              "bg-orange-500 hover:bg-orange-600"
            )}
          >
            {isUploading ? 'Uploading...' :
             allCompleted ? 'Complete' :
             hasErrors ? 'Retry' : 'Upload'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
};
