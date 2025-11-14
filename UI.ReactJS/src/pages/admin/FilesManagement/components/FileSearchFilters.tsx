import React from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Select, SelectItem } from '@/components/atomic/select.tsx';
import { SearchableSelect } from '@/components/atomic/searchable-select.tsx';
import { convertUpperCase } from '@/utils/common';

interface FileSearchFiltersProps {
  filters: {
    fileName?: string;
    fileFormat?: string;
    uploadedUser?: string;
  };
  availableUsers: {
    user_id: number;
    full_name: string;
  }[];
  availableFormats: string[];
  loading: boolean;
  onFiltersChange: (field: string, value: string) => void;
  onRefreshFiles: () => void;
  onClearFilters: () => void;
}

export const FileSearchFilters: React.FC<FileSearchFiltersProps> = ({
  filters,
  availableUsers,
  availableFormats,
  loading,
  onFiltersChange,
  onRefreshFiles,
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
    <div className="mb-6">
      <div className="flex gap-4 mb-4">
        <div className='w-1/3'>
          <Label className="text-sm text-gray-700 mb-2 block">File name</Label>
          <Input
            value={filters.fileName || ''}
            onChange={(e) => handleSearchChange('fileName', e.target.value)}
            placeholder="Search by file name"
            className="h-10"
          />
        </div>

        <div className='w-1/5'>
          <Label className="text-sm text-gray-700 mb-2 block">File format</Label>
          <Select
            value={filters.fileFormat || ''}
            onValueChange={(value) => handleSearchChange('fileFormat', value)}
            placeholder="Select format"
          >
            {availableFormats.map(format => (
              <SelectItem key={format} value={format}>
                {convertUpperCase(format)}
              </SelectItem>
            ))}
          </Select>
        </div>
        <div className='w-1/5'>
          <Label className="text-sm text-gray-700 mb-2 block">Uploaded user</Label>
          <SearchableSelect
            value={filters.uploadedUser || ''}
            onValueChange={(value) => handleSearchChange('uploadedUser', value)}
            placeholder="Type to search..."
          >
            {uniqueUsers.map(user => (
              <SelectItem key={user.user_id} value={(user.user_id).toString() || ""}>
                {user.full_name}
              </SelectItem>
            ))}
          </SearchableSelect>
        </div>
        <div className="flex justify-between items-end">
          <div className="flex items-center space-x-2">
            <Button
              variant="outline"
              className="text-white bg-[#635BFF] hover:bg-[#7b75f5] h-9"
              disabled={loading}
              onClick={onRefreshFiles}
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

    </div>
  );
};
