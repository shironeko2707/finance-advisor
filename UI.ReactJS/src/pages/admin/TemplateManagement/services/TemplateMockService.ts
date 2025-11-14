import type { Template, TemplateRequest } from '../types';
import { mockTemplates } from './datafix';

// Template Mock service - Handles mock data operations for development/testing
export class TemplateMockService {
  // Get all templates
  static async getTemplates(): Promise<Template[]> {
    await new Promise(resolve => setTimeout(resolve, 500));
    return [...mockTemplates];
  }

  // Get template by ID
  static async getTemplateById(id: number): Promise<Template | null> {
    await new Promise(resolve => setTimeout(resolve, 300));
    return mockTemplates.find(template => template.id === id) || null;
  }

  // Create new template
  static async createTemplate(templateData: TemplateRequest): Promise<Template> {
    await new Promise(resolve => setTimeout(resolve, 800));

    const newTemplate: Template = {
      ...templateData,
      id: Date.now(),
      creator_name: 'System', // Should come from auth context
      modifier_name: 'System',
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
      version: '1.0'
    };

    mockTemplates.push(newTemplate);
    return newTemplate;
  }

  // Update template
  static async updateTemplate(id: number, templateData: Partial<TemplateRequest>): Promise<Template> {
    await new Promise(resolve => setTimeout(resolve, 600));

    const templateIndex = mockTemplates.findIndex(template => template.id === id);
    if (templateIndex === -1) {
      throw new Error('Template not found');
    }

    mockTemplates[templateIndex] = {
      ...mockTemplates[templateIndex],
      ...templateData,
      modifier_name: 'System', // Should come from auth context
      updated_at: new Date().toISOString()
    };

    return mockTemplates[templateIndex];
  }

  // Delete template
  static async deleteTemplate(id: number): Promise<boolean> {
    await new Promise(resolve => setTimeout(resolve, 400));

    const templateIndex = mockTemplates.findIndex(template => template.id === id);
    if (templateIndex === -1) {
      throw new Error('Template not found');
    }

    mockTemplates.splice(templateIndex, 1);
    return true;
  }
}