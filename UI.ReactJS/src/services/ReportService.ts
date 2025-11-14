import type { Report, Template, ReportFilters } from '../types/report';

export class ReportService {
  // Mock data - in a real app this would come from an API
  private static reports: Report[] = [
    {
      id: '1',
      name: 'UOB Financial Review',
      template: 'Company results',
      createdDate: '21/07/2025',
      creator: 'Jason Derulo',
      status: 'completed'
    },
    {
      id: '2',
      name: 'UOB Financial Review',
      template: 'Company results',
      createdDate: '21/07/2025',
      creator: 'Jason Derulo',
      status: 'completed'
    }
  ];

  private static templates: Template[] = [
    {
      id: '1',
      name: 'Company results',
      description: 'Standard company financial results template',
      file: null,
      mappings: []
    },
    {
      id: '2',
      name: 'Quarterly Report',
      description: 'Quarterly performance report template',
      file: null,
      mappings: []
    }
  ];

  /**
   * Get all reports with optional filtering
   */
  static async getReports(filters?: ReportFilters): Promise<Report[]> {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 300));
    
    let filteredReports = [...this.reports];

    if (filters) {
      if (filters.search) {
        filteredReports = filteredReports.filter(report => 
          report.name.toLowerCase().includes(filters.search.toLowerCase()) ||
          report.creator.toLowerCase().includes(filters.search.toLowerCase())
        );
      }

      if (filters.template) {
        filteredReports = filteredReports.filter(report => 
          report.template === filters.template
        );
      }

      if (filters.creator) {
        filteredReports = filteredReports.filter(report => 
          report.creator === filters.creator
        );
      }
    }

    return filteredReports;
  }

  /**
   * Get report by ID
   */
  static async getReport(id: string): Promise<Report | null> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return this.reports.find(report => report.id === id) || null;
  }

  /**
   * Create new report
   */
  static async createReport(report: Omit<Report, 'id' | 'createdDate'>): Promise<Report> {
    await new Promise(resolve => setTimeout(resolve, 500));
    
    const newReport: Report = {
      ...report,
      id: Date.now().toString(),
      createdDate: new Date().toLocaleDateString('en-GB')
    };
    
    this.reports.unshift(newReport);
    return newReport;
  }

  /**
   * Update report
   */
  static async updateReport(id: string, updates: Partial<Report>): Promise<Report | null> {
    await new Promise(resolve => setTimeout(resolve, 300));
    
    const reportIndex = this.reports.findIndex(report => report.id === id);
    if (reportIndex === -1) return null;
    
    this.reports[reportIndex] = { ...this.reports[reportIndex], ...updates };
    return this.reports[reportIndex];
  }

  /**
   * Delete report
   */
  static async deleteReport(id: string): Promise<boolean> {
    await new Promise(resolve => setTimeout(resolve, 200));
    
    const reportIndex = this.reports.findIndex(report => report.id === id);
    if (reportIndex === -1) return false;
    
    this.reports.splice(reportIndex, 1);
    return true;
  }

  /**
   * Get available templates
   */
  static async getTemplates(): Promise<Template[]> {
    await new Promise(resolve => setTimeout(resolve, 200));
    return [...this.templates];
  }

  /**
   * Get unique creators for filtering
   */
  static async getCreators(): Promise<string[]> {
    await new Promise(resolve => setTimeout(resolve, 100));
    return Array.from(new Set(this.reports.map(report => report.creator)));
  }

  /**
   * Get unique templates for filtering  
   */
  static async getTemplateNames(): Promise<string[]> {
    await new Promise(resolve => setTimeout(resolve, 100));
    return Array.from(new Set(this.reports.map(report => report.template)));
  }
}