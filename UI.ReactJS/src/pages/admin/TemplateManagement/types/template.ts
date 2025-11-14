// Template interface for UI
export interface Template {
  id: number;
  name: string;
  category: string;
  fileName?: string;
  version?: string;
  created_at: string;
  updated_at: string;
  status: 'active' | 'inactive';
  downloadCount: number;
  created_by: string;
  isActive: boolean;
  file_url?: string;
  modifier_name?: string;
  creator_name?: string;
  description?: string;
}

// Template request interface for creating/updating templates
export interface TemplateRequest {
  name: string;
  category: string;
  fileName?: string;
}

// Template filters interface for search/filtering
export interface TemplateFilters {
  search: string;
  category: string;
  isActive: string;
  createdBy: string;
  creator: string;
}

// Template list state interface for useTemplateList hook
export interface TemplateListState {
  templates: Template[];
  loading: boolean;
  error: string | null;
  success: string | null;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalTemplates: number;
  filters: TemplateFilters;
}

// API response interface (snake_case from backend)
export interface TemplateApiResponseSnake {
  id: string;
  name: string;
  description: string;
  category: string;
  file_path: string;
  filename: string;
  file_size: number;
  creator: string;
  creator_name: string;
  modifier: string;
  modifier_name: string;
  modify_time: string;
  updated_at: string;
  status: 'active' | 'inactive';
  version: string;
  download_count: number;
  created_by: string;
  is_active: boolean;
  created_at?: string;
}

// Template form data interface
export interface TemplateFormData {
  name: string;
  category: string;
  fileName?: string;
}

// Template list response interface
export interface TemplateListResponse {
  templates: Template[];
  total: number;
}

// Template category interface
export interface TemplateCategory {
  value: string;
  label: string;
}

// Create template request interface
export interface CreateTemplateRequest {
  name: string;
  category: string;
  fileName?: string;
}

// Update template request interface
export interface UpdateTemplateRequest {
  name: string;
  category: string;
  fileName?: string;
}
