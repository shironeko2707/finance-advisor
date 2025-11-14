import React from 'react';
import type { RouteConfig } from './routes.ts';

// Helper function to create a route configuration
export const createRoute = (
  path: string,
  component: React.ComponentType,
  menu: string,
  exact: boolean = true
): RouteConfig => ({
  path,
  component,
  menu,
  exact
});

// Helper function to create menu route mapping
export const createMenuRoute = (menu: string, path: string) => ({
  [menu]: path
});

// Type-safe route creation helpers
export const RouteBuilder = {
  dashboard: (component: React.ComponentType) => 
    createRoute('/dashboard', component, 'dashboard'),
  
  template: {
    list: (component: React.ComponentType) => 
      createRoute('/templates', component, 'templates'),
    new: (component: React.ComponentType) => 
      createRoute('/templates/new', component, 'templates'),
    detail: (component: React.ComponentType) => 
      createRoute('/templates/:id', component, 'templates', false)
  },
  
  user: {
    list: (component: React.ComponentType) => 
      createRoute('/users', component, 'users'),
    new: (component: React.ComponentType) => 
      createRoute('/users/new', component, 'users'),
    detail: (component: React.ComponentType) => 
      createRoute('/users/:id', component, 'users', false)
  },
  
  reports: (component: React.ComponentType) => 
    createRoute('/reports', component, 'reports'),
  
  files: (component: React.ComponentType) => 
    createRoute('/files', component, 'files')
};

export default RouteBuilder;
