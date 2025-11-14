// Simple script to create a test Excel file for demonstration
import * as XLSX from 'xlsx';

// Create a simple workbook
const workbook = XLSX.utils.book_new();

// Create worksheet with sample data
const worksheetData = [
  ['Report Template', '', '', ''],
  ['Company Name:', '', '', ''],
  ['Report Date:', '', '', ''],
  ['Total Revenue:', '', '', ''],
  ['', '', '', ''],
  ['Financial Summary', '', '', ''],
  ['Account', 'Q1', 'Q2', 'Q3'],
  ['Revenue', '', '', ''],
  ['Expenses', '', '', ''],
  ['Net Income', '', '', '']
];

const worksheet = XLSX.utils.aoa_to_sheet(worksheetData);
XLSX.utils.book_append_sheet(workbook, worksheet, 'Report');

// Write to file
XLSX.writeFile(workbook, '/tmp/test-template.xlsx');
console.log('Test Excel template created at /tmp/test-template.xlsx');