import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/atomic/button.tsx';
import {Eye, Edit, Trash2, Shield, MoreHorizontal, Plus} from 'lucide-react';
import { useUserList } from './hooks/useUserList';
import { shouldUseFixture } from '@/config/config.ts';
import { UserSearchFilters } from './components/UserSearchFilters';
import { UserDetailModal } from './components/UserDetailModal';
import type { User } from './types/user';

// Local development flag - can override global config
const USE_FIXTURE = shouldUseFixture('USE_FIXTURE', false);

export const UserList: React.FC = () => {
  const navigate = useNavigate();
  const {
    users,
    loading,
    error,
    success,
    currentPage,
    totalPages,
    pageSize,
    totalUsers,
    filters,
    updateFilters,
    clearFilters,
    availableRoles,
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    toggleUserStatus,
    deleteUser,
    refreshUsers,
    clearNotifications
  } = useUserList({ useFixture: USE_FIXTURE });

  const [openActionMenu, setOpenActionMenu] = useState<string | null>(null);
  const [userDetailModal, setUserDetailModal] = useState<{
    isOpen: boolean;
    user: User | null;
  }>({
    isOpen: false,
    user: null
  });

  const actionMenuRef = useRef<HTMLDivElement | null>(null);

  // Auto-dismiss success notifications after 3 seconds
  React.useEffect(() => {
    if (success) {
      const timer = setTimeout(() => {
        clearNotifications();
      }, 3000);
      return () => clearTimeout(timer);
    }
  }, [success, clearNotifications]);

  // Close action menu if clicked outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (actionMenuRef.current && !actionMenuRef.current.contains(event.target as Node)) {
        setOpenActionMenu(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [actionMenuRef]);

  const handleViewUser = (userId: string) => {
    const user = users.find(u => u.id === userId);
    if (user) {
      setUserDetailModal({
        isOpen: true,
        user: user
      });
    }
  };

  const handleEditUser = (userId: string) => {
    navigate(`/users/${userId}/edit`);
    setOpenActionMenu(null);
  };

  const handleDeleteUser = async (userId: string) => {
    if (window.confirm('Are you sure you want to delete this user?')) {
      await deleteUser(userId);
      setOpenActionMenu(null);
    }
  };

  const handleToggleStatus = async (userId: string) => {
    await toggleUserStatus(userId);
    setOpenActionMenu(null);
  };

  const toggleActionMenu = (userId: string) => {
    setOpenActionMenu(openActionMenu === userId ? null : userId);
  };

  const generatePageNumbers = () => {
    const pages: number[] = [];
    const maxVisiblePages = 5;
    const halfVisible = Math.floor(maxVisiblePages / 2);

    let startPage = Math.max(1, currentPage - halfVisible);
    let endPage = Math.min(totalPages, currentPage + halfVisible);

    // Adjust if we're near the beginning or end
    if (endPage - startPage < maxVisiblePages - 1) {
      if (startPage === 1) {
        endPage = Math.min(totalPages, maxVisiblePages);
      } else {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
      }
    }

    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }

    return pages;
  };

  return (
    <div className="p-6">
      {/* Breadcrumb */}
      <div className="mb-6">
        <div className="flex items-center text-sm text-gray-600 mb-4">
          <span>Admin Panel</span>
          <span className="mx-2">/</span>
          <span>Users</span>
        </div>
        <div className='flex justify-between'>
          <h2 className="text-lg font-medium text-gray-900">Users List</h2>
          <Button
            variant="outline"
            className="bg-orange-500 hover:bg-orange-600 text-white"
            disabled={loading}
            onClick={() => navigate('/users/new')}
          >
            <Plus className="w-4 h-4 mr-1" />
            Create new user
          </Button>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800 text-sm">⚠ {error}</p>
          <Button
            onClick={() => refreshUsers()}
            variant="outline"
            className="mt-2 text-red-600 border-red-600 hover:bg-red-50"
            size="sm"
          >
            Retry
          </Button>
        </div>
      )}

      {/* Success Message */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-green-800 text-sm">✅ {success}</p>
        </div>
      )}

      {/* Search Filters */}
      <UserSearchFilters
        filters={filters}
        availableRoles={availableRoles}
        loading={loading}
        onFiltersChange={(field: string, value: string) => updateFilters({ [field]: value })}
        onRefreshUsers={refreshUsers}
        onClearFilters={clearFilters}
      />

      {/* Users Table */}
      {loading ? (
        <div className="text-center py-12">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          <p className="text-gray-600 text-sm mt-2">Loading users...</p>
        </div>
      ) : users.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-red-500 text-sm">No data found</p>
        </div>
      ) : (
        <div className="bg-white border border-gray-200 rounded-lg">
          <table className="w-full table-fixed">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="w-[5%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  #
                </th>
                <th className="w-[20%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider overflow-hidden text-ellipsis">
                  Name
                </th>
                <th className="w-[15%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider overflow-hidden text-ellipsis">
                  Job title
                </th>
                <th className="w-[20%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider overflow-hidden text-ellipsis">
                  Email
                </th>
                <th className="w-[10%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider overflow-hidden text-ellipsis">
                  Role
                </th>
                <th className="w-[10%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="w-[15%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created Date
                </th>
                <th className="w-[10%] px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {users.map((user, index) => (
                <tr key={user.id} className="hover:bg-gray-50">
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    {(currentPage - 1) * pageSize + index + 1}
                  </td>
                  <td
                    className="px-5 py-3 text-sm text-gray-900 cursor-pointer hover:text-blue-600 break-words"
                    onClick={() => handleViewUser(user.id)}
                  >
                    {user.firstName} {user.lastName}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-900 break-words">
                    {user.jobTitle}
                  </td>
                  <td className="px-5 py-3 text-sm text-gray-900 break-all">
                    {user.email}
                  </td>
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    {user.role}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${user.status === 'Active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-red-100 text-red-800'
                      }`}>
                      {user.status}
                    </span>
                  </td>
                  <td className="px-5 py-3 whitespace-nowrap text-sm text-gray-900">
                    {user.createdAt ? new Date(user.createdAt).toLocaleDateString() : 'N/A'}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 relative">
                    <button
                      onClick={() => toggleActionMenu(user.id)}
                      className="p-1 hover:bg-gray-100 rounded"
                      title="More options"
                    >
                      <MoreHorizontal className="w-4 h-4" />
                    </button>

                    {/* Action Dropdown Menu */}
                    {openActionMenu === user.id && (
                      <div ref={actionMenuRef} className="absolute right-0 top-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg z-10 min-w-32">

                        {/* View User */}
                        <button
                          onClick={() => {
                            handleViewUser(user.id);
                            setOpenActionMenu(null);
                          }}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Eye className="w-4 h-4 mr-2 text-blue-600" />
                          View Info
                        </button>

                        {/* Edit User */}
                        <button
                          onClick={() => handleEditUser(user.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Edit className="w-4 h-4 mr-2 text-green-600" />
                          Edit
                        </button>

                        {/* Toggle Status */}
                        <button
                          onClick={() => handleToggleStatus(user.id)}
                          className="flex items-center px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 w-full text-left"
                        >
                          <Shield className="w-4 h-4 mr-2 text-orange-600" />
                          {user.status === 'Active' ? 'Deactivate' : 'Activate'}
                        </button>

                        <hr className="my-1" />

                        <button
                          onClick={() => handleDeleteUser(user.id)}
                          className="flex items-center px-3 py-2 text-sm text-red-600 hover:bg-red-50 w-full text-left"
                        >
                          <Trash2 className="w-4 h-4 mr-2" />
                          Delete
                        </button>
                      </div>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          <div className="bg-white px-6 py-3 border-t border-gray-200 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-700">Rows per page:</span>
              <select
                className="border border-gray-300 rounded px-2 py-1 text-sm"
                value={pageSize}
                onChange={(e) => changePageSize(parseInt(e.target.value))}
              >
                <option value={10}>10</option>
                <option value={25}>25</option>
                <option value={50}>50</option>
              </select>
              <span className="text-sm text-gray-700">of {totalUsers} rows</span>
            </div>

            <div className="flex items-center space-x-2">
              <button
                className={`p-1 ${currentPage === 1 ? 'text-gray-300 cursor-not-allowed' : 'text-gray-400 hover:text-gray-600 cursor-pointer'}`}
                onClick={goToPrevPage}
                disabled={currentPage === 1}
                title="Previous page"
              >
                ‹
              </button>

              {generatePageNumbers().map(pageNum => (
                <button
                  key={pageNum}
                  className={`w-8 h-8 rounded-full flex items-center justify-center text-sm ${pageNum === currentPage
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100'
                    }`}
                  onClick={() => goToPage(pageNum)}
                >
                  {pageNum}
                </button>
              ))}

              <button
                className={`p-1 ${currentPage === totalPages ? 'text-gray-300 cursor-not-allowed' : 'text-gray-400 hover:text-gray-600 cursor-pointer'}`}
                onClick={goToNextPage}
                disabled={currentPage === totalPages}
                title="Next page"
              >
                ›
              </button>
            </div>
          </div>
        </div>
      )}

      {/* User Detail Modal */}
      <UserDetailModal
        isOpen={userDetailModal.isOpen}
        user={userDetailModal.user}
        onClose={() => setUserDetailModal({ isOpen: false, user: null })}
      />
    </div>
  );
};