// User interface for API mapping and view
export interface User {
  id: string;
  username: string;
  firstName: string;
  lastName: string;
  jobTitle: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  createdDate?: string;
  createdAt?: string;
}

// User role type
export type UserRole = 'Admin'  | 'User';

// User status type
export type UserStatus = 'Active' | 'Inactive';

// API response format (snake_case from backend)
export interface UserApiResponseSnake {
  id: string;
  username: string;
  last_name: string;
  first_name: string;
  job_title: string;
  email: string;
  role: 'Admin' | 'User';
  status: 'Active' | 'Inactive';
  created_at?: string;
  updated_at?: string;
}

// User create/update request interface
export interface UserRequest {
  username: string;
  firstName: string;
  lastName: string;
  jobTitle: string;
  email: string;
  password: string;
  role: UserRole;
  status?: UserStatus;
}

// User search/filter interface
export interface UserFilter {
  searchTerm?: string;
  role?: UserRole;
  status?: UserStatus;
}

// User profile update interface
export interface UserProfileUpdate {
  firstName?: string;
  lastName?: string;
  jobTitle?: string;
  email?: string;
}
