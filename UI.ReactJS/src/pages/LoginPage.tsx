import React, { useState } from 'react';
import { Navigate, Link } from 'react-router-dom';
import { Eye, EyeOff } from 'lucide-react';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Card, CardContent } from '@/components/atomic/card.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { useAuth } from '@/contexts/AuthContext.tsx';
import { useInputValidation } from '@/components/hooks/useInputValidation';
import defaultLogo from "@/assets/logo.png";
import cmcLogo from "@/assets/cmc.svg";

// Helper function to get logo URL
const getLogoUrl = (): string => {
  const logoUrl = import.meta.env.VITE_APP_LOGO_URL;
  if (logoUrl) {
    // Check for specific known assets
    if (logoUrl === './assets/cmc.svg' || logoUrl === 'assets/cmc.svg') {
      return cmcLogo;
    }
    // If it's a full URL, return as is
    if (logoUrl.startsWith('http')) {
      return logoUrl;
    }
  }
  return defaultLogo;
};

// Helper function to get company name
const getCompanyName = (): string => {
  return import.meta.env.VITE_APP_COMPANY_NAME || 'Kheng Leong Co';
};

// Helper function to get system name
const getAppName = (): string => {
  return import.meta.env.VITE_APP_APP_NAME || 'Kheng Leong Investment System';
};

export const LoginPage: React.FC = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [error, setError] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const { login, user, isLoading } = useAuth();

  // Use the generic input validation hook
  const { createValidatedFieldOnChange } = useInputValidation();

  // If user is already logged in, redirect to dashboard
  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Ensure we have clean string values
    const cleanEmail = String(formData.email || '').trim();
    const cleanPassword = String(formData.password || '').trim();

    if (!cleanEmail || !cleanPassword) {
      setError('Please fill in all fields');
      return;
    }

    const result = await login(cleanEmail, cleanPassword);
    if (!result.success) {
      setError(result.error || 'Login failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-gray-300">
      {/* Header */}
      <header className="bg-gray-600 px-6 py-4">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-white bg-opacity-20 rounded flex items-center justify-center mr-3">
            <img src={getLogoUrl()} alt="logo" className="w-8 h-8 object-contain" />
          </div>
          <span className="text-white text-lg font-medium">{getCompanyName()}</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] px-4">
        <Card className="w-full max-w-md bg-white shadow-lg border-0 rounded-lg">
          <CardContent className="p-8">
            <div className="text-center mb-8">
              <p className="text-gray-600 text-sm mb-1">Hello,</p>
              <h1 className="text-gray-900 text-xl font-medium">
                Sign in to {getAppName()}
              </h1>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email" className="text-gray-700 text-sm font-medium">
                  Username or Email
                </Label>
                <Input
                  id="usernameOrEmail"
                  placeholder="Input username or email address"
                  value={formData.email}
                  onChange={createValidatedFieldOnChange('email', setFormData)}
                  disabled={isLoading}
                  className="h-10 border-gray-300 rounded-md focus:border-blue-500 focus:ring-blue-500 text-sm"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="password" className="text-gray-700 text-sm font-medium">
                  Password
                </Label>
                <div className="relative">
                  <Input
                    id="password"
                    type={showPassword ? 'text' : 'password'}
                    placeholder="Input Password"
                    value={formData.password}
                    onChange={createValidatedFieldOnChange('password', setFormData)}
                    disabled={isLoading}
                    className="h-10 pr-10 border-gray-300 rounded-md focus:border-blue-500 focus:ring-blue-500 text-sm"
                    style={{
                      WebkitTextSecurity: showPassword ? 'none' : 'disc',
                      msRevealButtonDisplayed: 'none'
                    } as React.CSSProperties}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </div>

              <div className="text-right pt-2">
                <Link to="/forgot-password" className="text-blue-500 text-sm hover:text-blue-600">
                  Forgot your password?
                </Link>
              </div>

              {error && (
                <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
                  {error}
                </div>
              )}

              <div className="pt-4">
                <Button 
                  type="submit" 
                  className="w-full h-10 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-md text-sm"
                  disabled={isLoading}
                >
                  {isLoading ? 'Signing in...' : 'Sign in'}
                </Button>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
