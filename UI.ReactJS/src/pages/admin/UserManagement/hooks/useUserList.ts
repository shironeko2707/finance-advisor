import { useState, useEffect, useMemo } from 'react';
import type { User, UserRole, UserFilter } from '../types/user';
import { UserService } from '../services/userService';
import { UserMockService } from '../services/userMockService';

export interface UseUserListOptions {
  useFixture?: boolean;
  initialPageSize?: number;
}

export interface UseUserListReturn {
  users: User[];
  loading: boolean;
  error: string | null;
  success: string | null;
  currentPage: number;
  totalPages: number;
  pageSize: number;
  totalUsers: number;
  filters: UserFilter;
  availableRoles: UserRole[];
  updateFilters: (newFilters: Partial<UserFilter>) => void;
  clearFilters: () => void;
  goToPage: (page: number) => void;
  goToNextPage: () => void;
  goToPrevPage: () => void;
  changePageSize: (size: number) => void;
  toggleUserStatus: (userId: string) => Promise<void>;
  deleteUser: (userId: string) => Promise<void>;
  refreshUsers: () => Promise<void>;
  clearNotifications: () => void;
}

export const useUserList = (options: UseUserListOptions = {}): UseUserListReturn => {
  const { useFixture = false, initialPageSize = 10 } = options;

  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(initialPageSize);
  const [filters, setFilters] = useState<UserFilter>({});

  // Available roles for filtering, not focus UserRole type
  const availableRoles: UserRole[] = ['Admin', 'User'];

  // Choose service based on useFixture flag
  const userService = useFixture ? UserMockService : UserService;

  // Fetch users from API or mock service
  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const fetchedUsers = await userService.getUsers();
      setUsers(fetchedUsers);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch users');
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  // Filter users based on current filters
  const filteredUsers = useMemo(() => {
    return users.filter(user => {
      const searchTerm = filters.searchTerm?.toLowerCase().trim().replace(/\s+/g, ' ');
      const fullName = `${user.firstName?.toLowerCase()} ${user.lastName?.toLowerCase()}`.trim().replace(/\s+/g, ' ');

      const searchtermMatch = !searchTerm ||
        fullName.includes(searchTerm) ||
        user.jobTitle?.toLowerCase().includes(searchTerm) ||
        user.username?.toLowerCase().includes(searchTerm) ||
        user.email?.toLowerCase().includes(searchTerm);


      const roleMatch = !filters.role || user.role === filters.role;

      const statusMatch = !filters.status || user.status === filters.status;

      return searchtermMatch && roleMatch && statusMatch;
    });
  }, [users, filters]);

  // Paginated users
  const paginatedUsers = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return filteredUsers.slice(startIndex, endIndex);
  }, [filteredUsers, currentPage, pageSize]);

  const totalPages = Math.ceil(filteredUsers.length / pageSize);
  const totalUsers = filteredUsers.length;

  // Filter management
  const updateFilters = (newFilters: Partial<UserFilter>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    setCurrentPage(1); // Reset to first page when filters change
  };

  const clearFilters = () => {
    setFilters({});
    setCurrentPage(1);
  };

  // Pagination management
  const goToPage = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  const goToNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const goToPrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  };

  const changePageSize = (size: number) => {
    setPageSize(size);
    setCurrentPage(1); // Reset to first page when page size changes
  };

  // User actions
  const toggleUserStatus = async (userId: string) => {
    try {
      const updatedUser = await userService.toggleUserStatus(userId);
      setUsers(prev => prev.map(user =>
        user.id === userId ? updatedUser : user
      ));
      setSuccess('User status updated successfully');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to toggle user status');
      console.error('Error toggling user status:', err);
    }
  };

  const deleteUser = async (userId: string) => {
    try {
      await userService.deleteUser(userId);
      setUsers(prev => prev.filter(user => user.id !== userId));
      setSuccess('User deleted successfully');

      // Adjust current page if needed
      const newTotalPages = Math.ceil((totalUsers - 1) / pageSize);
      if (currentPage > newTotalPages && newTotalPages > 0) {
        setCurrentPage(newTotalPages);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete user');
      console.error('Error deleting user:', err);
    }
  };

  const refreshUsers = async () => {
    await fetchUsers();
  };

  const clearNotifications = () => {
    setError(null);
    setSuccess(null);
  };

  // Initial data fetch
  useEffect(() => {
    fetchUsers();
  }, [useFixture]); // Re-fetch when switching between mock and real API

  return {
    users: paginatedUsers,
    loading,
    error,
    success,
    currentPage,
    totalPages,
    pageSize,
    totalUsers,
    filters,
    availableRoles,
    updateFilters,
    clearFilters,
    goToPage,
    goToNextPage,
    goToPrevPage,
    changePageSize,
    toggleUserStatus,
    deleteUser,
    refreshUsers,
    clearNotifications,
  };
};
