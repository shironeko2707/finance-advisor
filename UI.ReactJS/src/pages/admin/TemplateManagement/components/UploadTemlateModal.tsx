import React, { useState, useCallback, useRef } from 'react';
import { Upload, X, File, AlertCircle, CheckCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogFooter } from '@/components/atomic/dialog.tsx';
import { Button } from '@/components/atomic/button.tsx';
import { useUploadTemplate } from '../hooks/useUploadTemplate';
import { cn } from '@/components/lib/utils.ts';

interface UploadTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onUploadSuccess: () => void;
}

// This is a simplified version of the FileUploadProgress type for UI purposes
type DisplayFile = {
  id: string;
  file: File;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  progress: number;
};

export const UploadTemlateModal: React.FC<UploadTemplateModalProps> = ({
  isOpen,
  onClose,
  onUploadSuccess
}) => {
  const [file, setFile] = useState<File | null>(null);
  const [displayFiles, setDisplayFiles] = useState<DisplayFile[]>([]);
  const [isDragging, setIsDragOver] = useState(false);
  const [fileSizeError, setFileSizeError] = useState<string | null>(null);
  const [uploadAttempted, setUploadAttempted] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);
  console.log(uploadAttempted);

  const {
    uploading,
    error,
    success,
    uploadTemplate,
    resetUploadState
  } = useUploadTemplate();

  const handleFileChange = useCallback((selectedFile: File | null) => {
    setFile(selectedFile);
    if (selectedFile) {
      setDisplayFiles([{
        id: selectedFile.name,
        file: selectedFile,
        status: 'pending',
        progress: 0
      }]);
    } else {
      setDisplayFiles([]);
    }
    setFileSizeError(null);
    setUploadAttempted(false);
  }, []);

  const removeFile = (id: string) => {
    if (file && file.name === id) {
      handleFileChange(null);
    }
  };

  const handleDragEnter = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
  }, []);

  const handleDragOver = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const validateFile = useCallback((fileToValidate: File) => {
    const MAX_FILE_SIZE_MB = 100;
    const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024;
    const allowedTypes = ['application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'application/vnd.ms-excel', 'application/vnd.ms-excel.sheet.macroEnabled.12', 'application/pdf'];
    const fileName = fileToValidate.name;
    const fileExtension = fileName.split('.').pop()?.toLowerCase();
    const isAllowedType = allowedTypes.includes(fileToValidate.type) || (fileExtension && ['xlsx', 'xls', 'xlsm', 'pdf'].includes(fileExtension));

    if (fileToValidate.size > MAX_FILE_SIZE_BYTES) {
      setFileSizeError(`File "${fileName}" is too large. Maximum size is ${MAX_FILE_SIZE_MB}MB.`);
      return false;
    }
    if (!isAllowedType) {
      setFileSizeError(`File "${fileName}" has an unsupported type. Only .xlsx, .xls, .xlsm, and .pdf files are allowed.`);
      return false;
    }

    setFileSizeError(null);
    return true;
  }, []);

  const handleDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      if (validateFile(droppedFile)) {
        handleFileChange(droppedFile);
      }
    }
  }, [validateFile, handleFileChange]);

  const handleBrowseFilesClick = useCallback(() => {
    fileInputRef.current?.click();
  }, []);

  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const selectedFile = e.target.files[0];
      if (validateFile(selectedFile)) {
        handleFileChange(selectedFile);
      }
    } else {
      handleFileChange(null);
    }
  }, [validateFile, handleFileChange]);

  const handleDone = async () => {
    setDisplayFiles([]);
    if (!file) {
      setFileSizeError('Please select a file to upload.');
      setUploadAttempted(true);
      return;
    }
    if (!validateFile(file)) {
      setUploadAttempted(true);
      return;
    }
    
    setDisplayFiles(prev => prev.map(df => ({ ...df, status: 'uploading', progress: 50 })));
    await uploadTemplate({ file, name: file.name, category: '0', version: '1.0' });
    setUploadAttempted(true);
  };

  React.useEffect(() => {
    if (success) {
      onUploadSuccess();
    }
  }, [success, onUploadSuccess]);
  
  React.useEffect(() => {
    if (error) {
      setDisplayFiles(prev => prev.map(df => ({ ...df, status: 'error', progress: 0 })));
    }
  }, [error]);

  const handleModalClose = useCallback(() => {
    resetUploadState();
    handleFileChange(null);
    setIsDragOver(false);
    setUploadAttempted(false);
    onClose();
    setDisplayFiles([]);
  }, [resetUploadState, onClose, handleFileChange]);

  const getStatusColor = (status: DisplayFile['status']) => {
    switch (status) {
      case 'pending': return 'bg-gray-200';
      case 'uploading': return 'bg-blue-500';
      case 'completed': return 'bg-green-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-200';
    }
  };

  const getStatusIcon = (status: DisplayFile['status']) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-600" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-600" />;
      default: return null;
    }
  };

  if (!isOpen) {
    return null;
  }

  return (
    <Dialog open={isOpen} onOpenChange={handleModalClose}>
      <DialogContent className="sm:max-w-[600px] bg-white !bg-opacity-100">
        <DialogHeader>
          <DialogTitle>File(s) Upload</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-gray-600 mb-4">Add your documents here</p>

        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors mb-4 ${isDragging ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'}`}
          onDragEnter={handleDragEnter}
          onDragLeave={handleDragLeave}
          onDragOver={handleDragOver}
          onDrop={handleDrop}
        >
          <Upload className="mx-auto h-12 w-12 text-blue-500 mb-4" />
          <p className="text-gray-600 mb-2">Drag your file(s) to start uploading</p>
          <p className="text-gray-500 text-sm mb-4">OR</p>
          <input
            ref={fileInputRef}
            type="file"
            id="browse-files"
            onChange={handleFileInputChange}
            className="hidden"
          />
          <Button
            variant="outline"
            onClick={handleBrowseFilesClick}
            disabled={uploading}
            className="border-blue-600 text-blue-600 hover:bg-blue-50"
          >
            Browse Templates
          </Button>
        </div>

        {/* File List */}
        {displayFiles.length > 0 && (
          <div className="space-y-2 max-h-64 overflow-y-auto">
            {displayFiles.map((displayFile) => (
              <div
                key={displayFile.id}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center flex-1 min-w-0">
                  <File className="h-4 w-4 text-gray-400 mr-2 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <p className="text-sm font-medium text-gray-900 truncate">
                        {displayFile.file.name}
                      </p>
                      {getStatusIcon(displayFile.status)}
                    </div>
                    <p className="text-xs text-gray-500">
                      {(displayFile.file.size / 1024).toFixed(1)} KB
                    </p>
                    
                    {/* Progress bar */}
                    {(uploading || success) && displayFile.status === 'uploading' && (
                      <div className="mt-2">
                        <div className="bg-gray-200 rounded-full h-2">
                          <div
                            className={cn("h-2 rounded-full transition-all", getStatusColor(displayFile.status))}
                            style={{ width: `${displayFile.progress}%` }}
                          />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          {displayFile.progress}% progress
                        </p>
                      </div>
                    )}
                    
                    {displayFile.status === 'completed' && (
                      <p className="text-xs text-green-600 mt-1">Upload completed</p>
                    )}
                    
                    {displayFile.status === 'error' && (
                      <p className="text-xs text-red-600 mt-1 flex items-center">
                        <AlertCircle className="h-3 w-3 mr-1" />
                        Upload failed: {error}
                      </p>
                    )}
                  </div>
                </div>

                {displayFile.status === 'pending' && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => removeFile(displayFile.id)}
                    className="ml-2"
                  >
                    <X className="h-4 w-4" />
                  </Button>
                )}
              </div>
            ))}
          </div>
        )}

        <p className="text-xs text-gray-500 mb-4">
          Only support .xlsx, .xls, .xlsm files
        </p>

        {fileSizeError && (
          <div className="p-3 bg-red-100 border border-red-200 rounded-md mb-4 flex items-center">
            <AlertCircle className="h-4 w-4 text-red-600 mr-2" />
            <p className="text-sm text-red-700">{fileSizeError}</p>
          </div>
        )}

        <DialogFooter className="pt-4 border-t border-gray-200 mt-4">
          <Button variant="outline" onClick={handleModalClose} disabled={uploading}>
            Cancel
          </Button>
          <Button
            onClick={handleDone}
            disabled={uploading || !file || !!fileSizeError}
            className={`text-white ${uploading ? 'bg-gray-400' : (fileSizeError ? 'bg-red-400' : 'bg-orange-500 hover:bg-orange-600')}`}
          >
            {uploading ? 'Uploading...' : 'Done'}
          </Button>
        </DialogFooter>
        {error && !fileSizeError && <p className="text-red-600 text-sm mt-4">Error: {error}</p>}
      </DialogContent>
    </Dialog>
  );
};