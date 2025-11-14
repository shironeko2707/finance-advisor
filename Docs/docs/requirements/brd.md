# Project Requirements Review
| Version | Updated Date | Updated Users | Changes |
|---------|--------------|---------------|----------|
| 0.1     | 2024-31-07   | Hường  | Stubing the document |

## 1. Project Scope

### In Scope
- **File Uploads:** Users can upload PDF and Excel files as input.
- **AI-Powered Report Generation:** System automates financial report creation using up to 40 internal templates (input: up to 5 files/report; data from tables, some from text paragraphs and charts).
- **Custom Mapping Logic:** Maps extracted data to designated Excel cells.
- **Template Management:** Manages up to 40 Excel output templates (e.g., bond/stock coverage for Tencent, Xiaomi, UBS, BNP, etc.; quarterly CPF statistics).
- **Output Preview & Download:** Users can preview and download generated Excel reports.
- **Multi-User Access:** Accessible by multiple desktop users via Chrome browser.
- **Template Limitation:** Only the provided 40 templates are supported in phase 1.

### Out of Scope
- Manual data entry system.
- Integration with external third-party document repositories (optional for future phase).
- Chart image extraction and insertion into reports.
- Supporting output templates beyond the initial 40.

---

## 2. Business Drivers

- **Reduce Workload & Costs:** Automation reduces manual labor and errors; staff can focus on analysis rather than formatting.
- **Faster Turnaround:** Cuts report delivery time from hours/days to near real-time.
- **Standardization:** Unlocks data from PDFs and messy Excels, enabling structured decision-making.

---

## 3. Current Process

*(Not provided in detail; assumed manual, labor-intensive, error-prone and slow.)*

---

## 4. Proposed Process

*(Implied: Automated, AI-driven extraction, mapping to templates, preview, and download via browser.)*

---

## 5. Business Requirements

| ID   | Requirement                                                                                  | Priority   | Notes                          |
|------|---------------------------------------------------------------------------------------------|------------|---------------------------------|
| BR 1 | User shall be able to upload input files (PDF, Excel)                                        | Critical   |                                 |
| BR 2 | System shall use AI to extract relevant fields and values from uploaded files                 | Critical   |                                 |
| BR 3 | System shall allow users to select a predefined output Excel template                        | High       | Templates stored in system      |
| BR 4 | System shall map extracted data into correct cells of the selected Excel template            | High       | Mapping config per template     |
| BR 5 | System shall allow preview and download of the generated report                              | High       | XLSX download + HTML preview    |
| BR 6 | System shall log all upload and generation activities                                        | Medium     | For audit trail                 |
| BR 7 | User shall be able to manage (add/update/delete) output templates                            | Medium     | Template management module      |
| BR 8 | Users shall receive error messages if extraction or mapping fails                            | High       | Includes validation errors      |

### Priority Rating Table

| Value | Rating    | Description                                                                                 |
|-------|-----------|--------------------------------------------------------------------------------------------|
| 1     | Critical  | Essential for project success; project not possible without it.                             |
| 2     | High      | High priority; project can proceed as MVP without it.                                       |
| 3     | Medium    | Adds value; project can proceed as MVP without it.                                          |
| 4     | Low       | Nice to have; not necessary for project success.                                            |
| 5     | Future    | Outside current scope; potential future feature.                                            |

---

## 6. Non-Functional Requirements (NFRs)

| ID     | Requirement                                                                                                  |
|--------|-------------------------------------------------------------------------------------------------------------|
| NFR 1  | Support up to 10 concurrent users reliably                                                                   |
| NFR 2  | Extract data within 5–25 seconds per document under normal load                                              |
| NFR 3  | Support horizontal scaling for more users/documents in future phases                                         |
| NFR 4  | 99% uptime, excluding scheduled maintenance                                                                  |
| NFR 5  | Secure storage of uploaded files (access control, encryption at rest/in transit)                             |
| NFR 6  | Auto-clean temporary files/logs to prevent data leakage                                                      |
| NFR 7  | Modular design for easy updates (e.g., AI model)                                                             |
| NFR 8  | Externalized, editable config files for template mappings/rules (within 40 templates for phase 1)            |
| NFR 9  | Intuitive UI for non-technical users; upload, manage templates, select template, preview/download, tooltips  |
| NFR 10 | Audit/log all actions (upload, generate, error) with timestamps and user IDs                                 |

---

## 7. Observations & Recommendations

- **Scope Control:** Strictly limit to 40 templates for phase 1; future expansion should be considered in architecture.
- **Security:** Strong emphasis on file security and auditability is appropriate for financial data.
- **Scalability:** Horizontal scaling and modularity are forward-looking and should be part of design from the start.
- **User Experience:** Clear requirements for non-technical users suggest UI/UX should be a primary focus.
- **Template Management:** Ability to add/update/delete templates is medium priority but will aid future flexibility.

---

## 8. Next Steps / Questions

- More details needed on the current process and pain points for a more complete analysis.
- Confirm if chart extraction is to be considered in future phases.
- Clarify if template management (BR 7) includes versioning/history or just CRUD.
