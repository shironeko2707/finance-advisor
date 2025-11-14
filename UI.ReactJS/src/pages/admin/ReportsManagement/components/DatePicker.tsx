import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import { Calendar, X } from 'lucide-react';

interface CustomDatePickerProps {
  value: string;
  onChange: (dateStr: string) => void;
}

const CustomDatePicker: React.FC<CustomDatePickerProps> = ({ value, onChange }) => {
  const [selectedDate, setSelectedDate] = useState<Date | null>(
    value ? parseDate(value) : null
  );
  const [open, setOpen] = useState(false);

  function parseDate(dateStr: string): Date | null {
    const [day, month, year] = dateStr.split('/').map(Number);
    if (!day || !month || !year) return null;
    return new Date(year, month - 1, day);
  }

  function formatDate(date: Date | null): string {
    if (!date) return '';
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}/${month}/${year}`;
  }

  const handleDateChange = (date: Date | null) => {
    setSelectedDate(date);
    onChange(formatDate(date));
    setOpen(false);
  };

  const handleClear = () => {
    setSelectedDate(null);
    onChange('');
  };

  return (
    <div className="relative">
      <div className="relative flex items-center">
        <DatePicker
          selected={selectedDate}
          onChange={handleDateChange}
          onCalendarClose={() => setOpen(false)}
          onCalendarOpen={() => setOpen(true)}
          dateFormat="dd/MM/yyyy"
          placeholderText="DD/MM/YYYY"
          open={open}
          onClickOutside={() => setOpen(false)}
          showPopperArrow={false}
          todayButton="Today"
          isClearable={false}
          showMonthDropdown
          showYearDropdown
          dropdownMode="select"
          customInput={
            <input
              className="h-10 w-full border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition duration-150 ease-in-out px-4"
              readOnly
              value={formatDate(selectedDate)}
              placeholder="DD/MM/YYYY"
              onClick={() => setOpen(true)}
            />
          }
        />
        {selectedDate && (
          <button
            type="button"
            className="absolute right-12 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition duration-150 ease-in-out"
            onClick={handleClear}
            tabIndex={-1}
            aria-label="Clear date"
          >
            <X className="w-5 h-5" />
          </button>
        )}
        <button
          type="button"
          className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600 transition duration-150 ease-in-out"
          onClick={() => setOpen((prev) => !prev)}
          tabIndex={-1}
          aria-label="Open calendar"
        >
          <Calendar className="w-5 h-5" />
        </button>
      </div>
    </div>
  );
};

export default CustomDatePicker;