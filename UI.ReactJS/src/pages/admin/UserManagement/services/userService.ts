import type { User, UserApiResponseSnake, UserRequest } from '../types/user';
import { apiService } from '@/services/ApiInterceptor.ts';

// Type for API request payload (snake_case)
type UserApiRequest = {
  username: string;
  first_name: string;
  last_name: string;
  job_title: string;
  email: string;
  password?: string;
  role: string;
  status: string;
};

// Utility function to map API response (snake_case) to UI format (camelCase)
const mapApiResponseToUser = (apiUser: UserApiResponseSnake): User => {
  return {
    id: apiUser.id,
    username: apiUser.username,
    firstName: apiUser.first_name,
    lastName: apiUser.last_name,
    jobTitle: apiUser.job_title,
    email: apiUser.email,
    role: apiUser.role,
    status: apiUser.status,
    createdAt: apiUser.created_at,
    createdDate: apiUser.created_at ? new Date(apiUser.created_at).toLocaleDateString() : undefined
  };
};

// Utility function to map UI format (camelCase) to API request (snake_case)
const mapUserToApiRequest = (user: Partial<UserRequest>): Partial<UserApiRequest> => {
  const apiRequest: Partial<UserApiRequest> = {};

  if (user.username !== undefined) apiRequest.username = user.username;
  if (user.firstName !== undefined) apiRequest.first_name = user.firstName;
  if (user.lastName !== undefined) apiRequest.last_name = user.lastName;
  if (user.jobTitle !== undefined) apiRequest.job_title = user.jobTitle;
  if (user.email !== undefined) apiRequest.email = user.email;
  if (user.password !== undefined) apiRequest.password = user.password;
  if (user.role !== undefined) apiRequest.role = user.role;
  if (user.status !== undefined) apiRequest.status = user.status;

  return apiRequest;
};

// User API service - Handles real API calls with field mapping
export class UserService {
  // Get all users
  static async getUsers(): Promise<User[]> {
    try {
      const response = await apiService.request<UserApiResponseSnake[]>(
        apiService.getApiUrl('/users'),
        {
          method: 'GET',
        }
      );
      return response.map(mapApiResponseToUser);
    } catch (error) {
      console.error('Error fetching users:', error);
      // Re-throw the original error to preserve detailed API error messages
      throw error;
    }
  }

  // Get user by ID
  static async getUserById(id: string): Promise<User | null> {
    try {
      const response = await apiService.request<UserApiResponseSnake>(
        apiService.getApiUrl(`/users/${id}`),
        {
          method: 'GET',
        }
      );
      return mapApiResponseToUser(response);
    } catch (error) {
      if (error instanceof Error && error.message.includes('404')) {
        return null;
      }
      console.error('Error fetching user:', error);
      // Re-throw the original error to preserve detailed API error messages
      throw error;
    }
  }

  // Create new user
  static async createUser(userData: UserRequest): Promise<User> {
    try {
      const apiRequest = mapUserToApiRequest(userData);
      const response = await apiService.request<UserApiResponseSnake>(
        apiService.getApiUrl('/users'),
        {
          method: 'POST',
          body: JSON.stringify(apiRequest),
        }
      );
      return mapApiResponseToUser(response);
    } catch (error) {
      console.error('Error creating user:', error);
      // Re-throw the original error to preserve detailed API error messages
      throw error;
    }
  }

  // Update existing user
  static async updateUser(id: string, userData: Partial<UserRequest>): Promise<User> {
    try {
      const apiRequest = mapUserToApiRequest(userData);
      // Remove password from update request if it's empty
      if (!apiRequest.password) {
        delete apiRequest.password;
      }

      const response = await apiService.request<UserApiResponseSnake>(
        apiService.getApiUrl(`/users/${id}`),
        {
          method: 'PUT',
          body: JSON.stringify(apiRequest),
        }
      );
      return mapApiResponseToUser(response);
    } catch (error) {
      console.error('Error updating user:', error);
      // Re-throw the original error to preserve detailed API error messages
      throw error;
    }
  }

  // Delete user
  static async deleteUser(id: string): Promise<void> {
    try {
      await apiService.request(
        apiService.getApiUrl(`/users/${id}`),
        {
          method: 'DELETE',
        }
      );
    } catch (error) {
      console.error('Error deleting user:', error);
      // Re-throw the original error to preserve detailed API error messages
      throw error;
    }
  }

  // Toggle user status
  static async toggleUserStatus(id: string): Promise<User> {
    try {
      const response = await apiService.request<UserApiResponseSnake>(
        apiService.getApiUrl(`/users/${id}/toggle-status`),
        {
          method: 'PATCH',
        }
      );
      return mapApiResponseToUser(response);
    } catch (error) {
      console.error('Error toggling user status:', error);
      // Re-throw the original error to preserve detailed API error messages
      throw error;
    }
  }
}
