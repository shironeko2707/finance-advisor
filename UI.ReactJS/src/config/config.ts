// Application configuration

export interface AppConfig {
  API_BASE_URL: string;
  AUTH_BASE_URL: string;
  FILE_BASE_URL: string;
  USE_MOCK_AUTH: boolean;
  MOCK_ADMIN_TOKEN: string;
}

// Configuration based on environment
function createConfig(): AppConfig {
  // Base configuration that can be overridden by environment variables
  return {
    API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'http://10.22.14.6:8080',
    AUTH_BASE_URL: import.meta.env.VITE_AUTH_BASE_URL || 'http://10.22.14.6:8080',
    FILE_BASE_URL: import.meta.env.VITE_FILE_BASE_URL || 'http://10.22.14.6:8088',
    USE_MOCK_AUTH: import.meta.env.VITE_USE_MOCK_AUTH === 'true',
    MOCK_ADMIN_TOKEN: 'M0ck_token_of_the_$uper_4dm!N'
  };
}

// Export the configuration
export const config = createConfig();

// Helper functions for easy access
export const getApiBaseUrl = (): string => config.API_BASE_URL;
export const getAuthBaseUrl = (): string => config.AUTH_BASE_URL;
export const getFileBaseUrl = (): string => config.FILE_BASE_URL;
export const shouldUseMockAuth = (): boolean => config.USE_MOCK_AUTH;
export const getMockAdminToken = (): string => config.MOCK_ADMIN_TOKEN;

// Development configuration for feature flags
export const devConfig = {
  // Local development flags - can be overridden per component
  USE_FIXTURE: false,
  USER_MANAGEMENT_USE_FIXTURE: false,
  TEMPLATE_MANAGEMENT_USE_FIXTURE: false,
  REPORTS_MANAGEMENT_USE_FIXTURE: false,
  FILES_MANAGEMENT_USE_FIXTURE: false,
  
  // Global flags
  API_BASE_URL: import.meta.env.VITE_API_BASE_URL || 'https://lengkeng-api-dev.hocai.fun',
  AUTH_BASE_URL: import.meta.env.VITE_AUTH_BASE_URL || 'https://lengkeng-api-dev.hocai.fun',

  // Feature flags for different development scenarios
  ENABLE_DEBUG_PANEL: import.meta.env.DEV,
} as const;

// Helper to check if we should use fixtures for a specific feature
export const shouldUseFixture = (feature: keyof typeof devConfig, localOverride?: boolean): boolean => {
  // Local override has highest priority
  if (localOverride !== undefined) {
    return localOverride;
  }
  
  // Fall back to feature-specific config
  const featureFlag = devConfig[feature];
  return typeof featureFlag === 'boolean' ? featureFlag : false;
};
