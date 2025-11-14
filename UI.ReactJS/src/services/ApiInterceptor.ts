import { getApiBaseUrl, getAuthBaseUrl } from '@/config/config';
import type {
  LoginResponse,
  OtpResponse,
  ResetPasswordResponse,
  UploadWithTemplateSyncResponse
} from '@/types/api';
import type { Template } from '@/pages/admin/TemplateManagement/types/template';

export class ApiInterceptor {
  private static instance: ApiInterceptor;

  private constructor() { }

  public static getInstance(): ApiInterceptor {
    if (!ApiInterceptor.instance) {
      ApiInterceptor.instance = new ApiInterceptor();
    }
    return ApiInterceptor.instance;
  }

  /**
   * Get the base URL for the main API
   */
  public getBaseUrl(): string {
    return getApiBaseUrl();
  }

  /**
   * Get the base URL for auth API
   */
  public getAuthBaseUrl(): string {
    return getAuthBaseUrl();
  }

  /**
   * Build full URL for auth endpoints
   */
  public getAuthUrl(endpoint: string): string {
    const baseUrl = this.getAuthBaseUrl();
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${baseUrl}${cleanEndpoint}`;
  }

  /**
   * Build full URL for main API endpoints
   */
  public getApiUrl(endpoint: string): string {
    const baseUrl = this.getBaseUrl();
    const cleanEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    return `${baseUrl}${cleanEndpoint}`;
  }

  /**
   * Get file upload headers (without Content-Type for multipart/form-data)
   */
  public getFileUploadHeaders(includeAuth: boolean = true): HeadersInit {
    const headers: HeadersInit = {};

    if (includeAuth) {
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }
  public getHeaders(includeAuth: boolean = false): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (includeAuth) {
      const token = localStorage.getItem('access_token');
      if (token) {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  /**
   * Generic fetch wrapper with error handling
   */
  public async request<T>(
    url: string,
    options: RequestInit = {}
  ): Promise<T> {
    const defaultOptions: RequestInit = {
      headers: this.getHeaders(true),
      ...options,
    };

    try {
      const response = await fetch(url, defaultOptions);

      if (!response.ok) {
        // Try to get detailed error message from response body
        let errorMessage = `HTTP ${response.status}: ${response.statusText}`;

        try {
          const errorData = await response.json();
          if (errorData.detail[0].msg) {
            const fieldError = errorData.detail[0].loc[1];
            errorMessage = fieldError + ': ' + errorData.detail[0].msg; // first error only
          } else if (errorData.detail) {
            errorMessage = errorData.detail;
          } else if (errorData.message) {
            errorMessage = errorData.message;
          } else if (errorData.error.msg) {
            errorMessage = errorData.error.msg;
          } else if (errorData.error) {
            errorMessage = errorData.error;
          }
        } catch (parseError) {
          // If we can't parse the error response, use the status text
          console.warn('Could not parse error response:', parseError);
        }

        throw new Error(errorMessage);
      }

      // Handle 204 No Content - don't try to parse JSON
      if (response.status === 204) {
        return undefined as T;
      }

      // Check if response has content before trying to parse JSON
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }

      // If no JSON content type, return undefined
      return undefined as T;
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  /**
   * Auth API methods
   */
  public auth = {
    login: (username: string, password: string): Promise<LoginResponse> =>
      this.request(this.getAuthUrl('/auth/login'), {
        method: 'POST',
        headers: this.getHeaders(false),
        body: JSON.stringify({ username, password })
      }),

    sendOtp: (email: string): Promise<OtpResponse> =>
      this.request(this.getAuthUrl('/auth/send-otp'), {
        method: 'POST',
        headers: this.getHeaders(false),
        body: JSON.stringify({ email })
      }),

    forgotPassword: (email: string): Promise<{ success: boolean; message?: string }> =>
      this.request(this.getAuthUrl('/auth/forgot-password'), {
        method: 'POST',
        headers: this.getHeaders(false),
        body: JSON.stringify({ email })
      }),

    verifyOtp: (email: string, otp_code: string): Promise<OtpResponse> =>
      this.request(this.getAuthUrl('/auth/validate-otp'), {
        method: 'POST',
        headers: this.getHeaders(false),
        body: JSON.stringify({ email, otp_code })
      }),

    resetPassword: (password: string, repassword: string, reset_token: string): Promise<ResetPasswordResponse> =>
      this.request(this.getAuthUrl('/auth/reset-password'), {
        method: 'POST',
        headers: this.getHeaders(false),
        body: JSON.stringify({ password, repassword, reset_token })
      })
  };

  /**
   * Main API methods
   */
  public api = {
    // Reports endpoints
    getReports: () => this.request(this.getApiUrl('/reports')),
    deleteReport: (reportId: number) => this.request(this.getApiUrl(`/reports/${reportId}`), {
      method: 'DELETE'
    }),
    downloadReport: (reportId: number): Promise<Blob> => {
      // For file downloads, we need to handle the response differently
      const url = this.getApiUrl(`/reports/${reportId}/download`);
      return fetch(url, {
        headers: this.getHeaders(true)
      }).then(async (fileResponse) => {
        if (!fileResponse.ok) {
          throw new Error(`Download failed: ${fileResponse.statusText}`);
        }

        return fileResponse.blob();
      });
    },

    // Get PDF content for viewing
    getPdfReport: (reportId: number): Promise<Blob> => {
      const url = this.getApiUrl(`/reports/${reportId}/pdf`);
      return fetch(url, {
        headers: this.getHeaders(true)
      }).then(async (fileResponse) => {
        if (!fileResponse.ok) {
          throw new Error(`PDF fetch failed: ${fileResponse.statusText}`);
        }

        return fileResponse.blob();
      });
    },

    downloadFile: (fileId: number): Promise<Blob> => {
      // For file downloads, we need to handle the response differently
      const url = this.getApiUrl(`/files/${fileId}/download`);
      return fetch(url, {
        headers: this.getHeaders(true)
      }).then(async (fileResponse) => {
        if (!fileResponse.ok) {
          throw new Error(`Download failed: ${fileResponse.statusText}`);
        }

        return fileResponse.blob();
      });
    },

    /**
     * Upload files with template synchronously
     */
    uploadWithTemplateSync: async (
      reportName: string,
      templateId?: string,
      templateFile?: File,
      file_ids?: number[],
      inputFiles?: File[],
    ): Promise<UploadWithTemplateSyncResponse> => {
      const formData = new FormData();

      // Add report name
      formData.append('report_name', reportName);
      // Ensure templateId is a string and only append if valid
      if (templateId) {
        formData.append('template_id', String(templateId));
      }

      // Handle file_ids array: append each ID individually for robust multi-value handling
      if (Array.isArray(file_ids) && file_ids.length > 0) {
        file_ids.forEach(id => {
          formData.append('file_ids', String(id));
        });
      } else if (file_ids) {
        // Fallback for single fileId or non-array but truthy value
        formData.append('file_ids', String(file_ids));
      }

      // Add template file
      if (templateFile) { formData.append('template', templateFile) };

      // Add input files
      if (inputFiles) {
        inputFiles.forEach(file => {
          formData.append('files', file);
        });
      }

      const url = this.getApiUrl('/files/upload/with-template-sync2');

      try {
        const response = await fetch(url, {
          method: 'POST',
          headers: this.getFileUploadHeaders(true),
          body: formData
        });

        if (!response.ok) {
          // Try to get detailed error message from response body
          let errorMessage = `Upload failed: ${response.statusText}`;

          try {
            const errorData = await response.json();
            if (errorData.detail && Array.isArray(errorData.detail) && errorData.detail[0]?.msg) {
              const fieldError = errorData.detail[0].loc?.[1];
              errorMessage = fieldError ? `${fieldError}: ${errorData.detail[0].msg}` : errorData.detail[0].msg;
            } else if (errorData.detail) {
              errorMessage = errorData.detail;
            } else if (errorData.message) {
              errorMessage = errorData.message;
            } else if (errorData.error?.msg) {
              errorMessage = errorData.error.msg;
            } else if (errorData.error) {
              errorMessage = errorData.error;
            }
          } catch (parseError) {
            // If we can't parse the error response, use the status text
            console.warn('Could not parse error response:', parseError);
          }

          throw new Error(errorMessage);
        }

        return await response.json();
      } catch (error) {
        console.error('File upload with template sync failed:', error);
        throw error;
      }
    },
    // Templates Endpoint
    getTemplates: (): Promise<{ templates: Template[] }> => this.request(this.getApiUrl('/templates')),

    getTemplate: (templateId: number) => this.request(this.getApiUrl(`/templates/${templateId}`)),

    createTemplate: (templateData: any) => this.request(this.getApiUrl('/templates'), {
      method: 'POST',
      body: JSON.stringify(templateData)
    }),

    updateTemplate: (templateId: number, templateData: any) => this.request(this.getApiUrl(`/templates/${templateId}`), {
      method: 'PUT',
      body: JSON.stringify(templateData)
    }),

    deleteTemplate: (templateId: number) => this.request(this.getApiUrl(`/templates/${templateId}`), {
      method: 'DELETE'
    }),

    downloadTemplate: (templateId: number): Promise<Blob> => {
      const url = this.getApiUrl(`/templates/${templateId}/download`);
      return fetch(url, {
        headers: this.getHeaders(true)
      }).then(async (fileResponse) => {
        if (!fileResponse.ok) {
          throw new Error(`Download failed: ${fileResponse.statusText}`);
        }
        return fileResponse.blob();
      });
    },

    uploadTemplate: (formData: FormData) => {
      const url = this.getApiUrl('/templates/upload');
      return fetch(url, {
        method: 'POST',
        headers: this.getFileUploadHeaders(true),
        body: formData
      }).then(response => {
        if (!response.ok) {
          throw new Error(`Upload failed: ${response.statusText}`);
        }
        return response.json();
      });
    }
  };
}

export const apiService = ApiInterceptor.getInstance();
