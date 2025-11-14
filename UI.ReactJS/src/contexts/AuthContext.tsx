import { jwtDecode } from 'jwt-decode';
import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { apiService } from '@/services/ApiInterceptor.ts';
import { shouldUseMockAuth, getMockAdminToken } from '@/config/config';
import type { LoginResponse } from '@/types/api';

interface User {
  id: string;
  email: string;
  name: string;
  role?: string;
  token?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;

  logout: () => void;
  isLoading: boolean;
  sendOtp: (email: string) => Promise<{ success: boolean; message?: string }>;
  verifyOtp: (email: string, otp: string) => Promise<{ success: boolean; reset_token?: string }>;
  resetPassword: (password: string, repassword: string, reset_token: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Toggle to use mock auth data instead of calling real API.
  // Default: false (use real API). To use mock set VITE_USE_MOCK_AUTH=true in your Vite env.
  // Example (in .env.local): VITE_USE_MOCK_AUTH=true
  const flagMockData = shouldUseMockAuth();

  // Initialize user state from localStorage or API
  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const tokenExpiry = localStorage.getItem('token_expiry');

    if (storedUser && tokenExpiry) {
      const expiryTime = parseInt(tokenExpiry, 10);
      if (new Date().getTime() < expiryTime) {
        setUser(JSON.parse(storedUser));
      } else {
        logout();
      }
    }
    setIsLoading(false);
  }, []);

  /**
   * Login function — demo authentication helper.
   *
   * Attempts to sign in a user with the provided email and password. This
   * implementation simulates an API call with a 1 second delay and accepts only
   * the hard-coded demo credentials:
   *   - email: 'admin@mail.com'
   *   - password: 'passwd'
   *
   * On success the function will:
   *   - set the `user` state (memory)
   *   - persist the user object to localStorage under the key 'user',
   *   - set `isLoading` to false and resolve to `true`.
   * On failure it sets `isLoading` to false and resolves to `false`.
   *
   * Example usage:
   * ```ts
   * const { login } = useAuth();
   * const handleLogin = async () => {
   *   const success = await login('admin@mail.com', 'passwd');
   *   if (success) {
   *     // redirect to dashboard or update UI
   *   } else {
   *     // show error message
   *   }
   * };
   * ```
   *
   * @param emailOrUsername - user's email address
   * @param password - user's password (plain-text for demo only)
   * @returns Promise<boolean> resolves `true` when credentials match demo user
   */
  const login = async (emailOrUsername: string, password: string): Promise<{ success: boolean; error?: string }> => {
    setIsLoading(true);

    // Ensure parameters are strings and strip spaces to prevent circular reference errors
    const cleanEmailOrUsername = String(emailOrUsername || '').trim();
    const cleanPassword = String(password || '').trim();

    console.log(flagMockData)
    // If flagMockData is true use the existing mock behaviour
    if (flagMockData) {
      // Simulate API call
      return new Promise((resolve) => {
        setTimeout(() => {
          // Simple validation - in real app, this would be an API call
          if (cleanEmailOrUsername === 'mock_admin' && cleanPassword === 'M0ck_token_of_the_$uper_4dm!N') {
            const userData = {
              id: '999999999',
              email: cleanEmailOrUsername,
              name: 'Mock Admin'
            };

            // Set the mock admin token in localStorage for API calls
            const mockToken = getMockAdminToken();
            localStorage.setItem('access_token', mockToken);

            // Set token expiry (24 hours from now)
            const expiryTime = new Date().getTime() + 24 * 60 * 60 * 1000;
            localStorage.setItem('token_expiry', expiryTime.toString());

            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
            setIsLoading(false);
            resolve({ success: true });
          } else {
            setIsLoading(false);
            resolve({ success: false, error: 'Invalid email or password' });
          }
        }, 1000);
      });
    }

    // Otherwise call real API
    try {
      const data: LoginResponse = await apiService.auth.login(cleanEmailOrUsername, cleanPassword);

      // Parse expected auth response shape if present
      // Example response:
      // {
      //   access_token, token_type, expires_in, user_id, username, role
      // }
      const token = data.access_token || data.token || '';
      const userId = String(data.user_id || data.id || data.user?.id || '0');
      const username = data.username || data.user?.username || data.user?.email || cleanEmailOrUsername;
      const role = data.role || data.user?.role || undefined;

      const userData: User = {
        id: userId,
        email: cleanEmailOrUsername,
        name: username,
        role,
        token
      };

      setUser(userData);
      // Persist both token and user for later API calls
      localStorage.setItem('user', JSON.stringify(userData));
      if (token) {
        const decodedToken: { exp: number } = jwtDecode(token);
        const expiryTime = decodedToken.exp * 1000;
        localStorage.setItem('access_token', token);
        localStorage.setItem('token_expiry', expiryTime.toString());
      }

      setIsLoading(false);
      return { success: true };
    } catch (err) {
      console.error('Login error:', err);
      let errorMessage = 'Login failed. Please try again later.';

      // Extract the specific error message from the server response
      if (err instanceof Error) {
        errorMessage = err.message;
        console.error('Error message:', err.message);
        console.error('Error stack:', err.stack);
      } else {
        console.error('Unknown error type:', typeof err, err);
      }

      setIsLoading(false);
      return { success: false, error: errorMessage };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_expiry');
  };

  const sendOtp = async (email: string): Promise<{ success: boolean; message?: string }> => {
    setIsLoading(true);
    const res = await apiService.auth.forgotPassword(email);
    setIsLoading(false);
    return res;
  };

  const verifyOtp = async (email: string, otp: string): Promise<{ success: boolean; reset_token?: string; }> => {
    setIsLoading(true);
    try {
      const response = await apiService.auth.verifyOtp(email, otp);
      setIsLoading(false);
      if (response.success) {
        return { success: true, reset_token: response.reset_token };
      }
      return { success: false };
    } catch (error) {
      console.error('Verify OTP error:', error);
      setIsLoading(false);
      return { success: false };
    }
  };

  const resetPassword = async (password: string, repassword: string, reset_token: string): Promise<boolean> => {
    setIsLoading(true);
    try {
      await apiService.auth.resetPassword(password, repassword, reset_token);
      setIsLoading(false);
      return true;
    } catch (error) {
      console.error('Reset password error:', error);
      setIsLoading(false);
      return false;
    }
  };

  const value = {
    user,
    login,
    logout,
    isLoading,
    sendOtp,
    verifyOtp,
    resetPassword
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
