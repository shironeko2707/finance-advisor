import React, { useState, useEffect } from 'react';
import { ArrowLeft, Upload, FileSpreadsheet, Eye, Download } from 'lucide-react';
import { Card, CardContent, CardHeader } from '@/components/atomic/card.tsx';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Select, SelectItem } from '@/components/atomic/select.tsx';
import { Label } from '@/components/atomic/label.tsx';
import type { Report, Template, FieldMapping, ReportData } from '@/types/report';
import { ReportService } from '@/services/ReportService';
import { ExcelService } from '@/services/ExcelService';

interface CreateReportFormProps {
  onBack: () => void;
  onSuccess: () => void;
}

type Step = 'basic' | 'template' | 'mapping' | 'preview';

export const CreateReportForm: React.FC<CreateReportFormProps> = ({ onBack, onSuccess }) => {
  const [currentStep, setCurrentStep] = useState<Step>('basic');
  const [loading, setLoading] = useState(false);
  const [templates, setTemplates] = useState<Template[]>([]);
  
  // Form data
  const [reportName, setReportName] = useState('');
  const [selectedTemplate, setSelectedTemplate] = useState('');
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [mappings, setMappings] = useState<FieldMapping[]>([]);
  const [previewHtml, setPreviewHtml] = useState('');

  // Sample data for demonstration
  const sampleData: ReportData = ExcelService.createSampleData();

  useEffect(() => {
    loadTemplates();
  }, []);

  const loadTemplates = async () => {
    try {
      const data = await ReportService.getTemplates();
      setTemplates(data);
    } catch (error) {
      console.error('Failed to load templates:', error);
    }
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setTemplateFile(file);
      // In a real app, you would parse the Excel file to extract cell references
      // For demo, we'll create some sample mappings
      const sampleMappings: FieldMapping[] = [
        {
          id: '1',
          sourceField: 'companyName',
          targetCell: 'B2',
          dataType: 'text'
        },
        {
          id: '2',
          sourceField: 'reportDate',
          targetCell: 'B3',
          dataType: 'date'
        },
        {
          id: '3',
          sourceField: 'totalRevenue',
          targetCell: 'B4',
          dataType: 'number'
        }
      ];
      setMappings(sampleMappings);
    }
  };

  const handlePreview = async () => {
    if (!templateFile) return;

    try {
      setLoading(true);
      const workbook = await ExcelService.readTemplate(templateFile);
      const mappedWorkbook = ExcelService.applyMappings(workbook, mappings, sampleData);
      const html = ExcelService.workbookToHTML(mappedWorkbook);
      setPreviewHtml(html);
      setCurrentStep('preview');
    } catch (error) {
      console.error('Failed to generate preview:', error);
      alert('Failed to generate preview. Please check your template file.');
    } finally {
      setLoading(false);
    }
  };

  const handleDownloadPreview = async () => {
    if (!templateFile) return;

    try {
      const workbook = await ExcelService.readTemplate(templateFile);
      const mappedWorkbook = ExcelService.applyMappings(workbook, mappings, sampleData);
      ExcelService.downloadExcel(mappedWorkbook, reportName || 'Generated Report');
    } catch (error) {
      console.error('Failed to download report:', error);
    }
  };

  const handleCreateReport = async () => {
    try {
      setLoading(true);
      // Trim reportName before sending to server
      const report: Omit<Report, 'id' | 'createdDate'> = {
        name: reportName.trim(),
        template: selectedTemplate?.trim() || 'Custom Template',
        creator: 'Admin User',
        status: 'completed'
      };
      
      await ReportService.createReport(report);
      onSuccess();
    } catch (error) {
      console.error('Failed to create report:', error);
    } finally {
      setLoading(false);
    }
  };

  const canProceedToTemplate = reportName.trim() !== '';
  const canProceedToMapping = selectedTemplate || templateFile;
  const canPreview = mappings.length > 0 && templateFile;

  const renderStep = () => {
    switch (currentStep) {
      case 'basic':
        return (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Basic Information</h3>
              <p className="text-sm text-gray-600">Enter the basic details for your report</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="reportName">Report Name *</Label>
                <Input
                  id="reportName"
                  value={reportName}
                  onChange={(e) => setReportName(e.target.value)}
                  placeholder="Enter report name (e.g., UOB Financial Review)"
                />
              </div>
              <div className="flex justify-end">
                <Button
                  onClick={() => setCurrentStep('template')}
                  disabled={!canProceedToTemplate}
                >
                  Next: Select Template
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      case 'template':
        return (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Template Selection</h3>
              <p className="text-sm text-gray-600">Choose an existing template or upload a custom one</p>
            </CardHeader>
            <CardContent className="space-y-6">
              <div>
                <Label htmlFor="template">Existing Template</Label>
                <Select
                  value={selectedTemplate}
                  onValueChange={setSelectedTemplate}
                  placeholder="Select a template..."
                >
                  {templates.map(template => (
                    <SelectItem key={template.id} value={template.name}>
                      {template.name}
                    </SelectItem>
                  ))}
                </Select>
              </div>
              
              <div className="flex items-center">
                <div className="flex-1 border-t border-gray-300"></div>
                <span className="px-4 text-sm text-gray-500">or</span>
                <div className="flex-1 border-t border-gray-300"></div>
              </div>

              <div>
                <Label htmlFor="fileUpload">Upload Custom Template</Label>
                <div className="mt-2">
                  <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-8 h-8 mb-4 text-gray-500" />
                      <p className="mb-2 text-sm text-gray-500">
                        {templateFile ? templateFile.name : 'Click to upload Excel template'}
                      </p>
                      <p className="text-xs text-gray-500">XLSX, XLS files only</p>
                    </div>
                    <input
                      id="fileUpload"
                      type="file"
                      className="hidden"
                      accept=".xlsx,.xls"
                      onChange={handleFileUpload}
                    />
                  </label>
                </div>
              </div>

              <div className="flex justify-between">
                <Button variant="outline" onClick={() => setCurrentStep('basic')}>
                  Back
                </Button>
                <Button
                  onClick={() => setCurrentStep('mapping')}
                  disabled={!canProceedToMapping}
                >
                  Next: Configure Mapping
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      case 'mapping':
        return (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Data Mapping Configuration</h3>
              <p className="text-sm text-gray-600">Configure how data maps to your template cells</p>
            </CardHeader>
            <CardContent className="space-y-4">
              {mappings.length > 0 ? (
                <>
                  <div className="space-y-3">
                    {mappings.map((mapping) => (
                      <div key={mapping.id} className="flex items-center gap-4 p-3 border rounded-lg">
                        <div className="flex-1">
                          <span className="text-sm font-medium">{mapping.sourceField}</span>
                          <div className="text-xs text-gray-500">
                            Sample value: {getSampleValue(mapping.sourceField)}
                          </div>
                        </div>
                        <div className="text-sm">
                          → Cell {mapping.targetCell}
                        </div>
                        <div className="text-xs text-gray-500 px-2 py-1 bg-gray-100 rounded">
                          {mapping.dataType}
                        </div>
                      </div>
                    ))}
                  </div>
                  <div className="flex justify-between">
                    <Button variant="outline" onClick={() => setCurrentStep('template')}>
                      Back
                    </Button>
                    <Button
                      onClick={handlePreview}
                      disabled={!canPreview || loading}
                    >
                      <Eye className="w-4 h-4 mr-2" />
                      {loading ? 'Generating...' : 'Preview Report'}
                    </Button>
                  </div>
                </>
              ) : (
                <div className="text-center py-8">
                  <FileSpreadsheet className="w-12 h-12 mx-auto text-gray-400 mb-4" />
                  <p className="text-gray-500 mb-4">No mappings available. Please upload a template first.</p>
                  <Button variant="outline" onClick={() => setCurrentStep('template')}>
                    Back to Template Selection
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        );

      case 'preview':
        return (
          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold">Report Preview</h3>
              <p className="text-sm text-gray-600">Preview your generated report before saving</p>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="border rounded-lg p-4 bg-gray-50 max-h-96 overflow-auto">
                {previewHtml ? (
                  <div dangerouslySetInnerHTML={{ __html: previewHtml }} />
                ) : (
                  <p className="text-gray-500">Preview not available</p>
                )}
              </div>
              
              <div className="flex justify-between">
                <div className="space-x-2">
                  <Button variant="outline" onClick={() => setCurrentStep('mapping')}>
                    Back to Mapping
                  </Button>
                  <Button variant="outline" onClick={handleDownloadPreview}>
                    <Download className="w-4 h-4 mr-2" />
                    Download Preview
                  </Button>
                </div>
                <Button
                  onClick={handleCreateReport}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {loading ? 'Creating...' : 'Create Report'}
                </Button>
              </div>
            </CardContent>
          </Card>
        );

      default:
        return null;
    }
  };

  const getSampleValue = (fieldName: string): string => {
    const textData = sampleData.texts.find(t => t.name === fieldName);
    if (textData) {
      return String(textData.value);
    }
    return 'Sample value';
  };

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <Button onClick={onBack} variant="outline" className="mb-4">
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back to Reports
        </Button>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Create New Report</h1>
        <p className="text-gray-600">Follow the steps to create a new report with custom data mapping.</p>
      </div>

      {/* Progress Steps */}
      <div className="mb-8">
        <div className="flex items-center">
          {(['basic', 'template', 'mapping', 'preview'] as Step[]).map((step, index) => (
            <React.Fragment key={step}>
              <div className={`flex items-center ${
                currentStep === step 
                  ? 'text-blue-600' 
                  : index < ['basic', 'template', 'mapping', 'preview'].indexOf(currentStep)
                    ? 'text-green-600'
                    : 'text-gray-400'
              }`}>
                <div className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-medium ${
                  currentStep === step 
                    ? 'border-blue-600 bg-blue-50' 
                    : index < ['basic', 'template', 'mapping', 'preview'].indexOf(currentStep)
                      ? 'border-green-600 bg-green-50'
                      : 'border-gray-300'
                }`}>
                  {index + 1}
                </div>
                <span className="ml-2 text-sm font-medium capitalize">{step}</span>
              </div>
              {index < 3 && (
                <div className={`flex-1 h-0.5 mx-4 ${
                  index < ['basic', 'template', 'mapping', 'preview'].indexOf(currentStep)
                    ? 'bg-green-600'
                    : 'bg-gray-300'
                }`}></div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>

      {/* Current Step Content */}
      {renderStep()}
    </div>
  );
};