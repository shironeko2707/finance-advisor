// Mock data fixtures for development and testing
import type { User, UserRole, UserStatus } from '../types';

// User mock data
export const mockUsers: User[] = [
  {
    id: '1',
    username: 'jasonlove',
    firstName: 'Jason',
    lastName: 'Derulo',
    jobTitle: 'Investment Director',
    email: 'jasonlove@khengleong.co',
    role: 'Admin',
    status: 'Active'
  },
  {
    id: '2',
    username: 'ashley.do',
    firstName: 'Ashley',
    lastName: 'Do',
    jobTitle: 'Investment Analyst',
    email: 'ashley@khengleong.co',
    role: 'User',
    status: 'Active'
  },
  {
    id: '3',
    username: 'lily.aldrin',
    firstName: 'Lily',
    lastName: 'Aldrin',
    jobTitle: 'Investment Analyst',
    email: 'lily@khengleong.co',
    role: 'User',
    status: 'Inactive'
  },
  {
    id: '4',
    username: 'john.smith',
    firstName: 'John',
    lastName: 'Smith',
    jobTitle: 'Senior Analyst',
    email: 'john.smith@khengleong.co',
    role: 'User',
    status: 'Active'
  },
  {
    id: '5',
    username: 'sarah.johnson',
    firstName: 'Sarah',
    lastName: 'Johnson',
    jobTitle: 'Portfolio Manager',
    email: 'sarah.johnson@khengleong.co',
    role: 'Admin',
    status: 'Active'
  },
  {
    id: '6',
    username: 'michael.brown',
    firstName: 'Michael',
    lastName: 'Brown',
    jobTitle: 'Risk Analyst',
    email: 'michael.brown@khengleong.co',
    role: 'User',
    status: 'Active'
  },
  {
    id: '7',
    username: 'emily.davis',
    firstName: 'Emily',
    lastName: 'Davis',
    jobTitle: 'Research Associate',
    email: 'emily.davis@khengleong.co',
    role: 'User',
    status: 'Active'
  },
  {
    id: '8',
    username: 'david.wilson',
    firstName: 'David',
    lastName: 'Wilson',
    jobTitle: 'Investment Manager',
    email: 'david.wilson@khengleong.co',
    role: 'Admin',
    status: 'Active'
  },
  {
    id: '9',
    username: 'jennifer.taylor',
    firstName: 'Jennifer',
    lastName: 'Taylor',
    jobTitle: 'Financial Analyst',
    email: 'jennifer.taylor@khengleong.co',
    role: 'User',
    status: 'Inactive'
  },
  {
    id: '10',
    username: 'robert.anderson',
    firstName: 'Robert',
    lastName: 'Anderson',
    jobTitle: 'Senior Portfolio Manager',
    email: 'robert.anderson@khengleong.co',
    role: 'Admin',
    status: 'Active'
  },
  {
    id: '11',
    username: 'lisa.martinez',
    firstName: 'Lisa',
    lastName: 'Martinez',
    jobTitle: 'Investment Associate',
    email: 'lisa.martinez@khengleong.co',
    role: 'User',
    status: 'Active'
  },
  {
    id: '12',
    username: 'james.garcia',
    firstName: 'James',
    lastName: 'Garcia',
    jobTitle: 'Quantitative Analyst',
    email: 'james.garcia@khengleong.co',
    role: 'User',
    status: 'Active'
  },
  {
    id: '13',
    username: 'amanda.rodriguez',
    firstName: 'Amanda',
    lastName: 'Rodriguez',
    jobTitle: 'Compliance Officer',
    email: 'amanda.rodriguez@khengleong.co',
    role: 'User',
    status: 'Active'
  },
  {
    id: '14',
    username: 'kevin.lee',
    firstName: 'Kevin',
    lastName: 'Lee',
    jobTitle: 'Investment Director',
    email: 'kevin.lee@khengleong.co',
    role: 'Admin',
    status: 'Inactive'
  },
  {
    id: '15',
    username: 'michelle.white',
    firstName: 'Michelle',
    lastName: 'White',
    jobTitle: 'Operations Analyst',
    email: 'michelle.white@khengleong.co',
    role: 'User',
    status: 'Active'
  }
];

// Configuration for using fixtures vs real API
import { shouldUseFixture, config } from '@/config/config.ts';

export const appConfig = {
  useFixture: shouldUseFixture('USER_MANAGEMENT_USE_FIXTURE'),
  apiBaseUrl: config.API_BASE_URL
};

// Role data
export const roles: UserRole[] = [
  'Admin',
  'User',
];

// Status options
export const statusOptions: readonly UserStatus[] = [
  'Active',
  'Inactive'
] as const;
