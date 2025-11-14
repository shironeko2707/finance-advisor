# Product Backlog

| Version | Updated Date | Updated Users | Changes |
|---------|--------------|---------------|----------|
| 0.1     | 2024-31-07   | Phan Hoàng  | Stubing the document |


This backlog is generated from the requirements review and is intended to drive development and prioritization for the AI-powered financial report automation system.

## 1. File Upload & Input

- **User can upload PDF and Excel files as input.**
  - Support drag-and-drop and file browser upload
  - Validate file types and size limits
  - Error handling for unsupported formats

## 2. Automated Data Extraction

- **AI-powered extraction of relevant fields and values from uploaded files.**
  - Support extraction from tables, paragraphs, and charts (data only)
  - Field mapping per template
  - Handle multi-file input for one report (up to 5 files)

## 3. Template Selection & Management

- **User can select a predefined Excel output template.**
  - Display available templates (40 templates for phase 1)
  - Filter/search templates by coverage (e.g., Tencent, Xiaomi, UBS, BNP, etc.)
- **User can add, update, or delete output templates.**
  - Template CRUD interface
  - Template validation and versioning (future phase)

## 4. Data Mapping & Report Generation

- **Map extracted data into correct cells of the selected Excel template.**
  - Custom mapping configuration per template
  - Support mapping from table, text, and chart data
  - Error handling for mapping failures
- **Generate report and allow user to preview and download.**
  - XLSX download
  - HTML/CSS preview
  - Preview before download

## 5. Error Handling & Validation

- **Error messages for extraction or mapping failures.**
  - User-friendly, localized error messages
  - Validation for required fields and mapping rules

## 6. Activity Logging & Audit Trail

- **Log all upload and generation activities.**
  - Store logs with timestamps and user IDs
  - Audit trail UI for admin
  - Auto-clean logs to avoid data leakage

## 7. Security & Access Control

- **Secure storage of uploaded files.**
  - Encryption at rest and in transit
  - Access control by user roles
  - Auto-clean temporary files

## 8. Performance & Scalability

- **Support up to 10 concurrent users reliably.**
  - Load and concurrency testing
- **Extract data within 5-25 seconds per document.**
  - Performance optimization and monitoring
- **Support horizontal scaling for increased user load (future phase).**
  - Modular architecture and cloud readiness

## 9. UI/UX

- **Intuitive UI for non-technical users.**
  - Simple upload and template selection
  - Tooltips, status indicators, and error messages
  - Localization support (if needed)

## 10. Configuration Management

- **Externalized, editable config files for template mappings/rules.**
  - Admin UI for config management
  - Support for editing without code changes (within 40 templates)

## 11. Uptime & Reliability

- **System uptime of 99% (excluding scheduled maintenance).**
  - Monitoring and alerting
  - Scheduled maintenance notifications

---

## Backlog Items by Priority

### Critical (Must-have for MVP)
- File upload (PDF, Excel)
- AI-powered data extraction
- Report generation via templates
- Data mapping into template cells

### High
- Template selection and management
- Error handling and validation
- Report preview and download

### Medium
- Activity logging and audit trail
- Template CRUD (add/update/delete)
- Log auto-cleaning

### Future/Low
- Integration with external repositories
- Chart image extraction and insertion
- Support for more than 40 templates

---

## Backlog Structure

| ID   | Epic/Feature                        | Description/Notes                           | Priority    |
|------|-------------------------------------|---------------------------------------------|-------------|
| PB1  | File Upload                        | User uploads PDF/Excel files                | Critical    |
| PB2  | Data Extraction                    | AI-powered extraction from uploads          | Critical    |
| PB3  | Template Selection                 | Select and manage Excel templates           | High        |
| PB4  | Data Mapping & Report Generation   | Map and generate report                     | Critical    |
| PB5  | Report Preview & Download          | Preview and export reports                  | High        |
| PB6  | Error Handling                     | Validation and error messages               | High        |
| PB7  | Logging & Audit Trail              | Record all actions                          | Medium      |
| PB8  | Template CRUD                      | Add/update/delete templates                 | Medium      |
| PB9  | Security & File Management         | Secure file storage and auto-cleaning       | Critical    |
| PB10 | Performance & Scalability          | Reliable, scalable, performant system       | High        |
| PB11 | UI/UX                              | Intuitive and user-friendly interface       | High        |
| PB12 | Configuration Management           | Externalized config for mappings/rules      | High        |
| PB13 | Uptime & Reliability               | System monitoring and alerting              | High        |
| PB14 | Future Features                    | Out-of-scope integrations, image extraction | Future      |

---

*This backlog should be reviewed and refined by the product owner and development team.*