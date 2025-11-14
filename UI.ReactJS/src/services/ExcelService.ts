import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import type { FieldMapping, ReportData, TableData } from '../types/report';

export class ExcelService {
  /**
   * Read Excel template file and return workbook
   */
  static async readTemplate(file: File): Promise<XLSX.WorkBook> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const data = new Uint8Array(e.target?.result as ArrayBuffer);
          const workbook = XLSX.read(data, { type: 'array' });
          resolve(workbook);
        } catch (error) {
          reject(error);
        }
      };
      reader.onerror = reject;
      reader.readAsArrayBuffer(file);
    });
  }

  /**
   * Apply data mappings to Excel template
   */
  static applyMappings(
    workbook: XLSX.WorkBook,
    mappings: FieldMapping[],
    data: ReportData
  ): XLSX.WorkBook {
    const clonedWorkbook = XLSX.utils.book_new();
    
    // Clone all worksheets
    workbook.SheetNames.forEach(sheetName => {
      const worksheet = workbook.Sheets[sheetName];
      const clonedWorksheet = XLSX.utils.aoa_to_sheet(XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as unknown[][]);
      XLSX.utils.book_append_sheet(clonedWorkbook, clonedWorksheet, sheetName);
    });

    // Apply mappings
    mappings.forEach(mapping => {
      const value = this.getDataValue(mapping, data);
      if (value !== undefined) {
        const sheetName = clonedWorkbook.SheetNames[0]; // Use first sheet for simplicity
        const worksheet = clonedWorkbook.Sheets[sheetName];
        
        // Set cell value
        XLSX.utils.sheet_add_aoa(worksheet, [[value]], { origin: mapping.targetCell });
      }
    });

    return clonedWorkbook;
  }

  /**
   * Get data value based on mapping configuration
   */
  private static getDataValue(mapping: FieldMapping, data: ReportData): unknown {
    const { sourceField, dataType } = mapping;

    switch (dataType) {
      case 'text': {
        const textData = data.texts.find(t => t.name === sourceField);
        return textData?.value || '';
      }

      case 'number': {
        const numberData = data.texts.find(t => t.name === sourceField);
        return typeof numberData?.value === 'number' ? numberData.value : 0;
      }

      case 'date': {
        const dateData = data.texts.find(t => t.name === sourceField);
        return dateData?.value instanceof Date ? dateData.value.toISOString().split('T')[0] : '';
      }

      case 'table': {
        const tableData = data.tables.find(t => t.name === sourceField);
        return tableData ? this.formatTableForExcel(tableData) : '';
      }

      case 'chart': {
        const chartData = data.charts.find(c => c.name === sourceField);
        return chartData ? JSON.stringify(chartData.data) : '';
      }

      default:
        return '';
    }
  }

  /**
   * Format table data for Excel insertion
   */
  private static formatTableForExcel(table: TableData): string {
    const headers = table.headers.join('\t');
    const rows = table.rows.map((row: unknown[]) => row.join('\t')).join('\n');
    return `${headers}\n${rows}`;
  }

  /**
   * Generate Excel file and trigger download
   */
  static downloadExcel(workbook: XLSX.WorkBook, filename: string): void {
    const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
    const blob = new Blob([excelBuffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, `${filename}.xlsx`);
  }

  /**
   * Convert workbook to HTML for preview
   */
  static workbookToHTML(workbook: XLSX.WorkBook): string {
    const sheetName = workbook.SheetNames[0];
    const worksheet = workbook.Sheets[sheetName];
    return XLSX.utils.sheet_to_html(worksheet, { header: '', footer: '' });
  }

  /**
   * Create sample data for testing
   */
  static createSampleData(): ReportData {
    return {
      texts: [
        { id: '1', name: 'companyName', value: 'UOB Bank Ltd.' },
        { id: '2', name: 'reportDate', value: new Date('2025-01-21') },
        { id: '3', name: 'totalRevenue', value: 1250000 },
        { id: '4', name: 'netProfit', value: 340000 }
      ],
      tables: [
        {
          id: '1',
          name: 'financialSummary',
          headers: ['Account', 'Q1', 'Q2', 'Q3', 'Q4'],
          rows: [
            ['Revenue', 300000, 310000, 315000, 325000],
            ['Expenses', 200000, 205000, 210000, 215000],
            ['Net Income', 100000, 105000, 105000, 110000]
          ]
        }
      ],
      charts: [
        {
          id: '1',
          name: 'quarterlyRevenue',
          type: 'bar',
          labels: ['Q1', 'Q2', 'Q3', 'Q4'],
          data: [300000, 310000, 315000, 325000]
        }
      ]
    };
  }
}