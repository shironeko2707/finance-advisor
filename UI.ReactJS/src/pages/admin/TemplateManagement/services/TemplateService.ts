import { apiService } from '@/services/ApiInterceptor.ts';
import { mapCategoryToLabel } from '@/services/Constants.ts';
import type { Template, TemplateListResponse, CreateTemplateRequest, UpdateTemplateRequest } from '../types';

// API response interface matching the actual backend response
interface TemplateApiResponse {
  id: number;
  name: string;
  category: string;
  file_name: string;
  file_path: string;
  version: string;
  created_at: string;
  updated_at: string | null;
  created_by: number;
  modified_by: number | null;
  creator_name: string | null;
  modifier_name: string | null;
  description?: string;
}

export class TemplateService {
  /**
   * Map API response to Template with proper field mapping and category label
   */
  private static mapTemplate(apiTemplate: TemplateApiResponse): Template {
    return {
      id: apiTemplate.id,
      name: apiTemplate.name,
      category: mapCategoryToLabel(apiTemplate.category),
      fileName: apiTemplate.file_name, // Map snake_case to camelCase
      version: apiTemplate.version,
      created_at: apiTemplate.created_at,
      updated_at: apiTemplate.updated_at || apiTemplate.created_at,
      file_url: apiTemplate.file_path,
      modifier_name: apiTemplate.modifier_name || undefined,
      creator_name: apiTemplate.creator_name || undefined,
      description: apiTemplate.description
    };
  }

  /**
   * Get templates from the API
   */
  static async getTemplates(): Promise<TemplateListResponse> {
    try {
      const response = await apiService.api.getTemplates();
      // Map category values to labels for each template
      if (response.templates && Array.isArray(response.templates)) {
        response.templates = response.templates.map(template => this.mapTemplate(template as TemplateApiResponse));
      }
      return response as TemplateListResponse;
    } catch (error) {
      console.error('Failed to fetch templates:', error);
      throw new Error('Failed to fetch templates');
    }
  }

  /**
   * Get a single template by ID
   */
  static async getTemplate(templateId: number): Promise<Template> {
    try {
      const response = await apiService.api.getTemplate(templateId);
      // Map category value to label
      return this.mapTemplate(response as TemplateApiResponse);
    } catch (error) {
      console.error('Failed to fetch template:', error);
      throw new Error('Failed to fetch template');
    }
  }

  /**
   * Create a new template
   */
  static async createTemplate(templateData: CreateTemplateRequest): Promise<Template> {
    try {
      const response = await apiService.api.createTemplate(templateData);
      // Map category value to label
      return this.mapTemplate(response as TemplateApiResponse);
    } catch (error) {
      console.error('Failed to create template:', error);
      throw new Error('Failed to create template');
    }
  }

  /**
   * Update an existing template
   */
  static async updateTemplate(templateId: number, templateData: UpdateTemplateRequest): Promise<Template> {
    try {
      const response = await apiService.api.updateTemplate(templateId, templateData);
      // Map category value to label
      return this.mapTemplate(response as TemplateApiResponse);
    } catch (error) {
      console.error('Failed to update template:', error);
      throw new Error('Failed to update template');
    }
  }

  /**
   * Delete a template by ID
   */
  static async deleteTemplate(templateId: number): Promise<void> {
    try {
      await apiService.api.deleteTemplate(templateId);
    } catch (error) {
      console.error('Failed to delete template:', error);
      throw new Error('Failed to delete template');
    }
  }

  /**
   * Download a template file
   */
  static async downloadTemplate(templateId: number): Promise<Blob> {
    try {
      const blob = await apiService.api.downloadTemplate(templateId);
      return blob;
    } catch (error) {
      console.error('Failed to download template:', error);
      throw new Error('Failed to download template');
    }
  }
}
