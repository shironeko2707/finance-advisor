import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/atomic/button.tsx';
import {Eye, FileSpreadsheet, FileText, Trash2, MoreHorizontal, Plus} from 'lucide-react';
import { useReportList } from './hooks/useReportList.ts';
import { useReportListUI } from './hooks/useReportListUI.ts';
import { shouldUseFixture } from '@/config/config.ts';
import { PDFViewerModal } from '@/components/PDFViewerModal.tsx';
import { Office365PreviewModal } from '@/components/Office365PreviewModal.tsx';
import { ReportsSearchFilters } from './components/ReportsSearchFilters.tsx';
import { ReportDetailModal } from './components/ReportDetailModal.tsx';
import { convertTimestamp } from '@/utils/common.ts';

// Local development flag - can override global config
const USE_FIXTURE = shouldUseFixture('REPORTS_MANAGEMENT_USE_FIXTURE', false);

export const ReportsList: React.FC = () => {
  const navigate = useNavigate();

  // Business logic hook
  const {
    reports,
    loading,
    error,
    success,
    availableUsers,
    currentPage,
    totalPages,
    pageSize,
    totalReports,
    filters,
    updateFilters,
    clearFilters,
    availableTemplates,
    // availableCreators, // Commented out as it's not used in the UI
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    deleteReport,
    downloadReport,
    refreshReports
  } = useReportList({ useFixture: USE_FIXTURE });

  // UI logic hook
  const {
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
  } = useReportListUI();

  if (loading && reports.length === 0) {
    return (
      <div className="p-6 text-center">
        <div className="text-lg">Loading reports...</div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Breadcrumb */}
      <div className="mb-6">
        <div className="flex items-center text-sm text-gray-600 mb-4">
          <span>Analyst Tools</span>
          <span className="mx-2">/</span>
          <span>Generated Reports</span>
        </div>
        <div className='flex justify-between'>
          <h2 className="text-lg font-medium text-gray-900">Generated Reports List</h2>
          {/* Action Buttons */}
          <div>
            <Button
              onClick={() => navigate('/reports/new')}
              className="bg-orange-500 hover:bg-orange-600 text-white"
              disabled={loading}
            >
              <Plus className="w-4 h-4 mr-1" />
              Create new report
            </Button>
          </div>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">⚠ {error}</p>
          <Button
            onClick={() => refreshReports()}
            variant="outline"
            className="mt-2 text-red-600 border-red-600 hover:bg-red-50"
            size="sm"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm">✅ {success}</p>
        </div>
      )}

      {/* Search Filters */}
      <ReportsSearchFilters
        availableUsers={availableUsers}
        filters={filters}
        availableTemplates={availableTemplates}
        loading={loading}
        onFiltersChange={(field: string, value: string) => updateFilters({ [field]: value })}
        onRefreshReports={refreshReports}
        onClearFilters={clearFilters}
      />

      {/* Reports Table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm mt-2">Loading reports...</p>
        </div>
      ) : reports.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-red-500 text-sm">No data found</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg">
          <table className="w-full table-fixed">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[5%]">
                  #
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider flex-grow w-[20%] overflow-hidden text-ellipsis">
                  Report name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider flex-grow w-[20%] overflow-hidden text-ellipsis">
                  Template
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[15%]">
                  Create date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[15%]">
                  Creator
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider w-[10%]">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {reports.map((report, index) => (
                <tr key={report.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 text-sm text-gray-900">
                    {(currentPage - 1) * pageSize + index + 1}
                  </td>
                  <td
                    className="px-5 py-3 text-sm text-gray-900 cursor-pointer hover:text-blue-600 flex-grow max-w-[450px] whitespace-nowrap"
                    onClick={() => handleViewReport(report.id, reports)}
                  >
                    {report.report_name.toString().length > 30
                      ? `${report.report_name.substring(0, 30)}...`
                      : report.report_name}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-900 flex-grow max-w-[450px] whitespace-nowrap" title={report.template_filename}>
                    {report.template_filename.toString().length > 30
                      ? `${report.template_filename.substring(0, 30)}...`
                      : report.template_filename}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-900">
                    {convertTimestamp(report.generated_at, true)}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-900">
                    {report.user_name}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500 relative">
                    <button
                      onClick={() => toggleActionMenu(report.id)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title="More options"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>

                    {/* Action Dropdown Menu */}
                    {openActionMenu === report.id && (
                      <div className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-32">

                        {/* View Info */}
                        <button
                          onClick={() => {
                            handleViewReport(report.id, reports);
                            setOpenActionMenu(null);
                          }}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Eye className="w-4 h-4 mr-2 text-blue-600" />
                          View Info
                        </button>

                        {/* View Excel */}
                        <button
                          onClick={() => {
                            console.log('Excel view clicked for report:', report.id);
                            handlePreviewExcel(report.id, reports);
                          }}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <FileText className="w-4 h-4 mr-2 text-red-600" />
                          View
                        </button>

                        {/* Download Excel */}
                        <button
                          onClick={() => {
                            handleDownloadReport(report.id, 'excel', reports, downloadReport);
                          }}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <FileSpreadsheet className="w-4 h-4 mr-2 text-green-600" />
                          Download Excel
                        </button>

                        {/* View PDF */}
                        <button
                          onClick={() => {
                            handleViewPdf(report.id, reports);
                            setOpenActionMenu(null);
                          }}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <FileText className="w-4 h-4 mr-2 text-red-600" />
                          View PDF
                        </button>

                        {/* Delete */}
                        <button
                          onClick={() => {
                            handleDeleteReport(report.id, deleteReport);
                          }}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Trash2 className="w-4 h-4 mr-2 text-red-600" />
                          Delete
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="bg-white px-6 py-3 border-t border-gray-200 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-700">Rows per page:</span>
              <select
                className="border border-gray-300 rounded px-2 py-1 text-sm"
                value={pageSize}
                onChange={(e) => changePageSize(parseInt(e.target.value))}
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
              <span className="text-sm text-gray-700">of {totalReports} rows</span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                className={`p-1 ${currentPage === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-400 hover:text-gray-600 cursor-pointer'}`}
                onClick={goToPrevPage}
                disabled={currentPage === 1}
                title="Previous page"
              >
                ‹
              </button>

              {generatePageNumbers(currentPage, totalPages).map(pageNum => (
                <button
                  key={pageNum}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${pageNum === currentPage
                    ? 'bg-blue-600 text-white'
                    : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                    }`}
                  onClick={() => goToPage(pageNum)}
                >
                  {pageNum}
                </button>
              ))}

              <button
                className={`p-1 ${currentPage === totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-400 hover:text-gray-600 cursor-pointer'}`}
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
                title="Next page"
              >
                ›
              </button>
            </div>
          </div>
        </div>
      )}

      {/* PDF Viewer Modal */}
      <PDFViewerModal
        open={pdfViewerState.isOpen}
        onOpenChange={(open) => setPdfViewerState({ ...pdfViewerState, isOpen: open })}
        reportName={pdfViewerState.reportName}
        reportId={pdfViewerState.reportId}
      />

      {/* Excel Preview Modal */}
      <Office365PreviewModal
        isOpen={excelPreviewState.isOpen}
        onClose={() => setExcelPreviewState({ ...excelPreviewState, isOpen: false })}
        fileName={excelPreviewState.fileName}
        fileUrl={excelPreviewState.fileUrl}
        fileType={excelPreviewState.fileType}
      />

      {/* Report Detail Modal */}
      <ReportDetailModal
        isOpen={reportMetadataModal.isOpen}
        report={reportMetadataModal.report}
        onClose={() => setReportMetadataModal({ isOpen: false, report: null })}
      />
    </div>
  );
};
