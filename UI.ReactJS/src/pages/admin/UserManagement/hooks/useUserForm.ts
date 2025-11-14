import { useState, useEffect, useCallback } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { UserService } from '../services/userService';
import type { UserRequest, UserRole, UserStatus } from '../types/user';

interface FormData {
  username: string;
  firstName: string;
  lastName: string;
  jobTitle: string;
  email: string;
  password: string;
  role: string;
  status: string;
}

export const useUserForm = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = Boolean(id);

  const [loading, setLoading] = useState(false);
  const [initialLoading, setInitialLoading] = useState(isEditMode);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [showPassword, setShowPassword] = useState(false);

  const [formData, setFormData] = useState<FormData>({
    username: '',
    firstName: '',
    lastName: '',
    jobTitle: '',
    email: '',
    password: '',
    role: 'User',
    status: 'Active'
  });

  // Track original form data to detect changes
  const [originalFormData, setOriginalFormData] = useState(formData);
  const [errors, setErrors] = useState<Record<string, string>>({});

  // Check if form has unsaved changes
  const hasUnsavedChanges = useCallback(() => {

    return Object.keys(formData).some(key => {
      const typedKey = key as keyof typeof formData;
      // Don't consider password field for change detection since it's empty by design in edit mode
      if (typedKey === 'password') return false;
      return formData[typedKey] !== originalFormData[typedKey];
    });
  }, [formData, originalFormData]);

  const handleInputChange = (field: keyof FormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  // Load user data in edit mode
  useEffect(() => {
    const loadUser = async () => {
      if (!isEditMode || !id) {
        setInitialLoading(false);
        return;
      }

      try {
        setInitialLoading(true);
        setError(null);
        const user = await UserService.getUserById(id);

        if (user) {
          const userData = {
            username: user.username,
            firstName: user.firstName,
            lastName: user.lastName,
            jobTitle: user.jobTitle,
            email: user.email,
            password: '', // Don't populate password in edit mode
            role: user.role,
            status: user.status
          };
          setFormData(userData);
          setOriginalFormData(userData);
        } else {
          setError('User not found');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load user');
      } finally {
        setInitialLoading(false);
      }
    };

    loadUser();
  }, [id, isEditMode]);

  // Add browser navigation protection for unsaved changes
  useEffect(() => {
    const handleBeforeUnload = (e: BeforeUnloadEvent) => {
      if (hasUnsavedChanges()) {
        e.preventDefault();
        e.returnValue = ''; // Required for Chrome
        return 'Leaving will stop any ongoing actions and discard unsaved progress. Are you sure you want to leave?';
      }
    };

    // Handle browser back button
    const handlePopState = (e: PopStateEvent) => {
      if (hasUnsavedChanges()) {
        e.preventDefault();
        if (!window.confirm('Leaving will stop any ongoing actions and discard unsaved progress. Are you sure you want to leave?')) {
          // User cancelled, push the current state back to prevent navigation
          window.history.pushState(null, '', window.location.pathname);
          return;
        } else {
          // User confirmed, reset form and allow navigation
          resetForm();
          navigate('/users');
        }
      }
    };

    window.addEventListener('beforeunload', handleBeforeUnload);
    window.addEventListener('popstate', handlePopState);

    // Push a state when component mounts to ensure we can handle back button
    window.history.pushState(null, '', window.location.pathname);

    return () => {
      window.removeEventListener('beforeunload', handleBeforeUnload);
      window.removeEventListener('popstate', handlePopState);
    };
  }, [hasUnsavedChanges, navigate]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.username.trim()) {
      newErrors.username = 'Please input username';
    }

    if (!formData.firstName.trim()) {
      newErrors.firstName = 'Please input first name';
    }

    if (!formData.lastName.trim()) {
      newErrors.lastName = 'Please input last name';
    }
    
    if (!formData.email.trim()) {
      newErrors.email = 'Please input email';
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please input valid email';
    }

    // Only require password for new users, not for updates
    if (!isEditMode && !formData.password.trim()) {
        newErrors.password = 'Please input password';
    }

    // Enhanced password validation
    if (formData.password) {
      const password = formData.password;

      if (password.length < 8) {
        newErrors.password = 'Password must have at least 8 characters, contain uppercase letters, lowercase letters, numbers, and symbols';
      } else {
        const hasUppercase = /[A-Z]/.test(password);
        const hasLowercase = /[a-z]/.test(password);
        const hasNumbers = /\d/.test(password);
        const hasSymbols = /[!@#$%^&*()_+\-=[\]{};':"\\|,.<>/?]/.test(password);

        if (!hasUppercase || !hasLowercase || !hasNumbers || !hasSymbols) {
          newErrors.password = 'Password must have at least 8 characters, contain uppercase letters, lowercase letters, numbers, and symbols';
        }
      }
    }

    // role and status are required
    if (!formData.role) {
      newErrors.role = 'Please select role';
    }
    if (!formData.status) {
      newErrors.status = 'Please select status';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const resetForm = () => {
    setFormData({
      username: '',
      firstName: '',
      lastName: '',
      jobTitle: '',
      email: '',
      password: '',
      role: '',
      status: ''
    });
    setErrors({});
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    try {
      setLoading(true);
      setError(null);
      setSuccess(null);
      setErrors({}); // Clear any existing field errors

      // Trim all string fields before sending to server
      const userData: UserRequest = {
        username: formData.username.trim(),
        firstName: formData.firstName.trim(),
        lastName: formData.lastName.trim(),
        jobTitle: formData.jobTitle.trim(),
        email: formData.email.trim(),
        password: formData.password.trim(),
        role: formData.role as UserRole,
        status: formData.status as UserStatus
      };

      if (isEditMode && id) {
        await UserService.updateUser(id, userData);
        setSuccess('User updated successfully!');
      } else {
        await UserService.createUser(userData);
        setSuccess('User created successfully!');
      }

      // Show success notification for 3 seconds, then redirect
      setTimeout(() => {
        navigate('/users');
      }, 1000);

    } catch (err) {
      console.error(`Error ${isEditMode ? 'updating' : 'creating'} user:`, err);

      if (err instanceof Error) {
        const errorMessage = err.message;
        console.log(errorMessage)

        // Handle specific API error cases
        if (errorMessage.toLowerCase().includes('email already registered')) {
          setErrors({ email: 'This email address is already registered. Please use a different email.' });
          setError(null); // Don't show general error if we have field-specific error
        } else if (errorMessage.toLowerCase().includes('username already taken')) {
          setErrors({ username: 'This username is already taken. Please choose a different username.' });
          setError(null);
        } else if (errorMessage.toLowerCase().includes('invalid email')) {
          setErrors({ email: 'Please enter a valid email address.' });
          setError(null);
        } else if (errorMessage.toLowerCase().includes('password')) {
          setErrors({ password: errorMessage });
          setError(null);
        } else {
          // Re-throw the original error to preserve detailed API error messages
          setError(errorMessage);
          throw err;
        }
      } else {
        setError('An unexpected error occurred. Please try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    // Check for unsaved changes in edit mode
    if (hasUnsavedChanges()) {
      if (!window.confirm('Leaving will stop any ongoing actions and discard unsaved progress. Are you sure you want to leave?')) {
        return; // User cancelled, don't navigate
      }
    }

    resetForm();
    navigate('/users');
  };

  return {
    // State
    formData,
    errors,
    loading,
    initialLoading,
    error,
    success,
    showPassword,
    isEditMode,

    // Actions
    handleInputChange,
    handleSubmit,
    handleCancel,
    setShowPassword,

    // Utils
    hasUnsavedChanges
  };
};
