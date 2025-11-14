import type { User, UserRequest } from '../types/user';
import { mockUsers } from './datafix.ts';

// Mock service for development with proper field mapping
export class UserMockService {
  private static users: User[] = [...mockUsers];

  // Simulate API delay
  private static delay(ms: number = 500): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  // Get all users
  static async getUsers(): Promise<User[]> {
    await this.delay();
    return [...this.users];
  }

  // Get user by ID
  static async getUserById(id: string): Promise<User | null> {
    await this.delay();
    return this.users.find(user => user.id === id) || null;
  }

  // Create new user
  static async createUser(userData: UserRequest): Promise<User> {
    await this.delay();
    const newUser: User = {
      id: String(this.users.length + 1),
      username: userData.username,
      firstName: userData.firstName,
      lastName: userData.lastName,
      jobTitle: userData.jobTitle,
      email: userData.email,
      role: userData.role,
      status: userData.status || 'Active',
      createdAt: new Date().toISOString(),
      createdDate: new Date().toLocaleDateString()
    };
    this.users.push(newUser);
    return newUser;
  }

  // Update user
  static async updateUser(id: string, userData: Partial<UserRequest>): Promise<User> {
    await this.delay();
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex === -1) {
      throw new Error('User not found');
    }

    this.users[userIndex] = {
      ...this.users[userIndex],
      ...userData
    };
    return this.users[userIndex];
  }

  // Delete user
  static async deleteUser(id: string): Promise<void> {
    await this.delay();
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex === -1) {
      throw new Error('User not found');
    }
    this.users.splice(userIndex, 1);
  }

  // Toggle user status
  static async toggleUserStatus(id: string): Promise<User> {
    await this.delay();
    const userIndex = this.users.findIndex(user => user.id === id);
    if (userIndex === -1) {
      throw new Error('User not found');
    }

    this.users[userIndex].status = this.users[userIndex].status === 'Active' ? 'Inactive' : 'Active';
    return this.users[userIndex];
  }
}
