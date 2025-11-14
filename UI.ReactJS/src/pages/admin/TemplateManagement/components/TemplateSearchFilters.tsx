import React from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Select, SelectItem } from '@/components/atomic/select.tsx';
import type { TemplateFilters } from '../types';
import { SearchableSelect } from '@/components/atomic/searchable-select';
import type { TEMPLATE_CATEGORIES } from '@/services/Constants';

interface TemplateSearchFiltersProps {
  filters: TemplateFilters;
  availableCategories: typeof TEMPLATE_CATEGORIES;
  availableCreators: {
    user_id: string;
    full_name: string;
  }[];
  loading: boolean;
  onFiltersChange: (filters: Partial<TemplateFilters>) => void;
  onRefreshTemplates: () => void;
  onClearFilters: () => void;
}

export const TemplateSearchFilters: React.FC<TemplateSearchFiltersProps> = ({
  filters,
  availableCategories,
  availableCreators,
  loading,
  onFiltersChange,
  onRefreshTemplates,
  onClearFilters,
}) => {
  const handleSearchChange = (field: keyof TemplateFilters, value: string) => {
    onFiltersChange({ [field]: value });
  };

  const newUniqueUsers = availableCreators.reduce((acc: { user_id: string; full_name: string }[], current) => {
    const x = acc.find(item => item?.user_id === current.user_id);
    if (!x) {
      return acc.concat([current]);
    } else {
      return acc;
    }
  }, []);

  const handleInputChange = (field: keyof TemplateFilters, value: string) => {
    onFiltersChange({ [field]: value });
  };

  return (
    <div className="mb-6">
      <div className="flex gap-3">
        <div className='w-1/3'>
          <Label className="text-sm text-gray-700 mb-2 block">Search</Label>
          <Input
            value={filters.search || ''}
            onChange={(e) => handleInputChange('search', e.target.value)}
            placeholder="Search templates..."
            className="h-10"
          />
        </div>

        <div className='w-1/4'>
          <Label className="text-sm text-gray-700 mb-2 block">Category</Label>
          <SearchableSelect
            value={filters.category || ''}
            onValueChange={(value) => handleSearchChange('category', value)}
            placeholder="Type to search..."
          >
            {availableCategories.map(category => (
              <SelectItem key={category.label} value={category.value}>
                {category.label}
              </SelectItem>
            ))}
          </SearchableSelect>
        </div>

        <div className='w-1/4'>
          <Label className="text-sm text-gray-700 mb-2 block">Created By</Label>
          {/* <Select
            value={filters.createdBy || ''}
            onValueChange={(value) => handleSearchChange('createdBy', value)}
            placeholder="Select creator"
          >
            {availableCreators.map(creator => (
              <SelectItem key={creator} value={creator}>
                {creator}
              </SelectItem>
            ))}
          </Select> */}
          <SearchableSelect
            value={filters.creator || ''}
            onValueChange={(value) => handleSearchChange('creator', value)}
            placeholder="Type to search..."
          >
            {newUniqueUsers.map((user: { user_id: string; full_name: string }) => (
              <SelectItem key={user.user_id} value={user.user_id || ""}>
                {user.full_name}
              </SelectItem>
            ))}
          </SearchableSelect>
        </div>

        <div className="flex items-end space-x-2">
          <Button
            variant="outline"
            className="text-white bg-[#635BFF] hover:bg-[#7b75f5] h-9"
            disabled={loading}
            onClick={onRefreshTemplates}
          >
            Search
          </Button>
          <Button
            variant="outline"
            className="text-white bg-[#635BFF] hover:bg-[#7b75f5] h-9"
            disabled={loading}
            onClick={onClearFilters}
          >
            Clear search
          </Button>
        </div>
      </div>
    </div>
  );
};
