import React, { useState } from 'react';
import { Navigate } from 'react-router-dom';
import { Button } from '@/components/atomic/button.tsx';
import { Input } from '@/components/atomic/input.tsx';
import { Card, CardContent } from '@/components/atomic/card.tsx';
import { Label } from '@/components/atomic/label.tsx';
import { useAuth } from '@/contexts/AuthContext.tsx';
import { Eye, EyeOff } from 'lucide-react';
import { useInputValidation } from '@/components/hooks/useInputValidation';

type ForgotPasswordStep = 'email' | 'verification' | 'newPassword' | 'success';

export const ForgotPasswordPage: React.FC = () => {
  const [step, setStep] = useState<ForgotPasswordStep>('email');
  const [showPassword, setShowPassword] = useState(false);
  const [showCFPassword, setShowCFPassword] = useState(false);
  const [formData, setFormData] = useState({
    email: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [otp, setOtp] = useState(['', '', '', '']);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [timer, setTimer] = useState(0);
  const [resetToken, setResetToken] = useState<string | undefined>(undefined);
  const { user, sendOtp, verifyOtp, resetPassword } = useAuth();

  // Use the generic input validation hook
  const { createValidatedFieldOnChange } = useInputValidation();

  // If user is already logged in, redirect to dashboard
  if (user) {
    return <Navigate to="/" replace />;
  }

  // Email step
  const handleEmailSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Trim email before validation and submission
    const trimmedEmail = formData.email.trim();

    if (!trimmedEmail) {
      setError('Please enter your email address');
      setIsLoading(false);
      return;
    }

    try {
      const res = await sendOtp(trimmedEmail);
      if (res?.success) {
        setStep('verification');
        setTimer(60); // Start 60 second timer

        // Start countdown
        const countdown = setInterval(() => {
          setTimer(prev => {
            if (prev <= 1) {
              clearInterval(countdown);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } else {
        setError(res.message ?? "");
      }
    } catch (err) {
      console.error('Send OTP error:', err);
      setError('Send OTP error');
    } finally {
      setIsLoading(false);
    }
  };

  // OTP verification step
  const handleOtpChange = (index: number, value: string) => {
    // Allow only numeric input
    if (value !== '' && !/^\d$/.test(value)) {
      return;
    }

    if (value.length > 1) return;

    const newOtp = [...otp];
    newOtp[index] = value;
    setOtp(newOtp);

    // Auto focus next input
    if (value && index < 3) {
      const nextInput = document.getElementById(`otp-${index + 1}`);
      nextInput?.focus();
    }
  };

  const handleOtpSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const otpCode = otp.join('');
    if (otpCode.length !== 4) {
      setError('Please enter the full OTP code');
      setIsLoading(false);
      return;
    }

    try {
      // Simulate a 1-second delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      const response = await verifyOtp(formData.email, otpCode);
      if (response.success && response.reset_token) {
        setResetToken(response.reset_token);
        setStep('newPassword');
      } else {
        setError('Incorrect or expired OTP code.');
      }
    } catch (err) {
      console.error('Verify OTP error:', err);
      setError('An error occurred. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  // New password step
  const handlePasswordSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    // Trim password fields before validation and submission
    const trimmedNewPassword = formData.newPassword.trim();
    const trimmedConfirmPassword = formData.confirmPassword.trim();

    if (!trimmedNewPassword || !trimmedConfirmPassword) {
      setError('Please fill in all fields');
      setIsLoading(false);
      return;
    }

    if (trimmedNewPassword !== trimmedConfirmPassword) {
      setError('Password does not match');
      setIsLoading(false);
      return;
    }

    const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$/;
    if (!passwordRegex.test(trimmedNewPassword)) {
      setError('Password must have at least 8 characters, contain uppercase letters, lowercase letters, numbers, and symbols.');
      setIsLoading(false);
      return;
    }

    try {
      if (!resetToken) {
        setError('Password reset token not found. Please try again.');
        setIsLoading(false);
        return;
      }
      const success = await resetPassword(trimmedNewPassword, trimmedConfirmPassword, resetToken);
      if (success) {
        setStep('success');
      } else {
        setError('An error occurred while resetting the password.');
      }
    } catch (err) {
      console.error('Reset password error:', err);
      setError('An error occurred. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const resendOtp = async () => {
    setIsLoading(true);
    setError('');

    try {
      const success = await sendOtp(formData.email.trim());
      if (success) {
        setTimer(60);

        const countdown = setInterval(() => {
          setTimer(prev => {
            if (prev <= 1) {
              clearInterval(countdown);
              return 0;
            }
            return prev - 1;
          });
        }, 1000);
      } else {
        setError('Could not resend OTP code. Please try again.');
      }
    } catch (err) {
      console.error('Resend OTP error:', err);
      setError('An error occurred. Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-300">
      {/* Header */}
      <header className="bg-gray-600 px-6 py-4">
        <div className="flex items-center">
          <div className="w-10 h-10 bg-white bg-opacity-20 rounded flex items-center justify-center mr-3">
            <div className="text-white font-bold text-base">
              <div className="text-xs leading-tight">慶</div>
              <div className="text-xs leading-tight">隆</div>
            </div>
          </div>
          <span className="text-white text-lg font-medium">Kheng Leong Co</span>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex items-center justify-center min-h-[calc(100vh-80px)] px-4">
        <Card className="w-full max-w-md bg-white shadow-lg border-0 rounded-lg">
          <CardContent className="p-8">
            {/* Email Step */}
            {step === 'email' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h1 className="text-xl font-medium text-gray-900 mb-2">Reset Password</h1>
                  <p className="text-gray-600 text-sm">
                    Enter your email address and we will send you a code to reset your password.
                  </p>
                </div>

                <form onSubmit={handleEmailSubmit} className="space-y-4">
                  <div className="space-y-2">
                    <Label htmlFor="email" className="text-gray-700 text-sm font-medium">
                      Email Address
                    </Label>
                    <Input
                      id="email"
                      type="email"
                      placeholder="Enter your email address"
                      value={formData.email}
                      onChange={createValidatedFieldOnChange('email', setFormData)}
                      disabled={isLoading}
                      className="h-10 border-gray-300 rounded-md focus:border-blue-500 focus:ring-blue-500 text-sm"
                    />
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
                      {isLoading ? 'Sending...' : 'Send Confirmation Code'}
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Verification Step */}
            {step === 'verification' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h1 className="text-xl font-medium text-gray-900 mb-2">Enter Confirmation Code</h1>
                  <p className="text-gray-600 text-sm">
                    We have sent a 4-digit confirmation code to <span className="font-medium">{formData.email}</span>
                  </p>
                </div>

                <form onSubmit={handleOtpSubmit} className="space-y-4">
                  <div>
                    <Label className="text-gray-700 text-sm font-medium mb-3 block">
                      Confirmation Code
                    </Label>
                    <div className="flex justify-center space-x-3">
                      {otp.map((digit, index) => (
                        <Input
                          key={index}
                          id={`otp-${index}`}
                          type="text"
                          maxLength={1}
                          value={digit}
                          onChange={(e) => handleOtpChange(index, e.target.value)}
                          disabled={isLoading}
                          className="w-12 h-12 text-center text-lg font-medium border-gray-300 rounded-md focus:border-blue-500 focus:ring-blue-500"
                        />
                      ))}
                    </div>
                  </div>

                  {error && (
                    <div className="text-sm text-red-600 bg-red-50 border border-red-200 rounded-md p-3">
                      {error}
                    </div>
                  )}

                  <div className="text-center">
                    <p className="text-gray-600 text-sm">
                      Didn't receive the code? {' '}
                      {timer > 0 ? (
                        <span className="text-gray-500">Resend in {timer}s</span>
                      ) : (
                        <button
                          type="button"
                          onClick={resendOtp}
                          className="text-blue-600 hover:text-blue-500 font-medium"
                          disabled={isLoading}
                        >
                          Resend
                        </button>
                      )}
                    </p>
                  </div>

                  <div className="pt-4">
                    <Button
                      type="submit"
                      className="w-full h-10 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-md text-sm"
                      disabled={isLoading || otp.join('').length !== 4}
                    >
                      {isLoading ? 'Confirming...' : 'Confirm'}
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* New Password Step */}
            {step === 'newPassword' && (
              <div className="space-y-6">
                <div className="text-center">
                  <h1 className="text-xl font-medium text-gray-900 mb-2">Set New Password</h1>
                  <p className="text-gray-600 text-sm">
                    Enter a new password for your account
                  </p>
                </div>

                <form onSubmit={handlePasswordSubmit} className="space-y-4">
                  <div className="space-y-2 relative">
                    <Label htmlFor="newPassword" className="text-gray-700 text-sm font-medium">
                      New Password
                    </Label>
                    <Input
                      id="newPassword"
                      type={showPassword ? 'text' : 'password'}
                      placeholder="Enter new password"
                      value={formData.newPassword}
                      onChange={createValidatedFieldOnChange('newPassword', setFormData)}
                      disabled={isLoading}
                      className="h-10 border-gray-300 rounded-md focus:border-blue-500 focus:ring-blue-500 text-sm"
                      style={{
                        WebkitTextSecurity: showPassword ? 'none' : 'disc',
                        msRevealButtonDisplayed: 'none'
                      } as React.CSSProperties}
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-10 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
                  </div>

                  <div className="space-y-2 relative">
                    <Label htmlFor="confirmPassword" className="text-gray-700 text-sm font-medium">
                      Confirm Password
                    </Label>
                    <Input
                      id="confirmPassword"
                      type={showCFPassword ? 'text' : 'password'}
                      placeholder="Confirm new password"
                      value={formData.confirmPassword}
                      onChange={createValidatedFieldOnChange('confirmPassword', setFormData)}
                      disabled={isLoading}
                      className="h-10 border-gray-300 rounded-md focus:border-blue-500 focus:ring-blue-500 text-sm"
                      style={{
                        WebkitTextSecurity: showCFPassword ? 'none' : 'disc',
                        msRevealButtonDisplayed: 'none'
                      } as React.CSSProperties}
                    />
                    <button
                      type="button"
                      onClick={() => setShowCFPassword(!showCFPassword)}
                      className="absolute right-3 top-10 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
                    >
                      {showCFPassword ? (
                        <EyeOff className="h-4 w-4" />
                      ) : (
                        <Eye className="h-4 w-4" />
                      )}
                    </button>
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
                      {isLoading ? 'Updating...' : 'Reset Password'}
                    </Button>
                  </div>
                </form>
              </div>
            )}

            {/* Success Step */}
            {step === 'success' && (
              <div className="space-y-6 text-center">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto">
                  <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                </div>

                <div>
                  <h1 className="text-xl font-medium text-gray-900 mb-2">Success!</h1>
                  <p className="text-gray-600 text-sm">
                    Your password has been reset successfully. You can now sign in with your new password.
                  </p>
                </div>

                <Button
                  onClick={() => window.location.href = '/login'}
                  className="w-full h-10 bg-orange-500 hover:bg-orange-600 text-white font-medium rounded-md text-sm"
                >
                  Sign In Now
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
