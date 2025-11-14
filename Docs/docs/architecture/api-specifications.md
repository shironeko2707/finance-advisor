# API Design Specifications
*Detailed API specifications for Khengleong system modules*

## Overview

This document provides detailed API specifications for each module in the Khengleong system architecture. All APIs follow RESTful design principles and include comprehensive error handling, authentication, and documentation.

## Global API Standards

### Base URL Structure
```
https://api.Khengleong.com/v1/{service}/{resource}
```

### Common Headers
```http
Authorization: Bearer {jwt_token}
Content-Type: application/json
Accept: application/json
X-Request-ID: {unique_request_id}
X-API-Version: 1.0
```

### Standard HTTP Status Codes
- `200` - OK (Success)
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `422` - Unprocessable Entity
- `429` - Too Many Requests
- `500` - Internal Server Error

### Standard Error Response Format
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input parameters",
    "details": [
      {
        "field": "file_type",
        "message": "File type not supported"
      }
    ],
    "request_id": "req_123456789"
  }
}
```

## 1. File Upload Service API

### Upload File
```http
POST /api/v1/files/upload
Content-Type: multipart/form-data
```

**Request Body:**
```
files: [File, File, ...] (max 5 files)
report_name: string (optional)
description: string (optional)
```

**Response:**
```json
{
  "upload_id": "upload_123456",
  "files": [
    {
      "file_id": "file_001",
      "original_name": "report.pdf",
      "size": 1024576,
      "type": "application/pdf",
      "status": "uploaded"
    }
  ],
  "status": "completed",
  "created_at": "2025-01-30T10:00:00Z"
}
```

### Get Upload Status
```http
GET /api/v1/files/upload/{upload_id}/status
```

**Response:**
```json
{
  "upload_id": "upload_123456",
  "status": "processing|completed|failed",
  "progress": 85,
  "files": [
    {
      "file_id": "file_001",
      "status": "validated",
      "validation_errors": []
    }
  ],
  "updated_at": "2025-01-30T10:05:00Z"
}
```

### Delete File
```http
DELETE /api/v1/files/{file_id}
```

**Response:**
```json
{
  "message": "File deleted successfully",
  "file_id": "file_001"
}
```

### Validate File
```http
POST /api/v1/files/validate
Content-Type: multipart/form-data
```

**Request Body:**
```
file: File
```

**Response:**
```json
{
  "valid": true,
  "file_type": "application/pdf",
  "size": 1024576,
  "validation_results": {
    "format_check": "passed",
    "virus_scan": "clean",
    "content_check": "readable"
  }
}
```

## 2. AI Extraction Service API

### Start Extraction Process
```http
POST /api/v1/extract/process
```

**Request Body:**
```json
{
  "upload_id": "upload_123456",
  "extraction_config": {
    "extract_tables": true,
    "extract_text": true,
    "ocr_enabled": true,
    "confidence_threshold": 0.8
  }
}
```

**Response:**
```json
{
  "job_id": "extract_job_001",
  "status": "queued",
  "estimated_duration": "120s",
  "created_at": "2025-01-30T10:00:00Z"
}
```

### Get Extraction Status
```http
GET /api/v1/extract/{job_id}/status
```

**Response:**
```json
{
  "job_id": "extract_job_001",
  "status": "processing|completed|failed",
  "progress": 75,
  "current_step": "table_extraction",
  "steps": [
    {
      "name": "file_analysis",
      "status": "completed",
      "duration": 5
    },
    {
      "name": "text_extraction",
      "status": "completed",
      "duration": 30
    },
    {
      "name": "table_extraction",
      "status": "processing",
      "progress": 60
    }
  ],
  "updated_at": "2025-01-30T10:02:00Z"
}
```

### Get Extraction Results
```http
GET /api/v1/extract/{job_id}/results
```

**Response:**
```json
{
  "job_id": "extract_job_001",
  "extraction_results": {
    "text_data": {
      "content": "Extracted text content...",
      "confidence": 0.95
    },
    "table_data": [
      {
        "table_id": "table_001",
        "headers": ["Date", "Amount", "Description"],
        "rows": [
          ["2025-01-30", "1000.00", "Investment return"]
        ],
        "confidence": 0.92
      }
    ],
    "metadata": {
      "total_pages": 5,
      "processed_pages": 5,
      "extraction_time": 120
    }
  },
  "completed_at": "2025-01-30T10:02:00Z"
}
```

### Validate Extraction Results
```http
POST /api/v1/extract/validate
```

**Request Body:**
```json
{
  "job_id": "extract_job_001",
  "validation_rules": {
    "required_fields": ["date", "amount"],
    "data_types": {
      "amount": "number",
      "date": "date"
    }
  }
}
```

**Response:**
```json
{
  "validation_result": {
    "valid": true,
    "errors": [],
    "warnings": [
      {
        "field": "description",
        "message": "Field confidence below threshold"
      }
    ]
  }
}
```

## 3. Template Service API

### List Templates
```http
GET /api/v1/templates?page=1&limit=20&status=active
```

**Response:**
```json
{
  "templates": [
    {
      "id": "template_001",
      "name": "Tencent Quarterly Report",
      "description": "Template for Tencent quarterly financial reports",
      "version": 2,
      "status": "active",
      "category": "quarterly_reports",
      "created_at": "2025-01-30T10:00:00Z",
      "updated_at": "2025-01-30T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 40,
    "total_pages": 2
  }
}
```

### Create Template
```http
POST /api/v1/templates
Content-Type: multipart/form-data
```

**Request Body:**
```
name: string
description: string (optional)
category: string
template_file: File (Excel file)
mapping_config: JSON string
```

**Response:**
```json
{
  "id": "template_002",
  "name": "New Template",
  "version": 1,
  "status": "draft",
  "file_path": "/templates/template_002_v1.xlsx",
  "created_at": "2025-01-30T10:00:00Z"
}
```

### Get Template
```http
GET /api/v1/templates/{template_id}
```

**Response:**
```json
{
  "id": "template_001",
  "name": "Tencent Quarterly Report",
  "description": "Template for Tencent quarterly financial reports",
  "version": 2,
  "status": "active",
  "category": "quarterly_reports",
  "file_path": "/templates/template_001_v2.xlsx",
  "field_mappings": [
    {
      "id": "mapping_001",
      "field_name": "revenue_q1",
      "cell_reference": "B5",
      "data_type": "currency",
      "validation_rules": {
        "min_value": 0,
        "required": true
      }
    }
  ],
  "created_at": "2025-01-30T10:00:00Z",
  "updated_at": "2025-01-30T10:00:00Z"
}
```

### Update Template
```http
PUT /api/v1/templates/{template_id}
```

**Request Body:**
```json
{
  "name": "Updated Template Name",
  "description": "Updated description",
  "status": "active"
}
```

**Response:**
```json
{
  "id": "template_001",
  "name": "Updated Template Name",
  "version": 3,
  "status": "active",
  "updated_at": "2025-01-30T10:00:00Z"
}
```

### Delete Template
```http
DELETE /api/v1/templates/{template_id}
```

**Response:**
```json
{
  "message": "Template deleted successfully",
  "template_id": "template_001"
}
```

### Add Field Mapping
```http
POST /api/v1/templates/{template_id}/mappings
```

**Request Body:**
```json
{
  "field_name": "net_income",
  "cell_reference": "B10",
  "data_type": "currency",
  "validation_rules": {
    "required": true,
    "min_value": 0
  }
}
```

**Response:**
```json
{
  "id": "mapping_002",
  "template_id": "template_001",
  "field_name": "net_income",
  "cell_reference": "B10",
  "data_type": "currency",
  "created_at": "2025-01-30T10:00:00Z"
}
```

### Get Template Preview
```http
GET /api/v1/templates/{template_id}/preview
```

**Response:**
```json
{
  "template_id": "template_001",
  "preview_url": "https://api.Khengleong.com/files/preview/template_001_preview.html",
  "thumbnail_url": "https://api.Khengleong.com/files/preview/template_001_thumb.png",
  "structure": {
    "sheets": [
      {
        "name": "Summary",
        "mapped_fields": 15,
        "total_fields": 20
      }
    ]
  }
}
```

## 4. Report Service API

### Generate Report
```http
POST /api/v1/reports/generate
```

**Request Body:**
```json
{
  "template_id": "template_001",
  "extraction_job_id": "extract_job_001",
  "report_name": "Tencent Q1 2025 Report",
  "options": {
    "include_raw_data": false,
    "apply_formatting": true
  }
}
```

**Response:**
```json
{
  "report_id": "report_001",
  "status": "generating",
  "estimated_completion": "2025-01-30T10:05:00Z",
  "created_at": "2025-01-30T10:00:00Z"
}
```

### Get Report Preview
```http
GET /api/v1/reports/{report_id}/preview
```

**Response:**
```json
{
  "report_id": "report_001",
  "preview_url": "https://api.Khengleong.com/reports/preview/report_001.html",
  "status": "ready",
  "metadata": {
    "template_name": "Tencent Quarterly Report",
    "data_sources": ["file_001", "file_002"],
    "generated_at": "2025-01-30T10:03:00Z"
  }
}
```

### Download Report
```http
GET /api/v1/reports/{report_id}/download
```

**Response Headers:**
```http
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="Tencent_Q1_2025_Report.xlsx"
```

**Response:** Binary Excel file content

### Get Report History
```http
GET /api/v1/reports/history?page=1&limit=20&user_id=user_001
```

**Response:**
```json
{
  "reports": [
    {
      "id": "report_001",
      "name": "Tencent Q1 2025 Report",
      "template_name": "Tencent Quarterly Report",
      "status": "completed",
      "created_at": "2025-01-30T10:00:00Z",
      "download_count": 3,
      "file_size": 1024576
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "total_pages": 3
  }
}
```

### Batch Generate Reports
```http
POST /api/v1/reports/batch-generate
```

**Request Body:**
```json
{
  "batch_name": "Q1 2025 All Companies",
  "reports": [
    {
      "template_id": "template_001",
      "extraction_job_id": "extract_job_001",
      "report_name": "Tencent Q1 Report"
    },
    {
      "template_id": "template_002",
      "extraction_job_id": "extract_job_002",
      "report_name": "Xiaomi Q1 Report"
    }
  ]
}
```

**Response:**
```json
{
  "batch_id": "batch_001",
  "status": "queued",
  "total_reports": 2,
  "estimated_completion": "2025-01-30T10:10:00Z",
  "created_at": "2025-01-30T10:00:00Z"
}
```

## 5. Authentication & Authorization API

### User Login
```http
POST /api/v1/auth/login
```

**Request Body:**
```json
{
  "username": "user@company.com",
  "password": "password123",
  "remember_me": true
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 3600,
  "user": {
    "id": "user_001",
    "username": "user@company.com",
    "name": "John Doe",
    "role": "user",
    "permissions": ["file.upload", "report.generate"]
  }
}
```

### Refresh Token
```http
POST /api/v1/auth/refresh
```

**Request Body:**
```json
{
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

### User Logout
```http
POST /api/v1/auth/logout
```

### Get Current User
```http
GET /api/v1/auth/me
```

**Response:**
```json
{
  "id": "user_001",
  "username": "user@company.com",
  "name": "John Doe",
  "role": "user",
  "permissions": ["file.upload", "report.generate"],
  "last_login": "2025-01-30T09:00:00Z"
}
```

## 6. Audit & Logging API

### Get Audit Logs
```http
GET /api/v1/audit/logs?start_date=2025-01-01&end_date=2025-01-30&action=file.upload&page=1&limit=50
```

**Response:**
```json
{
  "logs": [
    {
      "id": "log_001",
      "timestamp": "2025-01-30T10:00:00Z",
      "user_id": "user_001",
      "action": "file.upload",
      "resource_type": "file",
      "resource_id": "file_001",
      "details": {
        "file_name": "report.pdf",
        "file_size": 1024576
      },
      "ip_address": "192.168.1.100",
      "status": "success"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 50,
    "total": 1000,
    "total_pages": 20
  }
}
```

### Export Audit Logs
```http
POST /api/v1/audit/export
```

**Request Body:**
```json
{
  "start_date": "2025-01-01",
  "end_date": "2025-01-30",
  "format": "csv|json|excel",
  "filters": {
    "actions": ["file.upload", "report.generate"],
    "users": ["user_001", "user_002"]
  }
}
```

**Response:**
```json
{
  "export_id": "export_001",
  "status": "processing",
  "estimated_completion": "2025-01-30T10:05:00Z"
}
```

---

*Document Version: 1.0*  
*Last Updated: 2025-01-30*  
*Author: API Design Team*