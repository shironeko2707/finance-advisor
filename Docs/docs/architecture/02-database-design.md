# Database Design Document

| Version | Updated Date | Updated By | Reviewed By |  Note                 |
|---------|--------------|------------|-------------|-----------------------|
| 0.1.0   | 2024-31-07   | HoangPT    | TamHT       |Stubing the document   |

## Overview

This document outlines the complete database design for the Khengleong AI Report Generation Platform. The system uses PostgreSQL as the primary database with Redis for caching and Elasticsearch for search and logging.

## Database Architecture

### Multi-Database Strategy

![Multi-DB](../assets/architecture/02-db/multi-db.svg)
[Refer: Mermaid Language](../assets/architecture/02-db/multi-db.mmd)

## 1. Application Database Schema

### Core Tables

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) NOT NULL DEFAULT 'user',
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    last_login_at TIMESTAMP,
    password_changed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT users_role_check CHECK (role IN ('admin', 'user', 'viewer')),
    CONSTRAINT users_status_check CHECK (status IN ('active', 'inactive', 'suspended'))
);

CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
```

#### User Sessions Table
```sql
CREATE TABLE user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    session_token VARCHAR(512) NOT NULL,
    refresh_token VARCHAR(512),
    ip_address INET,
    user_agent TEXT,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    last_accessed_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_token ON user_sessions(session_token);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);
```

#### File Uploads Table
```sql
CREATE TABLE file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    upload_batch_id UUID,
    original_filename VARCHAR(500) NOT NULL,
    stored_filename VARCHAR(500) NOT NULL,
    file_path VARCHAR(1000) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(100) NOT NULL,
    mime_type VARCHAR(100) NOT NULL,
    file_hash VARCHAR(128),
    status VARCHAR(50) NOT NULL DEFAULT 'uploaded',
    validation_status VARCHAR(50) DEFAULT 'pending',
    validation_errors JSONB,
    metadata JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT file_uploads_status_check CHECK (
        status IN ('uploaded', 'validated', 'processing', 'completed', 'failed', 'deleted')
    ),
    CONSTRAINT file_uploads_validation_status_check CHECK (
        validation_status IN ('pending', 'passed', 'failed')
    )
);

CREATE INDEX idx_file_uploads_user_id ON file_uploads(user_id);
CREATE INDEX idx_file_uploads_batch_id ON file_uploads(upload_batch_id);
CREATE INDEX idx_file_uploads_status ON file_uploads(status);
CREATE INDEX idx_file_uploads_file_type ON file_uploads(file_type);
```

#### Extraction Jobs Table
```sql
CREATE TABLE extraction_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    upload_batch_id UUID,
    job_name VARCHAR(255),
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    progress INTEGER DEFAULT 0,
    current_step VARCHAR(100),
    extraction_config JSONB,
    results JSONB,
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    estimated_duration INTEGER, -- in seconds
    actual_duration INTEGER, -- in seconds
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT extraction_jobs_status_check CHECK (
        status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')
    ),
    CONSTRAINT extraction_jobs_progress_check CHECK (progress >= 0 AND progress <= 100)
);

CREATE INDEX idx_extraction_jobs_user_id ON extraction_jobs(user_id);
CREATE INDEX idx_extraction_jobs_status ON extraction_jobs(status);
CREATE INDEX idx_extraction_jobs_created_at ON extraction_jobs(created_at);
CREATE INDEX idx_extraction_jobs_batch_id ON extraction_jobs(upload_batch_id);
```

#### Extraction Job Files Table
```sql
CREATE TABLE extraction_job_files (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    extraction_job_id UUID NOT NULL REFERENCES extraction_jobs(id) ON DELETE CASCADE,
    file_upload_id UUID NOT NULL REFERENCES file_uploads(id),
    processing_order INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    file_results JSONB,
    processing_time INTEGER, -- in seconds
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT extraction_job_files_status_check CHECK (
        status IN ('pending', 'processing', 'completed', 'failed')
    )
);

CREATE INDEX idx_extraction_job_files_job_id ON extraction_job_files(extraction_job_id);
CREATE INDEX idx_extraction_job_files_file_id ON extraction_job_files(file_upload_id);
```

#### Templates Table
```sql
CREATE TABLE templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    file_path VARCHAR(1000) NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    status VARCHAR(50) NOT NULL DEFAULT 'draft',
    is_default BOOLEAN DEFAULT FALSE,
    usage_count INTEGER DEFAULT 0,
    created_by UUID NOT NULL REFERENCES users(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT templates_status_check CHECK (
        status IN ('draft', 'active', 'deprecated', 'archived')
    ),
    CONSTRAINT templates_version_check CHECK (version > 0)
);

CREATE INDEX idx_templates_name ON templates(name);
CREATE INDEX idx_templates_category ON templates(category);
CREATE INDEX idx_templates_status ON templates(status);
CREATE INDEX idx_templates_created_by ON templates(created_by);
CREATE UNIQUE INDEX idx_templates_name_version ON templates(name, version);
```

#### Field Mappings Table
```sql
CREATE TABLE field_mappings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    template_id UUID NOT NULL REFERENCES templates(id) ON DELETE CASCADE,
    field_name VARCHAR(255) NOT NULL,
    field_label VARCHAR(255),
    cell_reference VARCHAR(20) NOT NULL,
    sheet_name VARCHAR(100) DEFAULT 'Sheet1',
    data_type VARCHAR(50) NOT NULL,
    is_required BOOLEAN DEFAULT FALSE,
    validation_rules JSONB,
    default_value TEXT,
    transformation_rules JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT field_mappings_data_type_check CHECK (
        data_type IN ('text', 'number', 'currency', 'percentage', 'date', 'boolean')
    )
);

CREATE INDEX idx_field_mappings_template_id ON field_mappings(template_id);
CREATE INDEX idx_field_mappings_field_name ON field_mappings(field_name);
CREATE UNIQUE INDEX idx_field_mappings_template_cell ON field_mappings(template_id, cell_reference, sheet_name);
```

#### Reports Table
```sql
CREATE TABLE reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    template_id UUID NOT NULL REFERENCES templates(id),
    extraction_job_id UUID REFERENCES extraction_jobs(id),
    report_name VARCHAR(255) NOT NULL,
    file_path VARCHAR(1000),
    file_size BIGINT,
    status VARCHAR(50) NOT NULL DEFAULT 'generating',
    generation_config JSONB,
    error_message TEXT,
    download_count INTEGER DEFAULT 0,
    last_downloaded_at TIMESTAMP,
    generated_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT reports_status_check CHECK (
        status IN ('generating', 'completed', 'failed', 'expired', 'deleted')
    )
);

CREATE INDEX idx_reports_user_id ON reports(user_id);
CREATE INDEX idx_reports_template_id ON reports(template_id);
CREATE INDEX idx_reports_extraction_job_id ON reports(extraction_job_id);
CREATE INDEX idx_reports_status ON reports(status);
CREATE INDEX idx_reports_created_at ON reports(created_at);
```

#### Report Batch Table
```sql
CREATE TABLE report_batches (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    batch_name VARCHAR(255) NOT NULL,
    total_reports INTEGER NOT NULL,
    completed_reports INTEGER DEFAULT 0,
    failed_reports INTEGER DEFAULT 0,
    status VARCHAR(50) NOT NULL DEFAULT 'queued',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT report_batches_status_check CHECK (
        status IN ('queued', 'processing', 'completed', 'failed', 'cancelled')
    )
);

CREATE INDEX idx_report_batches_user_id ON report_batches(user_id);
CREATE INDEX idx_report_batches_status ON report_batches(status);
```

#### Report Batch Items Table
```sql
CREATE TABLE report_batch_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    batch_id UUID NOT NULL REFERENCES report_batches(id) ON DELETE CASCADE,
    report_id UUID REFERENCES reports(id),
    template_id UUID NOT NULL REFERENCES templates(id),
    extraction_job_id UUID REFERENCES extraction_jobs(id),
    report_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT report_batch_items_status_check CHECK (
        status IN ('pending', 'processing', 'completed', 'failed')
    )
);

CREATE INDEX idx_report_batch_items_batch_id ON report_batch_items(batch_id);
CREATE INDEX idx_report_batch_items_report_id ON report_batch_items(report_id);
```

## 2. Audit Database Schema

### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    user_id UUID,
    session_id UUID,
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id VARCHAR(255),
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    status VARCHAR(20) NOT NULL,
    execution_time INTEGER, -- in milliseconds
    request_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Partitioning by month for better performance
CREATE TABLE audit_logs_y2025m01 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE TABLE audit_logs_y2025m02 PARTITION OF audit_logs
    FOR VALUES FROM ('2025-02-01') TO ('2025-03-01');

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_resource ON audit_logs(resource_type, resource_id);
CREATE INDEX idx_audit_logs_status ON audit_logs(status);
```

### Security Events Table
```sql
CREATE TABLE security_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    user_id UUID,
    ip_address INET,
    user_agent TEXT,
    details JSONB,
    resolved BOOLEAN DEFAULT FALSE,
    resolved_by UUID,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    
    CONSTRAINT security_events_severity_check CHECK (
        severity IN ('low', 'medium', 'high', 'critical')
    )
);

CREATE INDEX idx_security_events_type ON security_events(event_type);
CREATE INDEX idx_security_events_severity ON security_events(severity);
CREATE INDEX idx_security_events_resolved ON security_events(resolved);
CREATE INDEX idx_security_events_created_at ON security_events(created_at);
```

## 3. Cache Database Schema (Redis)

### Cache Key Patterns

```
# User sessions
session:user:{user_id}:{session_id} -> session_data (TTL: 1 hour)

# File upload progress
upload:progress:{upload_id} -> progress_data (TTL: 1 day)

# Extraction job results
extraction:results:{job_id} -> results_data (TTL: 7 days)

# Template cache
template:{template_id} -> template_data (TTL: 1 hour)

# User permissions
user:permissions:{user_id} -> permissions_array (TTL: 30 minutes)

# API rate limiting
rate_limit:user:{user_id}:{endpoint} -> request_count (TTL: 1 minute)

# Report generation status
report:status:{report_id} -> generation_status (TTL: 1 day)

# Temporary file tokens
file:token:{token} -> file_metadata (TTL: 1 hour)
```

### Redis Data Structures

```redis
# User session data
HSET session:user:123:abc456 
    user_id "123"
    username "john.doe"
    role "user"
    permissions '["file.upload", "report.generate"]'
    created_at "2025-01-30T10:00:00Z"
    last_accessed "2025-01-30T10:30:00Z"

# File upload progress
HSET upload:progress:upload_123
    status "processing"
    progress "75"
    current_file "file_002"
    files_completed "2"
    files_total "3"
    estimated_completion "2025-01-30T10:35:00Z"

# Extraction results cache
SET extraction:results:job_001 '{"text_data": {...}, "table_data": [...]}'

# Rate limiting
INCR rate_limit:user:123:/api/v1/files/upload
EXPIRE rate_limit:user:123:/api/v1/files/upload 60
```

## 4. Search Database Schema (Elasticsearch)

### Document Indices

#### Application Logs Index
```json
{
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "level": { "type": "keyword" },
      "service": { "type": "keyword" },
      "message": { "type": "text" },
      "user_id": { "type": "keyword" },
      "request_id": { "type": "keyword" },
      "execution_time": { "type": "integer" },
      "error": {
        "properties": {
          "code": { "type": "keyword" },
          "message": { "type": "text" },
          "stack_trace": { "type": "text" }
        }
      }
    }
  }
}
```

#### Business Metrics Index
```json
{
  "mappings": {
    "properties": {
      "@timestamp": { "type": "date" },
      "metric_type": { "type": "keyword" },
      "metric_name": { "type": "keyword" },
      "value": { "type": "double" },
      "user_id": { "type": "keyword" },
      "template_id": { "type": "keyword" },
      "dimensions": { "type": "object" }
    }
  }
}
```

## 5. Database Relationships Diagram

```
Users ||--o{ File_Uploads : creates
Users ||--o{ Extraction_Jobs : owns
Users ||--o{ Templates : creates
Users ||--o{ Reports : generates
Users ||--o{ User_Sessions : has

Templates ||--o{ Field_Mappings : contains
Templates ||--o{ Reports : used_in

Extraction_Jobs ||--o{ Extraction_Job_Files : processes
File_Uploads ||--o{ Extraction_Job_Files : included_in

Reports }o--|| Templates : uses
Reports }o--|| Extraction_Jobs : based_on

Report_Batches ||--o{ Report_Batch_Items : contains
Reports ||--o{ Report_Batch_Items : includes
```

## 6. Database Configuration

### PostgreSQL Configuration
```postgresql
# postgresql.conf

# Memory settings
shared_buffers = 256MB
effective_cache_size = 1GB
work_mem = 4MB

# Connection settings
max_connections = 200
listen_addresses = '*'

# Logging
log_statement = 'mod'
log_duration = on
log_min_duration_statement = 1000

# Performance
random_page_cost = 1.1
effective_io_concurrency = 200

# WAL settings
wal_buffers = 16MB
checkpoint_completion_target = 0.9
```

### Redis Configuration
```redis
# redis.conf

# Memory
maxmemory 512mb
maxmemory-policy allkeys-lru

# Persistence
save 900 1
save 300 10
save 60 10000

# Security
requirepass your_secure_password
```

## 7. Data Migration Strategy

### Version Control
```sql
CREATE TABLE schema_migrations (
    version VARCHAR(50) PRIMARY KEY,
    applied_at TIMESTAMP NOT NULL DEFAULT NOW(),
    description TEXT
);
```

### Migration Scripts Structure
```
migrations/
├── 001_initial_schema.sql
├── 002_add_audit_tables.sql
├── 003_add_batch_processing.sql
└── rollback/
    ├── 001_rollback_initial.sql
    ├── 002_rollback_audit.sql
    └── 003_rollback_batch.sql
```

## 8. Backup and Recovery Strategy

### Backup Schedule
- **Full backup**: Daily at 2:00 AM
- **Incremental backup**: Every 6 hours
- **WAL archiving**: Continuous
- **Cross-region replication**: Real-time to DR site

### Recovery Procedures
```bash
# Point-in-time recovery
pg_basebackup -h primary_server -D /backup/location -U backup_user -W

# Restore from backup
pg_restore -h target_server -U postgres -d Khengleong_db backup_file.dump
```

## 9. Performance Optimization

### Indexing Strategy
- Primary keys and foreign keys
- Query-specific indexes based on access patterns
- Partial indexes for filtered queries
- Composite indexes for multi-column searches

### Query Optimization
```sql
-- Materialized views for complex aggregations
CREATE MATERIALIZED VIEW monthly_usage_stats AS
SELECT 
    DATE_TRUNC('month', created_at) as month,
    COUNT(*) as total_reports,
    COUNT(DISTINCT user_id) as active_users
FROM reports 
WHERE status = 'completed'
GROUP BY DATE_TRUNC('month', created_at);

-- Refresh strategy
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_usage_stats;
```

### Partitioning Strategy
```sql
-- Partition audit logs by month
CREATE TABLE audit_logs (
    id UUID,
    timestamp TIMESTAMP,
    -- other columns
) PARTITION BY RANGE (timestamp);
```