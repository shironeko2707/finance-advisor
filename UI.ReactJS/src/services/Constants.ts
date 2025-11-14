// Template constants shared across the application

export interface TemplateCategory {
  value: string;
  label: string;
}

export const TEMPLATE_CATEGORIES: TemplateCategory[] = [
  { value: '0', label: 'Default' },
  { value: '1', label: 'Company results' },
  { value: '2', label: 'Investment analysis' },
  { value: '3', label: 'Financial reports' },
  { value: '4', label: 'Market research' },
  { value: '5', label: 'Risk assessment' }
];

/**
 * Maps a category value to its corresponding label
 * @param categoryValue - The category value to map
 * @returns The corresponding category label or 'Default' if not found
 */
export const mapCategoryToLabel = (categoryValue: string): string => {
  const category = TEMPLATE_CATEGORIES.find(cat => cat.value === categoryValue);
  return category ? category.label : 'Default';
};
