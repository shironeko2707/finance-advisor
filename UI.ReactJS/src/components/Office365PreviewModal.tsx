import React from 'react';
import { X } from 'lucide-react';
import { Button } from '@/components/atomic/button';

interface Office365PreviewModalProps {
  isOpen: boolean;
  onClose: () => void;
  fileName: string;
  fileUrl: string;
  fileType: string;
}

export const Office365PreviewModal: React.FC<Office365PreviewModalProps> = ({
  isOpen,
  onClose,
  fileName,
  fileUrl,
  fileType
}) => {
  if (!isOpen) return null;

  // Office 365 Online Viewer URL
  const getOffice365ViewerUrl = (fileUrl: string, fileType: string): string => {
    // Office 365 Online supports different file types
    const supportedTypes = ['pdf', 'docx', 'doc', 'xlsx', 'xls', 'pptx', 'ppt', 'excel', 'word', 'powerpoint'];

    if (!supportedTypes.includes(fileType.toLowerCase())) {
      return '';
    }

    // For Office 365 Online Viewer, we need to encode the file URL
    // Since we're using local server URLs, we'll use a different approach
    // Instead of using Office 365 viewer, we'll embed the file directly for supported types
    if (fileType.toLowerCase() === 'pdf') {
      // For PDF, embed directly with authentication headers
      return fileUrl + '#toolbar=0&navpanes=0&scrollbar=0';
    } else {
      // For Office documents, use Office 365 Online Viewer
      const encodedFileUrl = encodeURIComponent(fileUrl);
      return `https://view.officeapps.live.com/op/embed.aspx?src=${encodedFileUrl}`;
    }
  };

  const viewerUrl = getOffice365ViewerUrl(fileUrl, fileType);

  const isSupported = viewerUrl !== '';

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div
          className="fixed inset-0 transition-opacity bg-gray-500 bg-opacity-75"
          onClick={onClose}
        />

        {/* Modal */}
        <div className="inline-block w-full max-w-6xl p-6 my-8 overflow-hidden text-left align-middle transition-all transform bg-white shadow-xl rounded-lg">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-lg font-medium text-gray-900">File Preview</h3>
              <p className="text-sm text-gray-600 mt-1">{fileName}</p>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={onClose}
              className="p-2"
            >
              <X className="w-4 h-4" />
            </Button>
          </div>

          {/* Content */}
          <div className="space-y-4">
            {!isSupported ? (
              <div className="text-center py-12">
                <div className="text-gray-500 mb-4">
                  <svg className="w-16 h-16 mx-auto mb-4" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
                  </svg>
                </div>
                <h4 className="text-lg font-medium text-gray-900 mb-2">Preview Not Available</h4>
                <p className="text-gray-600 mb-4">
                  File type ".{fileType}" is not supported for preview.
                </p>
                <p className="text-sm text-gray-500">
                  Supported formats: PDF, Word (DOC, DOCX), Excel (XLS, XLSX), PowerPoint (PPT, PPTX)
                </p>
              </div>
            ) : (
              <div className="relative bg-gray-100 rounded-lg overflow-hidden" style={{ height: '600px' }}>
                <iframe
                  src={viewerUrl}
                  width="100%"
                  height="100%"
                  style={{ border: 0 }}
                  className="rounded-lg"
                  title={`Preview of ${fileName}`}
                  onError={(e) => {
                    console.error('Error loading Office 365 preview:', e);
                  }}
                >
                  <div className="flex items-center justify-center h-full">
                    <p className="text-gray-600">
                      Your browser doesn't support iframes. Please download the file to view it.
                    </p>
                  </div>
                </iframe>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="flex justify-end mt-6 pt-4 border-t border-gray-200">
            <Button
              onClick={onClose}
              variant="outline"
            >
              Close
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};
