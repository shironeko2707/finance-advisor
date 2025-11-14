import type { Report } from '../types';

// Mock data for development and testing
export const mockReports: Report[] = [
  {
    id: 1,
    report_name: 'UOB Financial Review',
    report_filename: 'generated_report_uob_financial_20250820_111248.xlsx',
    report_file_path: 'storage/generated\\generated_report_uob_financial_20250820_111248.xlsx',
    report_file_size: 22382,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: '240826-UOB Financial Review-FullInput.xlsx',
    input_files_count: 3,
    input_files_info: [
      {
        id: 21,
        original_filename: 'UOB - condensed-financial-statement-4q-2024-results 1.pdf',
        stored_filename: '45ea5bdd-8b83-40fd-8c3a-3b1313bb3952.pdf',
        file_path: 'storage/uploads\\45ea5bdd-8b83-40fd-8c3a-3b1313bb3952.pdf',
        file_type: 'pdf',
        file_size: 2035588,
        uploaded_at: '2025-08-20T04:09:53.016307'
      },
      {
        id: 22,
        original_filename: 'UOB - selected-financial-statements-2024-english 1.pdf',
        stored_filename: 'ff2290af-561a-4394-a3c5-c42c94f97cc3.pdf',
        file_path: 'storage/uploads\\ff2290af-561a-4394-a3c5-c42c94f97cc3.pdf',
        file_type: 'pdf',
        file_size: 178349,
        uploaded_at: '2025-08-20T04:09:53.028988'
      },
      {
        id: 23,
        original_filename: 'uob-annual-report-2024 1.pdf',
        stored_filename: '45ea946b-3c6b-4b52-9abc-914ed4a56fd5.pdf',
        file_path: 'storage/uploads\\45ea946b-3c6b-4b52-9abc-914ed4a56fd5.pdf',
        file_type: 'pdf',
        file_size: 12480657,
        uploaded_at: '2025-08-20T04:09:53.084609'
      }
    ],
    generated_at: '2025-08-20T04:12:48.705567',
    generated_by: 999999,
    generation_status: 'success',
    generation_time_seconds: 175,
    is_downloaded: false,
    download_count: 0
  },
  {
    id: 2,
    report_name: 'Quarterly Market Analysis',
    report_filename: 'generated_report_market_analysis_20250819_143021.xlsx',
    report_file_path: 'storage/generated\\generated_report_market_analysis_20250819_143021.xlsx',
    report_file_size: 18456,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Market-Analysis-Template.xlsx',
    input_files_count: 2,
    input_files_info: [
      {
        id: 24,
        original_filename: 'market-data-q3-2024.pdf',
        stored_filename: '7f3a8b1c-9d2e-4f5g-6h7i-8j9k0l1m2n3o.pdf',
        file_path: 'storage/uploads\\7f3a8b1c-9d2e-4f5g-6h7i-8j9k0l1m2n3o.pdf',
        file_type: 'pdf',
        file_size: 1245678,
        uploaded_at: '2025-08-19T14:25:12.123456'
      },
      {
        id: 25,
        original_filename: 'competitor-analysis.xlsx',
        stored_filename: '8a4b9c2d-0e3f-5g6h-7i8j-9k0l1m2n3o4p.xlsx',
        file_path: 'storage/uploads\\8a4b9c2d-0e3f-5g6h-7i8j-9k0l1m2n3o4p.xlsx',
        file_type: 'xlsx',
        file_size: 567890,
        uploaded_at: '2025-08-19T14:25:45.987654'
      }
    ],
    generated_at: '2025-08-19T14:30:21.456789',
    generated_by: 888888,
    generation_status: 'success',
    generation_time_seconds: 89,
    is_downloaded: true,
    download_count: 3
  },
  {
    id: 3,
    report_name: 'Investment Portfolio Review',
    report_filename: 'generated_report_investment_portfolio_20250818_160000.xlsx',
    report_file_path: 'storage/generated\\generated_report_investment_portfolio_20250818_160000.xlsx',
    report_file_size: 15678,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Investment-Analysis-Template.xlsx',
    input_files_count: 1,
    input_files_info: [
      {
        id: 26,
        original_filename: 'portfolio-data-2024.pdf',
        stored_filename: '9b5c8d3e-1f4g-6h7i-8j9k-0l1m2n3o4p5q.pdf',
        file_path: 'storage/uploads\\9b5c8d3e-1f4g-6h7i-8j9k-0l1m2n3o4p5q.pdf',
        file_type: 'pdf',
        file_size: 987654,
        uploaded_at: '2025-08-18T15:55:00.123456'
      }
    ],
    generated_at: '2025-08-18T16:00:00.654321',
    generated_by: 777777,
    generation_status: 'success',
    generation_time_seconds: 125,
    is_downloaded: true,
    download_count: 1
  },
  {
    id: 4,
    report_name: 'Annual Financial Summary',
    report_filename: 'generated_report_annual_summary_20250817_120000.xlsx',
    report_file_path: 'storage/generated\\generated_report_annual_summary_20250817_120000.xlsx',
    report_file_size: 19876,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Annual-Summary-Template.xlsx',
    input_files_count: 2,
    input_files_info: [
      {
        id: 27,
        original_filename: 'annual-report-2024.pdf',
        stored_filename: 'b0f1c2d3-4e5f-6g7h-8i9j-0k1l2m3n4o5p.pdf',
        file_path: 'storage/uploads\\b0f1c2d3-4e5f-6g7h-8i9j-0k1l2m3n4o5p.pdf',
        file_type: 'pdf',
        file_size: 345678,
        uploaded_at: '2025-08-17T09:00:00.000000'
      },
      {
        id: 28,
        original_filename: 'summary-data-2024.xlsx',
        stored_filename: 'c1d2e3f4-5g6h-7i8j-9k0l1m2n3o4p5q.xlsx',
        file_path: 'storage/uploads\\c1d2e3f4-5g6h-7i8j-9k0l1m2n3o4p5q.xlsx',
        file_type: 'xlsx',
        file_size: 123456,
        uploaded_at: '2025-08-17T10:00:00.000000'
      }
    ],
    generated_at: '2025-08-17T12:00:00.000000',
    generated_by: 666666,
    generation_status: 'success',
    generation_time_seconds: 100,
    is_downloaded: false,
    download_count: 0
  },
  {
    id: 5,
    report_name: 'Market Trends Overview',
    report_filename: 'generated_report_market_trends_20250816_140000.xlsx',
    report_file_path: 'storage/generated\\generated_report_market_trends_20250816_140000.xlsx',
    report_file_size: 43210,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Market-Trends-Template.xlsx',
    input_files_count: 1,
    input_files_info: [
      {
        id: 29,
        original_filename: 'trends-q2-2024.pdf',
        stored_filename: 'e2f3g4h5-6i7j-8k9l-0m1n2o3p4q5r.pdf',
        file_path: 'storage/uploads\\e2f3g4h5-6i7j-8k9l-0m1n2o3p4q5r.pdf',
        file_type: 'pdf',
        file_size: 567890,
        uploaded_at: '2025-08-16T11:30:00.000000'
      }
    ],
    generated_at: '2025-08-16T14:00:00.000000',
    generated_by: 555555,
    generation_status: 'success',
    generation_time_seconds: 150,
    is_downloaded: true,
    download_count: 2
  },
  {
    id: 6,
    report_name: 'Customer Satisfaction Analysis',
    report_filename: 'generated_report_customer_satisfaction_20250815_160000.xlsx',
    report_file_path: 'storage/generated\\generated_report_customer_satisfaction_20250815_160000.xlsx',
    report_file_size: 56789,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Customer-Satisfaction-Template.xlsx',
    input_files_count: 3,
    input_files_info: [
      {
        id: 30,
        original_filename: 'customer-feedback-2024.pdf',
        stored_filename: 'f1g2h3i4-5j6k-7l8m-9n0o1p2q3r4s.pdf',
        file_path: 'storage/uploads\\f1g2h3i4-5j6k-7l8m-9n0o1p2q3r4s.pdf',
        file_type: 'pdf',
        file_size: 234567,
        uploaded_at: '2025-08-15T09:15:00.000000'
      },
      {
        id: 31,
        original_filename: 'satisfaction-survey-2024.xlsx',
        stored_filename: 'g2h3i4j5-6k7l-8m9n-0o1p2q3r4s5t.xlsx',
        file_path: 'storage/uploads\\g2h3i4j5-6k7l-8m9n-0o1p2q3r4s5t.xlsx',
        file_type: 'xlsx',
        file_size: 456789,
        uploaded_at: '2025-08-15T09:30:00.000000'
      }
    ],
    generated_at: '2025-08-15T16:00:00.000000',
    generated_by: 444444,
    generation_status: 'success',
    generation_time_seconds: 120,
    is_downloaded: false,
    download_count: 0
  },
  {
    id: 7,
    report_name: 'Risk Assessment Report',
    report_filename: 'generated_report_risk_assessment_20250814_110000.xlsx',
    report_file_path: 'storage/generated\\generated_report_risk_assessment_20250814_110000.xlsx',
    report_file_size: 67890,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Risk-Assessment-Template.xlsx',
    input_files_count: 2,
    input_files_info: [
      {
        id: 32,
        original_filename: 'risk-data-2024.pdf',
        stored_filename: 'h3i4j5k6-7l8m-9n0o1p2q3r4s5t.pdf',
        file_path: 'storage/uploads\\h3i4j5k6-7l8m-9n0o1p2q3r4s5t.pdf',
        file_type: 'pdf',
        file_size: 345678,
        uploaded_at: '2025-08-14T10:00:00.000000'
      },
      {
        id: 33,
        original_filename: 'risk-mitigation-strategies.xlsx',
        stored_filename: 'i4j5k6l7-8m9n-0o1p2q3r4s5t6u.xlsx',
        file_path: 'storage/uploads\\i4j5k6l7-8m9n-0o1p2q3r4s5t6u.xlsx',
        file_type: 'xlsx',
        file_size: 567890,
        uploaded_at: '2025-08-14T10:30:00.000000'
      }
    ],
    generated_at: '2025-08-14T11:00:00.000000',
    generated_by: 333333,
    generation_status: 'success',
    generation_time_seconds: 140,
    is_downloaded: true,
    download_count: 4
  },
  {
    id: 8,
    report_name: 'Sales Performance Review',
    report_filename: 'generated_report_sales_performance_20250813_130000.xlsx',
    report_file_path: 'storage/generated\\generated_report_sales_performance_20250813_130000.xlsx',
    report_file_size: 78901,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Sales-Performance-Template.xlsx',
    input_files_count: 2,
    input_files_info: [
      {
        id: 34,
        original_filename: 'sales-data-2024.pdf',
        stored_filename: 'j5k6l7m8-9n0o1p2q3r4s5t6u.pdf',
        file_path: 'storage/uploads\\j5k6l7m8-9n0o1p2q3r4s5t6u.pdf',
        file_type: 'pdf',
        file_size: 456789,
        uploaded_at: '2025-08-13T12:00:00.000000'
      },
      {
        id: 35,
        original_filename: 'sales-summary-2024.xlsx',
        stored_filename: 'k6l7m8n9-0o1p2q3r4s5t6u7v.xlsx',
        file_path: 'storage/uploads\\k6l7m8n9-0o1p2q3r4s5t6u7v.xlsx',
        file_type: 'xlsx',
        file_size: 234567,
        uploaded_at: '2025-08-13T12:30:00.000000'
      }
    ],
    generated_at: '2025-08-13T13:00:00.000000',
    generated_by: 222222,
    generation_status: 'success',
    generation_time_seconds: 110,
    is_downloaded: false,
    download_count: 0
  },
  {
    id: 9,
    report_name: 'Operational Efficiency Report',
    report_filename: 'generated_report_operational_efficiency_20250812_100000.xlsx',
    report_file_path: 'storage/generated\\generated_report_operational_efficiency_20250812_100000.xlsx',
    report_file_size: 89012,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Operational-Efficiency-Template.xlsx',
    input_files_count: 2,
    input_files_info: [
      {
        id: 36,
        original_filename: 'efficiency-data-2024.pdf',
        stored_filename: 'l7m8n9o0-1p2q3r4s5t6u7v8w.pdf',
        file_path: 'storage/uploads\\l7m8n9o0-1p2q3r4s5t6u7v8w.pdf',
        file_type: 'pdf',
        file_size: 123456,
        uploaded_at: '2025-08-12T09:00:00.000000'
      },
      {
        id: 37,
        original_filename: 'efficiency-summary-2024.xlsx',
        stored_filename: 'm8n9o0p1-2q3r4s5t6u7v8w9x.xlsx',
        file_path: 'storage/uploads\\m8n9o0p1-2q3r4s5t6u7v8w9x.xlsx',
        file_type: 'xlsx',
        file_size: 345678,
        uploaded_at: '2025-08-12T09:30:00.000000'
      }
    ],
    generated_at: '2025-08-12T10:00:00.000000',
    generated_by: 111111,
    generation_status: 'success',
    generation_time_seconds: 130,
    is_downloaded: true,
    download_count: 5
  },
  {
    id: 10,
    report_name: 'Product Development Insights',
    report_filename: 'generated_report_product_development_20250811_150000.xlsx',
    report_file_path: 'storage/generated\\generated_report_product_development_20250811_150000.xlsx',
    report_file_size: 90123,
    report_content_type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    template_filename: 'Product-Development-Template.xlsx',
    input_files_count: 1,
    input_files_info: [
      {
        id: 38,
        original_filename: 'product-research-2024.pdf',
        stored_filename: 'n9o2q3r4s5t6u7v8w9x.xlsx',
        file_path: 'storage/uploads\\m8n9o0p1-2q3r4s5t6u7v8w9x.xlsx',
        file_type: 'xlsx',
        file_size: 345678,
        uploaded_at: '2025-08-12T09:30:00.000000'
      }
    ],
    generated_at: '2025-08-12T10:00:00.000000',
    generated_by: 111111,
    generation_status: 'success',
    generation_time_seconds: 130,
    is_downloaded: true,
    download_count: 5
  }
]

// Available templates (should match from template management)
export const availableTemplates = [
  '240826-UOB Financial Review-FullInput.xlsx',
  'Market-Analysis-Template.xlsx',
  'Investment-Analysis-Template.xlsx',
  'Risk-Assessment-Template.xlsx',
  'Quarterly-Report-Template.xlsx'
];

// Available creators (should come from user management)
export const availableCreators = [
  '999999',
  '888888',
  '777777',
  '666666',
  '555555'
];