import { useCallback } from 'react';

interface UseInputValidationProps {
  maxLength?: number;
  alertMessage?: string;
}

// Simple hook for input validation with 255 character limit
export const useInputValidation = (options: UseInputValidationProps = {}) => {
  const {
    maxLength = 255,
    alertMessage = `Maximum ${maxLength} characters allowed for this field!`
  } = options;

  const validateAndSetValue = useCallback((
    value: string,
    setValue: (value: string) => void
  ) => {
    if (value.length > maxLength) {
      alert(alertMessage);
      return; // Don't update if limit exceeded
    }
    setValue(value);
  }, [maxLength, alertMessage]);

  // For single string states
  const createValidatedOnChange = useCallback((
    setValue: (value: string) => void
  ) => {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      validateAndSetValue(e.target.value, setValue);
    };
  }, [validateAndSetValue]);

  // For form object fields
  const createValidatedFieldOnChange = useCallback(<T>(
    field: keyof T,
    setFormData: React.Dispatch<React.SetStateAction<T>>,
    clearError?: () => void
  ) => {
    return (e: React.ChangeEvent<HTMLInputElement>) => {
      const value = e.target.value;
      if (value.length > maxLength) {
        alert(alertMessage);
        return;
      }
      setFormData(prev => ({ ...prev, [field]: value }));
      if (clearError) clearError();
    };
  }, [maxLength, alertMessage]);

  return {
    validateAndSetValue,
    createValidatedOnChange,
    createValidatedFieldOnChange,
    maxLength
  };
};
