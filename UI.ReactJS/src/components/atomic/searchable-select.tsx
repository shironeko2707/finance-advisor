import React, { useState, useEffect, useRef } from 'react';
import downArrow from '../../assets/down-arrow.png';
import { Input } from './input';

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
}

export const SelectItem: React.FC<SelectItemProps> = ({ value, children }) => (
  <div data-value={value}>{children}</div>
);

interface SearchableSelectProps {
  value: string;
  onValueChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  children: React.ReactElement<SelectItemProps>[] | React.ReactElement<SelectItemProps>;
}

export const SearchableSelect: React.FC<SearchableSelectProps> = ({
  value,
  onValueChange,
  placeholder,
  disabled,
  children
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedValue, setSelectedValue] = useState(value);
  const [isFocused, setIsFocused] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);

  const items = React.Children.toArray(children) as React.ReactElement<SelectItemProps>[];

  const selectedItem = items.find(item => item.props.value === selectedValue);
  const selectedItemText = selectedItem ? selectedItem.props.children : '';

  const inputDisplayValue = isFocused ? searchTerm : (selectedValue !== '' ? String(selectedItemText) : '');

  useEffect(() => {
    setSelectedValue(value);
  }, [value]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  useEffect(() => {
    if (!isOpen) {
      setSearchTerm('');
    }
  }, [isOpen]);

  const handleSelect = (itemValue: string) => {
    setSelectedValue(itemValue);
    onValueChange(itemValue);
    setIsOpen(false);
    setSearchTerm('');
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newSearchTerm = e.target.value;
    if (e.target.value.trim() === "") {
      setSelectedValue("");
    }
    setSearchTerm(newSearchTerm);
    setIsOpen(true);
  };


  const filteredItems = items.filter(item =>
    React.Children.toArray(item.props.children).some(child =>
      typeof child === 'string' && child.toLowerCase().includes(searchTerm.toLowerCase().trim().replace(/\s+/g, ' '))
    )
  );

  return (
    <div className="relative" ref={selectRef}>
      {/* Main Input Field */}
      <div className='relative'>
        <Input
          type="text"
          value={inputDisplayValue}
          onChange={handleInputChange}
          onFocus={() => { setIsFocused(true); setIsOpen(true); }}
          onBlur={() => {setIsFocused(false); setSearchTerm("")}}
          placeholder={placeholder}
          className="h-10 w-full border border-gray-300 rounded-md px-3 py-2 text-sm"
          disabled={disabled}
        />
        <img src={downArrow} alt="downArrow" className='absolute right-2 top-[55%] translate-y-[-50%] w-4 h-4' />
      </div>
      {/* Dropdown List */}
      {isOpen && (
        <div className="absolute z-10 w-full bg-white border border-gray-300 rounded-md mt-1">
          <div className="max-h-60 overflow-y-auto">
            { filteredItems.length ? filteredItems.map(item => (
              <div
                key={item.props.value}
                className="w-full px-3 py-2 text-left text-sm hover:bg-gray-100 focus:bg-gray-100 focus:outline-none cursor-pointer"
                onClick={() => handleSelect(item.props.value)}
              >
                {item.props.children}
              </div>
            )) : <div className='p-2 text-sm'>No data found</div>}
          </div>
        </div>
      )}
    </div>
  );
};