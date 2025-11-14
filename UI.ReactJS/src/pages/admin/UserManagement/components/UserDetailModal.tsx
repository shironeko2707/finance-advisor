import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/atomic/button.tsx';
import { Label } from '@/components/atomic/label.tsx';
import {User as UserIcon, Mail, Shield, X, Edit} from 'lucide-react';
import type { User } from '../types/user';

interface UserDetailModalProps {
  isOpen: boolean;
  user: User | null;
  onClose: () => void;
}

export const UserDetailModal: React.FC<UserDetailModalProps> = ({
  isOpen,
  user,
  onClose
}) => {
  const navigate = useNavigate();

  if (!isOpen || !user) {
    return null;
  }

  const handleEditUser = () => {
    navigate(`/users/${user.id}/edit`);
    onClose();
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900">User Details</h3>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="p-6 space-y-6">
          {/* Basic Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <UserIcon className="w-4 h-4 mr-2 text-blue-600" />
              Basic Information
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Username</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {user.username}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Full Name</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border min-h-[2.5rem] flex items-center">
                  {user.firstName || user.lastName
                    ? `${user.firstName} ${user.lastName}`.trim()
                    : <span className="text-gray-500 italic">No name provided</span>
                  }
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Job Title</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border min-h-[2.5rem] flex items-center">
                  {user.jobTitle || <span className="text-gray-500 italic">No job title provided</span>}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">User ID</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border font-mono">
                  {user.id}
                </p>
              </div>
            </div>
          </div>

          {/* Contact Information */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Mail className="w-4 h-4 mr-2 text-green-600" />
              Contact Information
            </h4>
            <div>
              <Label className="text-sm font-medium text-gray-700">Email Address</Label>
              <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                {user.email}
              </p>
            </div>
          </div>

          {/* Role & Access */}
          <div>
            <h4 className="text-md font-medium text-gray-900 mb-4 flex items-center">
              <Shield className="w-4 h-4 mr-2 text-purple-600" />
              Role & Access
            </h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label className="text-sm font-medium text-gray-700">Role</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  {user.role}
                </p>
              </div>
              <div>
                <Label className="text-sm font-medium text-gray-700">Status</Label>
                <p className="text-sm text-gray-900 mt-1 p-2 bg-gray-50 rounded border">
                  <span className={`inline-flex px-2 py-1 text-xs font-medium rounded-full ${
                    user.status === 'Active'
                      ? 'bg-green-100 text-green-800'
                      : 'bg-red-100 text-red-800'
                  }`}>
                    {user.status}
                  </span>
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="flex items-center justify-end space-x-3 p-6 border-t border-gray-200 bg-gray-50">
          <Button
            variant="outline"
            onClick={onClose}
          >
            Close
          </Button>
          <Button
            onClick={handleEditUser}
            className="bg-orange-500 hover:bg-orange-600 text-white"
          >
            <Edit className="w-4 h-4 mr-2" />
            Edit User
          </Button>
        </div>
      </div>
    </div>
  );
};
