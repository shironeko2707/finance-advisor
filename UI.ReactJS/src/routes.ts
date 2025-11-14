import React from 'react';
import { Dashboard } from './pages/admin/Dashboard.tsx';
import { ReportsList } from './pages/admin/ReportsManagement/ReportsList.tsx';
import { CreateReport } from './pages/admin/ReportsManagement/CreateReport.tsx';
import { FilesList } from './pages/admin/FilesManagement/FilesList.tsx';
import { TemplateList } from './pages/admin/TemplateManagement/TemplateList.tsx';
import { TemplateForm } from './pages/admin/TemplateManagement/TemplateForm.tsx';
import { UserList } from './pages/admin/UserManagement/UserList.tsx';
import { UserForm } from './pages/admin/UserManagement/UserForm.tsx';

export interface RouteConfig {
  path: string;
  component: React.ComponentType;
  menu: string;
  exact?: boolean;
  role: "User" | "Admin";
}

export const routes: RouteConfig[] = [
  // Dashboard routes
  {
    path: '/dashboard',
    component: Dashboard,
    menu: 'dashboard',
    exact: true,
    role: "User"
  },

  // Template routes
  {
    path: '/templates/:id/edit',
    component: TemplateForm,
    menu: 'templates',
    exact: false,
    role: "User"
  },
  {
    path: '/templates',
    component: TemplateList,
    menu: 'templates',
    exact: true,
    role: "User"
  },

  // User routes
  {
    path: '/users/new',
    component: UserForm,
    menu: 'users',
    exact: true,
    role: "Admin"
  },
  {
    path: '/users/:id/edit',
    component: UserForm,
    menu: 'users',
    exact: false,
    role: "Admin"
  },
  {
    path: '/users',
    component: UserList,
    menu: 'users',
    exact: true,
    role: "Admin"
  },

  // Reports routes
  {
    path: '/reports/new',
    component: CreateReport,
    menu: 'reports',
    exact: true,
    role: "User"
  },
  {
    path: '/reports',
    component: ReportsList,
    menu: 'reports',
    exact: true,
    role: "User"
  },

  // Files routes
  {
    path: '/files',
    component: FilesList,
    menu: 'files',
    exact: true,
    role: "User"
  }
];

// Menu mapping for navigation
export const menuRouteMap: { [key: string]: string } = {
  'dashboard': '/dashboard',
  'templates': '/templates',
  'users': '/users',
  'reports': '/reports',
  'files': '/files'
};

// Helper function to match route patterns
export const matchRoute = (pathname: string, routePath: string, exact: boolean = true): boolean => {
  if (exact) {
    return pathname === routePath;
  }
  
  // Convert route pattern to regex (e.g., /users/:id -> /^\/users\/\d+$/)
  const pattern = routePath
    .replace(/:\w+/g, '\\d+') // Replace :id with \d+ for numeric IDs
    .replace(/\//g, '\\/');   // Escape forward slashes
  
  const regex = new RegExp(`^${pattern}$`);
  return regex.test(pathname);
};

// Function to find matching route for current path
export const findMatchingRoute = (pathname: string, activeMenu: string): RouteConfig | null => {
  // Filter routes by active menu first
  const menuRoutes = routes.filter(route => route.menu === activeMenu);
  
  // Sort routes by specificity (more specific routes first)
  // Routes with exact match and longer paths should be checked first
  const sortedRoutes = menuRoutes.sort((a, b) => {
    if (a.exact && !b.exact) return -1;
    if (!a.exact && b.exact) return 1;
    return b.path.length - a.path.length;
  });

  // Find first matching route
  for (const route of sortedRoutes) {
    if (matchRoute(pathname, route.path, route.exact)) {
      return route;
    }
  }

  return null;
};

// Get all unique admin route paths for App.tsx routing
// export const getAdminRoutePaths = (): string[] => {
//   return Array.from(new Set(adminRoutes.map(route => route.path)));
// };

// Check if a path is an admin route
// export const isAdminRoute = (path: string): boolean => {
//   return adminRoutes.some(route => {
//     if (route.exact) {
//       return path === route.path;
//     }
//     // For non-exact routes, check if it matches the pattern
//     return matchRoute(path, route.path, route.exact);
//   });
// };

// Helper component for generating React Router routes
// export const generateAdminRoutes = (layoutComponent: React.ComponentType) => {
//   return getAdminRoutePaths().map((routePath) => ({
//     path: routePath,
//     element: React.createElement(layoutComponent)
//   }));
// };
