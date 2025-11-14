import React, { useState, useRef, useEffect } from 'react';
import { MoreHorizontal } from 'lucide-react';
import { cn } from '@/components/lib/utils';

export interface DropdownMenuItem {
  label: string;
  onClick: () => void;
  icon?: React.ReactNode;
  className?: string;
  disabled?: boolean;
}

export interface DropdownMenuProps {
  items: DropdownMenuItem[];
  trigger?: React.ReactNode;
  className?: string;
  triggerClassName?: string;
  menuClassName?: string;
  align?: 'left' | 'right' | 'center';
}

export const DropdownMenu: React.FC<DropdownMenuProps> = ({
  items,
  trigger,
  className,
  triggerClassName,
  menuClassName,
  align = 'center'
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isOpen]);

  const getAlignmentClass = () => {
    switch (align) {
      case 'left': return 'left-0';
      case 'right': return 'right-0';
      case 'center': return 'left-1/2 transform -translate-x-1/2';
      default: return 'left-1/2 transform -translate-x-1/2';
    }
  };

  return (
    <div className={cn('relative inline-block text-left', className)} ref={dropdownRef}>
      <button
        type="button"
        onClick={() => setIsOpen(!isOpen)}
        className={cn(
          'inline-flex items-center focus:outline-none',
          triggerClassName
        )}
      >
        {trigger || (
          <div className="inline-flex items-center justify-center w-8 h-8 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-full">
            <MoreHorizontal className="w-4 h-4" />
          </div>
        )}
      </button>

      {isOpen && (
        <div className={cn(
          'absolute z-10 mt-2 w-48 origin-top bg-white rounded-md shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none',
          getAlignmentClass(),
          menuClassName
        )}>
          <div className="py-1">
            {items.map((item, index) => (
              <button
                key={index}
                onClick={() => {
                  item.onClick();
                  setIsOpen(false);
                }}
                disabled={item.disabled}
                className={cn(
                  'group flex items-center px-4 py-2 text-sm w-full text-left',
                  'text-gray-700 hover:bg-gray-100 hover:text-gray-900',
                  'disabled:opacity-50 disabled:cursor-not-allowed',
                  item.className
                )}
              >
                {item.icon && (
                  <span className="mr-3 flex-shrink-0">
                    {item.icon}
                  </span>
                )}
                {item.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};