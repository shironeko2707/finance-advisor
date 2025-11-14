import { TemplateService } from './TemplateService';
import { TemplateMockService } from './TemplateMockService';
import { appConfig } from './datafix';
import type { Template, TemplateRequest } from '../types';

// Unified template service interface
interface ITemplateService {
  getTemplates(): Promise<Template[]>;
  getTemplateById(id: string): Promise<Template | null>;
  createTemplate(templateData: TemplateRequest): Promise<Template>;
  updateTemplate(id: string, templateData: Partial<TemplateRequest>): Promise<Template>;
  deleteTemplate(id: string): Promise<boolean | void>;
}

// Export the appropriate service based on configuration
export const templateService: ITemplateService = appConfig.useFixture
  ? TemplateMockService
  : TemplateService;

// Also export individual services for direct access if needed
export { TemplateService, TemplateMockService, appConfig };
export * from './datafix';
