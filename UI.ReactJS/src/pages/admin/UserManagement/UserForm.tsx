import React from 'react';
import { Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { Select, SelectItem } from '@/components/atomic/select.tsx';
import { useUserForm } from './hooks/useUserForm';

export const UserForm: React.FC = () => {
  const {
    // State
    formData,
    errors,
    loading,
    initialLoading,
    error,
    success,
    showPassword,
    isEditMode,

    // Actions
    handleInputChange,
    handleSubmit,
    handleCancel,
    setShowPassword
  } = useUserForm();

  // Simple input change handler with validation
  const handleValidatedInputChange = (field: keyof typeof formData) => {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      if (value.length > 255) {
        alert(`Maximum 255 characters allowed for this field!`);
        return;
      }
      handleInputChange(field, value);
    };
  };

  return (
    <div className="p-6">
      <div className="mb-6">
        <h1 className="text-xl font-medium text-gray-900 mb-2">Users</h1>
        <h2 className="text-lg text-gray-700">
          {isEditMode ? 'Edit user' : 'Create new user'}
        </h2>
      </div>

      {/* Loading state for edit mode */}
      {initialLoading && (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm mt-2">Loading user data...</p>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm">✅ {success}</p>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">⚠ {error}</p>
        </div>
      )}

      {!initialLoading && (
        <form onSubmit={handleSubmit} className="bg-gray-100 p-6 rounded-lg">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
          {/* Username */}
          <div>
            <Label htmlFor="username" className="text-sm font-medium text-gray-700 mb-2 block">
              Username <span className="text-red-500">*</span>
            </Label>
            <Input
              id="username"
              value={formData.username}
              onChange={handleValidatedInputChange('username')}
              className="h-10"
              placeholder=""
            />
            {errors.username && (
              <p className="text-red-500 text-xs mt-1">⚠ {errors.username}</p>
            )}
          </div>

          {/* First Name */}
          <div>
            <Label htmlFor="firstName" className="text-sm font-medium text-gray-700 mb-2 block">
              First name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="firstName"
              value={formData.firstName}
              onChange={handleValidatedInputChange('firstName')}
              className="h-10"
              placeholder=""
            />
            {errors.firstName && (
              <p className="text-red-500 text-xs mt-1">⚠ {errors.firstName}</p>
            )}
          </div>

          {/* Last Name */}
          <div>
            <Label htmlFor="lastName" className="text-sm font-medium text-gray-700 mb-2 block">
              Last name <span className="text-red-500">*</span>
            </Label>
            <Input
              id="lastName"
              value={formData.lastName}
              onChange={handleValidatedInputChange('lastName')}
              className="h-10"
              placeholder=""
            />
            {errors.lastName && (
              <p className="text-red-500 text-xs mt-1">⚠ {errors.lastName}</p>
            )}
          </div>

          {/* Job Title */}
          <div>
            <Label htmlFor="jobTitle" className="text-sm font-medium text-gray-700 mb-2 block">
              Job title
            </Label>
            <Input
              id="jobTitle"
              value={formData.jobTitle}
              onChange={handleValidatedInputChange('jobTitle')}
              className="h-10"
              placeholder=""
            />
          </div>

          {/* Email */}
          <div>
            <Label htmlFor="email" className="text-sm font-medium text-gray-700 mb-2 block">
              Email <span className="text-red-500">*</span>
            </Label>
            <Input
              id="email"
              type="email"
              value={formData.email}
              onChange={handleValidatedInputChange('email')}
              className="h-10"
              placeholder=""
            />
            {errors.email && (
              <p className="text-red-500 text-xs mt-1">⚠ {errors.email}</p>
            )}
          </div>

          {/* Password */}
          <div>
            <Label htmlFor="password" className="text-sm font-medium text-gray-700 mb-2 block">
              Password {!isEditMode && <span className="text-red-500">*</span>}
              {isEditMode && <span className="text-gray-500 text-xs">(leave empty to keep current)</span>}
            </Label>
            <div className="relative">
              <Input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleValidatedInputChange('password')}
                className="h-10 pr-10"
                placeholder=""
              />
              <button
                type="button"
                onClick={() => setShowPassword(prev => !prev)}
                className="absolute inset-y-0 right-0 flex items-center pr-3"
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
            {errors.password && (
              <p className="text-red-500 text-xs mt-1">⚠ {errors.password}</p>
            )}
          </div>

          {/* Role */}
          <div>
            <Label htmlFor="role" className="text-sm font-medium text-gray-700 mb-2 block">
              Role <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.role}
              onValueChange={(value) => handleInputChange('role', value)}
              placeholder="Select role"
            >
              <SelectItem value="Admin">Admin</SelectItem>
              <SelectItem value="User">User</SelectItem>
            </Select>
            {errors.role && (
              <p className="text-red-500 text-xs mt-1">⚠ {errors.role}</p>
            )}
          </div>

          {/* Status */}
          <div>
            <Label htmlFor="status" className="text-sm font-medium text-gray-700 mb-2 block">
              Status <span className="text-red-500">*</span>
            </Label>
            <Select
              value={formData.status}
              onValueChange={(value) => handleInputChange('status', value)}
              placeholder="Select status"
            >
              <SelectItem value="Active">Active</SelectItem>
              <SelectItem value="Inactive">Inactive</SelectItem>
            </Select>
            {errors.status && (
              <p className="text-red-500 text-xs mt-1">⚠ {errors.status}</p>
            )}
          </div>
        </div>

        <div className="flex justify-end space-x-3">
          <Button 
            type="button" 
            variant="outline"
            onClick={handleCancel}
            className="px-6"
            disabled={loading || Boolean(success)}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            className="px-6 bg-orange-500 hover:bg-orange-600 text-white"
            disabled={loading || Boolean(success)}
          >
            {loading ? (
              <>
                <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                {isEditMode ? 'Updating...' : 'Creating...'}
              </>
            ) : (
              isEditMode ? 'Update' : 'Create'
            )}
          </Button>
        </div>
      </form>
      )}
    </div>
  );
};
