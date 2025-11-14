import React, { useEffect, useState } from 'react';
import { ArrowLeft, Upload, X } from 'lucide-react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Card, CardContent } from '@/components/atomic/card.tsx';
import { Office365PreviewModal } from '@/components/Office365PreviewModal';
import { useReportCreate } from './hooks/useReportCreate';
import { apiService } from '@/services/ApiInterceptor';
import type { Template } from '../TemplateManagement/types';
import { SearchableSelect } from '@/components/atomic/searchable-select';
import { SelectItem } from '@/components/atomic/select';
import { FileService } from '../FilesManagement/services';
import type { UploadedFile } from '@/types/file';

export const CreateReport: React.FC = () => {
  const {
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
  } = useReportCreate();

  const [templates, setTemplates] = useState<Template[]>([]);
  const [files, setFiles] = useState<UploadedFile[]>([]);
  const [fileSellected, setFileSellected] = useState<{
    id: number;
    fileName: string;
  }[]>([]);

  const MAX_FILE_SELECTION_LIMIT = 3;
  const [fileSelectionError, setFileSelectionError] = useState<string | null>(null);

  const [optionSellected, setOptionSellected] = useState<{
    templateId: number | undefined;
    file_ids: number[];
  } | undefined>({
    templateId: undefined,
    file_ids: []
  });

  const handleSearchChange = (typeChange: "template" | "files", e: string) => {
    if (typeChange === "template") {
      setOptionSellected(pre => ({
        ...pre,
        templateId: Number(e),
        file_ids: pre?.file_ids || []
      }))
      return;
    } else if (typeChange === "files") {
      setOptionSellected(pre => {
        const newFileIds = pre?.file_ids ? [...pre.file_ids] : [];
        const fileId = Number(e);

        if (newFileIds.includes(fileId)) {
          setFileSelectionError("This file is already selected.");
          return {
            templateId: pre?.templateId,
            file_ids: newFileIds
          };
        }

        if (newFileIds.length >= MAX_FILE_SELECTION_LIMIT) {
          setFileSelectionError(`You can select a maximum of ${MAX_FILE_SELECTION_LIMIT} files.`);
          return {
            templateId: pre?.templateId,
            file_ids: newFileIds
          };
        }

        newFileIds.push(fileId);
        setFileSelectionError(null);
        return {
          templateId: pre?.templateId,
          file_ids: newFileIds
        };
      });
    }
  };
  useEffect(() => {
    const fetchTemplates = async () => {
      try {
        const res = await apiService.api.getTemplates();
        setTemplates(res.templates ?? [])
      } catch (e) {
        console.log(e);
      }
    }
    const fetchFiles = async () => {
      try {
        const resFiles = await FileService.getFiles();
        setFiles(resFiles.files ?? []);
      } catch (e) {
        console.log(e);
      }
    }

    fetchTemplates();
    fetchFiles();
  }, []);
  useEffect(() => {
    const res: {
      id: number;
      fileName: string;
    }[] = [];

    optionSellected?.file_ids.forEach(id => {
      const foundFile = files.find(file => Number(file.id) === id);
      if (foundFile) {
        res.push({
          id: foundFile.id,
          fileName: foundFile.original_filename
        });
      }
    });
    setFileSellected(res);
  }, [optionSellected?.file_ids, optionSellected?.templateId, files]);

  useEffect(() => {
    setFormData(prev => ({
      ...prev,
      template_id: optionSellected?.templateId?.toString() || '',
      file_ids: optionSellected?.file_ids || []
    }));
  }, [optionSellected?.templateId, optionSellected?.file_ids, setFormData]);

  return (
    <div className="p-6 max-w-4xl mx-auto">
      {/* Breadcrumb */}
      <div className="mb-6">
        <div className="flex items-center text-sm text-gray-600 mb-4">
          <span>Analyst Tools</span>
          <span className="mx-2">/</span>
          <span>Reports management</span>
        </div>

        <div className="flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-gray-900">Create new report</h1>
        </div>
      </div>

      {/* Report Name */}
      <div className='w-1/2 mb-5'>
        <Label htmlFor="reportName" className="text-base font-medium text-gray-900 mb-3 block">
          Report name *
        </Label>
        <Input
          id="reportName"
          value={formData.report_name}
          onChange={createValidatedFieldOnChange('report_name', setFormData)}
          placeholder="Enter report name"
          className="h-10"
        />
      </div>
      {/* Main Content Card */}
      <Card className="shadow-sm mb-5">
        <CardContent className="px-8 py-5">
          <div className="space-y-5">
            {/* Sellect Template ID */}
            <div className='flex justify-between gap-8'>
              <div className='w-1/2'>
                <Label className="text-base font-medium text-gray-900 mb-3 block">
                  Select output template:
                </Label>
                <SearchableSelect
                  value={optionSellected?.templateId?.toString() || ''}
                  onValueChange={(value) => handleSearchChange("template", value)}
                  placeholder="Type to search..."
                  disabled={!!templateFile}
                >
                  {templates.map(item => (
                    <SelectItem key={item.id} value={(item.id).toString() || ""}>
                      {item.name}
                    </SelectItem>
                  ))}
                </SearchableSelect>
              </div>
            </div>

            {/* Template Upload */}
            <div>
              <Label className="mt-4 text-base font-medium text-gray-900 mb-3 block">
                Template Upload:
              </Label>
              <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center bg-gray-50 hover:bg-gray-100 transition-colors">
                <div className="flex flex-col items-center">
                  <Upload className="w-10 h-10 text-blue-600 mb-3" />
                  <p className="text-base text-gray-700 mb-2">Drop your template file or start uploading</p>
                  <label htmlFor="templateUpload" className="cursor-pointer">
                    <Button
                      variant="outline"
                      className="border-blue-600 text-blue-600 hover:bg-blue-50"
                      asChild
                    >
                      <span>Browse template</span>
                    </Button>
                    <input
                      id="templateUpload"
                      type="file"
                      multiple
                      className="hidden"
                      accept=".xlsx,.xls,.xlsm"
                      onChange={handleTemplateUpload}
                    />
                  </label>
                </div>
              </div>

              {/* Uploaded Template Display */}
              {templateFile && (
                <div className="mt-4">
                  <Label className="text-sm font-medium text-gray-700 mb-2 block">Template file:</Label>
                  <div className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                        <svg className="w-5 h-5 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zM6.293 6.707a1 1 0 010-1.414l3-3a1 1 0 011.414 0l3 3a1 1 0 01-1.414 1.414L11 5.414V13a1 1 0 11-2 0V5.414L7.707 6.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{templateFile.file.name}</p>
                        <p className="text-sm text-gray-500">{formatFileSize(templateFile.file.size)}</p>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      {/* <Button
                        variant="outline"
                        size="sm"
                        className="bg-orange-500 text-white border-orange-500 hover:bg-orange-600"
                      >
                        Preview
                      </Button> */}
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={removeTemplateFile}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
      <Card className='shadow-sm mb-5'>
        <CardContent className='px-8 py-5'>
          {/* Input Files */}
          <div>
            <div className='space-y-3 w-1/2'>
              <Label className="text-base font-medium text-gray-900 mb-3 block">
                Input files:
              </Label>
              <SearchableSelect
                value=''
                onValueChange={(value) => handleSearchChange("files", value)}
                placeholder="Type to search..."
                // disabled={inputFiles.length > 0}
              >
                {files.map(item => (
                  <SelectItem key={item.id} value={(item.id).toString() || ""}>
                    {item.original_filename}
                  </SelectItem>
                ))}
              </SearchableSelect>
            </div>
            {fileSelectionError && (
              <p className="text-red-500 text-sm mt-2">{fileSelectionError}</p>
            )}
            {/* Uploaded Files List */}
            {fileSellected.length > 0 && (
              <div className="mt-6 space-y-3">
                <Label className="text-sm font-medium text-gray-700">Files:</Label>
                {fileSellected.map((inputFile) => (
                  <div
                    key={inputFile.id}
                    className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                        <svg className={`w-5 h-5 ${inputFiles.length > 0 ? "text-green-300" : "text-green-600"} `} fill="currentColor" viewBox="0 0 20 20">
                          <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586a1 1 0 01.707.293l3.414 3.414a1 1 0 01.293.707V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4z" clipRule="evenodd" />
                        </svg>
                      </div>
                      <div>
                        <p className={`font-medium ${inputFiles.length > 0 ? "text-gray-500" : "text-gray-900" }`}>{inputFile.fileName}</p>
                        {/* <p className="text-sm text-gray-500">{formatFileSize(inputFile.file.size)}</p> */}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <Button
                        disabled={inputFiles.length > 0}
                        variant="ghost"
                        size="sm"
                        onClick={() => {
                          setOptionSellected(pre => {
                            const updatedFileIds = pre?.file_ids.filter(id => {
                              return id !== Number(inputFile.id);
                            }) || [];
                            return {
                              templateId: pre?.templateId,
                              file_ids: updatedFileIds
                            };
                          });
                          setFileSelectionError(null); // Clear error on file removal
                        }}
                        className="text-red-500 hover:text-red-700 hover:bg-red-50"
                      >
                        <X className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <Label className="text-base font-medium text-gray-900 mt-4 mb-3 block">
            File(s) upload
          </Label>
          <div className="border-2 border-dashed border-gray-300 rounded-lg p-8 text-center bg-gray-50 hover:bg-gray-100 transition-colors">
            <div className="flex flex-col items-center">
              <Upload className="w-10 h-10 text-blue-600 mb-4" />
              <p className="text-base text-gray-700 mb-2">Drop your file(s) or start uploading</p>
              <label htmlFor="fileUpload" className="cursor-pointer">
                <Button
                  variant="outline"
                  className="border-blue-600 text-blue-600 hover:bg-blue-50"
                  asChild
                >
                  <span>Browse files</span>
                </Button>
                <input
                  id="fileUpload"
                  type="file"
                  multiple
                  className="hidden"
                  accept=".xlsx,.xls,.csv,.pdf"
                  onChange={handleFileUpload}
                />
              </label>
            </div>
          </div>

          {/* Uploaded Files List */}
          {inputFiles.length > 0 && (
            <div className="mt-6 space-y-3">
              {inputFiles.map((inputFile) => (
                <div
                  key={inputFile.id}
                  className="flex items-center justify-between p-4 bg-white border border-gray-200 rounded-lg"
                >
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                      <svg className="w-5 h-5 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                      </svg>
                    </div>
                    <div>
                      <p className="font-medium text-gray-900">{inputFile.file.name}</p>
                      <p className="text-sm text-gray-500">{formatFileSize(inputFile.file.size)}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                      <span className="text-sm text-gray-600">
                        {inputFile.status === 'uploaded' ? 'Ready' : inputFile.status}
                      </span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => removeFile(inputFile.id)}
                      className="text-red-500 hover:text-red-700 hover:bg-red-50"
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex items-center justify-between pt-5">
        {/* Progress Indicator */}
        {loading && uploadProgress && (
          <div className="flex items-center text-sm text-blue-600">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
            {uploadProgress}
          </div>
        )}
        {!loading && (
          <div></div>
        )}

        <div className="flex gap-3">
          <Button
            variant="outline"
            onClick={navigateToReports}
            disabled={loading}
            className="px-8"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>

          <Button
            variant="outline"
            className="px-8"
            onClick={navigateToReports}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            onClick={handleCreateReport}
            disabled={loading || !isFormValid()}
            className="bg-orange-500 hover:bg-orange-600 text-white px-8"
          >
            {loading ? 'Creating...' : 'Create report'}
          </Button>
        </div>
      </div>

      {/* Success Modal */}
      {showSuccessModal && generatedReport && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b border-gray-200">
              <div className="flex items-center">
                <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center mr-3">
                  <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
                    <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M16 8V2H4v16h12V8z" />
                    <path strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" d="M16 2l-6 6H4" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900">Generate Report Successfully</h3>
              </div>
              <button
                onClick={handleCloseSuccessModal}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-6">
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-blue-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                </div>
                <p className="text-gray-600 mb-4">
                  Your report has been generated successfully!
                </p>
                <div className="text-sm text-gray-500 mb-4">
                  <p><strong>Template:</strong> {generatedReport.template_upload.original_filename}</p>
                  <p><strong>Files processed:</strong> {generatedReport.file_uploads.successful_uploads}/{generatedReport.file_uploads.total_files}</p>
                  {generatedReport.generated_report.generated_file_path && (
                    <p className="text-xs text-gray-400 mt-2">
                      <strong>File path:</strong> {generatedReport.generated_report.generated_file_path}
                    </p>
                  )}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3">
                <Button
                  variant="outline"
                  onClick={handleViewReport}
                  className="flex-1"
                >
                  View
                </Button>
                <Button
                  onClick={handleDownloadReport}
                  className="flex-1 bg-orange-500 hover:bg-orange-600 text-white"
                >
                  Download
                </Button>
              </div>
            </div>

            {/* Modal Footer */}
            <div className="flex items-center justify-between px-6 py-4 border-t border-gray-200 bg-gray-50">
              <div className="flex items-center text-sm text-gray-600">
                <div className="w-2 h-2 bg-green-500 rounded-full mr-2"></div>
                <span>{formData.report_name || 'Generated Report'}</span>
              </div>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleCloseSuccessModal}
                >
                  Cancel
                </Button>
                <Button
                  size="sm"
                  onClick={handleCloseSuccessModal}
                  className="bg-orange-500 hover:bg-orange-600 text-white"
                >
                  Continue
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Office 365 Preview Modal */}
      <Office365PreviewModal
        isOpen={excelPreviewState.isOpen}
        onClose={closeExcelPreview}
        fileName={excelPreviewState.fileName}
        fileUrl={excelPreviewState.fileUrl}
        fileType={excelPreviewState.fileType}
      />
    </div>
  );
};
