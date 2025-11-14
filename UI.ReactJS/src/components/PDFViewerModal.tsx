import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/atomic/dialog';
import { Button } from '@/components/atomic/button';
import { Download, X } from 'lucide-react';
import { ReportService } from '@/pages/admin/ReportsManagement/services/ReportService';

interface PDFViewerModalProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  reportName: string;
  reportId: number;
}

export const PDFViewerModal: React.FC<PDFViewerModalProps> = ({
  open,
  onOpenChange,
  reportName,
  reportId
}) => {
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    if (open && reportId) {
      loadPdfContent();
    }

    // Cleanup URL when modal closes
    return () => {
      if (pdfUrl) {
        URL.revokeObjectURL(pdfUrl);
      }
    };
  }, [open, reportId]);

  const loadPdfContent = async () => {
    setLoading(true);
    setError(null);

    try {
      const pdfBlob = await ReportService.getPdfReport(reportId);
      const url = URL.createObjectURL(pdfBlob);
      setPdfUrl(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load PDF');
      console.error('Failed to load PDF:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    if (pdfUrl) {
      const link = document.createElement('a');
      link.href = pdfUrl;
      link.download = `${reportName}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      setSuccess("Download successfully");
    }
  };

  const handleClose = () => {
    if (pdfUrl) {
      URL.revokeObjectURL(pdfUrl);
      setPdfUrl(null);
    }
    setError(null);
    onOpenChange(false);
    setSuccess("");
  };

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="max-w-4xl w-full h-[90vh] p-0 gap-0 overflow-hidden">
        <DialogHeader className="p-6 pb-4 border-b bg-white">
          <div className="flex items-center justify-between mb-4">
            <DialogTitle className="text-xl font-semibold">
              PDF Preview: {reportName}
            </DialogTitle>
            <div className="flex items-center gap-2 pr-3">
              <Button
                variant="outline"
                size="sm"
                onClick={handleDownload}
                disabled={!pdfUrl || loading}
                className="flex items-center gap-2"
              >
                <Download className="w-4 h-4" />
                Download
              </Button>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClose}
                className="flex items-center gap-2"
              >
                <X className="w-4 h-4" />
                Close
              </Button>
            </div>
          </div>
          {/* Success Message */}
          {success && (
            <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
              <p className="text-green-800 text-sm">✅ {success}</p>
            </div>
          )}
        </DialogHeader>

        <div className="flex-1 p-0">
          {loading ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500 mb-4"></div>
                <p className="text-gray-600">Loading PDF...</p>
              </div>
            </div>
          ) : error ? (
            <div className="flex items-center justify-center h-full">
              <div className="text-center">
                <p className="text-red-600 mb-4">Error: {error}</p>
                <Button onClick={loadPdfContent} variant="outline">
                  Retry
                </Button>
              </div>
            </div>
          ) : pdfUrl ? (
            <iframe
              src={pdfUrl}
              className="w-full h-full border-0"
              title={`PDF Preview - ${reportName}`}
              style={{ minHeight: '600px' }}
            >
              <p className="p-6 text-center text-gray-500">
                Your browser doesn't support PDF viewing.
                <Button
                  variant="link"
                  onClick={handleDownload}
                  className="ml-2"
                >
                  Please download the PDF to view it.
                </Button>
              </p>
            </iframe>
          ) : null}
        </div>
      </DialogContent>
    </Dialog>
  );
};
