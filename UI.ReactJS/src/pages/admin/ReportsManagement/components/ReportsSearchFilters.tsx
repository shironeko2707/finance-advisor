import React from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { SelectItem } from '@/components/atomic/select.tsx';
import { SearchableSelect } from '@/components/atomic/searchable-select';
import CustomDatePicker from './DatePicker';

interface ReportsSearchFiltersProps {
  filters: {
    reportName?: string;
    template?: string;
    createDate?: string;
    creator?: string;
  };
  availableUsers: {
    user_id: number;
    full_name: string;
  }[];
  availableTemplates: string[];
  loading: boolean;
  onFiltersChange: (field: string, value: string) => void;
  onRefreshReports: () => void;
  onClearFilters: () => void;
}

export const ReportsSearchFilters: React.FC<ReportsSearchFiltersProps> = ({
  filters,
  availableUsers,
  availableTemplates,
  loading,
  onFiltersChange,
  onRefreshReports,
  onClearFilters
}) => {

  const handleSearchChange = (field: string, value: string) => {
    onFiltersChange(field, value);
  };

  const uniqueUsers: {
    user_id: number;
    full_name: string;
  }[] = availableUsers.reduce((acc: { user_id: number; full_name: string }[], current) => {
    const x = acc.find(item => item?.user_id === current.user_id);
    if (!x) {
      return acc.concat([current]);
    } else {
      return acc;
    }
  }, []);

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-6">
      <div>
        <Label className="text-sm text-gray-700 mb-2 block">Report name</Label>
        <Input
          value={filters.reportName || ''}
          onChange={(e) => handleSearchChange('reportName', e.target.value)}
          placeholder="Search by report name"
          className="h-10"
        />
      </div>

      <div>
        <Label className="text-sm text-gray-700 mb-2 block">Template</Label>
        <SearchableSelect
          value={filters.template || ''}
          onValueChange={(value) => handleSearchChange('template', value)}
          placeholder="Type to search..."
        >
          {availableTemplates.map(template => (
            <SelectItem key={template} value={(template).toString() || ""}>
              {template}
            </SelectItem>
          ))}
        </SearchableSelect>
      </div>

      <div className="relative">
        <Label className="text-sm text-gray-700 mb-2 block">Create date</Label>
        <CustomDatePicker
          value={filters.createDate ?? ""}
          onChange={(dateStr) => handleSearchChange('createDate', dateStr)}
        />
      </div>

      <div>
        <Label className="text-sm text-gray-700 mb-2 block">Creator</Label>
        <SearchableSelect
          value={filters.creator || ''}
          onValueChange={(value) => handleSearchChange('creator', value)}
          placeholder="Type to search..."
        >
          {uniqueUsers.map(user => (
            <SelectItem key={user.user_id} value={(user.user_id).toString() || ""}>
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
          onClick={onRefreshReports}
        >
          {/* <Search className="w-4 h-4 mr-1" /> */}
          Search
        </Button>
        <Button
          variant="outline"
          className="text-white bg-[#635BFF] hover:bg-[#7b75f5] h-9"
          disabled={loading}
          onClick={onClearFilters}
        >
          {/* <X className="w-4 h-4 mr-1" /> */}
          Clear search
        </Button>
      </div>
    </div>
  );
};
