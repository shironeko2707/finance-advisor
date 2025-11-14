export interface Report {
  id: string;
  name: string;
  template: string;
  createdDate: string;
  creator: string;
  status: 'draft' | 'completed' | 'error';
  data?: unknown;
}

export interface Template {
  id: string;
  name: string;
  description?: string;
  file: File | null;
  mappings: FieldMapping[];
}

export interface FieldMapping {
  id: string;
  sourceField: string;
  targetCell: string;
  dataType: 'text' | 'number' | 'date' | 'table' | 'chart';
  transform?: string; // Optional transformation function
}

export interface ReportData {
  tables: TableData[];
  texts: TextData[];
  charts: ChartData[];
}

export interface TableData {
  id: string;
  name: string;
  headers: string[];
  rows: unknown[][];
}

export interface TextData {
  id: string;
  name: string;
  value: string | number | Date;
}

export interface ChartData {
  id: string;
  name: string;
  type: 'bar' | 'line' | 'pie';
  data: unknown[];
  labels: string[];
}

export interface ReportFilters {
  search: string;
  template: string;
  creator: string;
  dateFrom: string;
  dateTo: string;
}

export interface DropdownMenuItem {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  className?: string;
  disabled?: boolean;
}