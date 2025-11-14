import React from 'react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Select, SelectItem } from '@/components/atomic/select.tsx';
import type { UserFilter } from '../types/user';

interface UserSearchFiltersProps {
  filters: UserFilter;
  availableRoles: string[];
  loading: boolean;
  onFiltersChange: (field: string, value: string) => void;
  onRefreshUsers: () => void;
  onClearFilters: () => void;
}

export const UserSearchFilters: React.FC<UserSearchFiltersProps> = ({
  filters,
  availableRoles,
  loading,
  onFiltersChange,
  onRefreshUsers,
  onClearFilters,
}) => {
  const handleSearchChange = (field: string, value: string) => {
    onFiltersChange(field, value);
  };

  return (
    <div className="mb-6">
      <div className="flex gap-3">
        <div className='w-1/3'>
          <Label className="text-sm text-gray-700 mb-2 block">Search</Label>
          <Input
            value={filters.searchTerm || ''}
            onChange={(e) => handleSearchChange('searchTerm', e.target.value)}
            placeholder="Search by name, username, or email"
            className="h-10"
          />
        </div>

        <div className='w-1/5'>
          <Label className="text-sm text-gray-700 mb-2 block">Role</Label>
          <Select
            value={filters.role || ''}
            onValueChange={(value) => handleSearchChange('role', value)}
            placeholder="Select role"
          >
            {availableRoles.map(role => (
              <SelectItem key={role} value={role}>
                {role}
              </SelectItem>
            ))}
          </Select>
        </div>

        <div className='w-1/5'>
          <Label className="text-sm text-gray-700 mb-2 block">Status</Label>
          <Select
            value={filters.status || ''}
            onValueChange={(value) => handleSearchChange('status', value)}
            placeholder="Select status"
          >
            <SelectItem value="Active">Active</SelectItem>
            <SelectItem value="Inactive">Inactive</SelectItem>
          </Select>
        </div>
        <div className="flex items-end space-x-2">
          <Button
            variant="outline"
            className="text-white bg-[#635BFF] hover:bg-[#7b75f5] h-9"
            disabled={loading}
            onClick={onRefreshUsers}
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

    </div>
  );
};
