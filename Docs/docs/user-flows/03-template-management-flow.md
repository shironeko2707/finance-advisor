# Template Management Flow - Quản Lý Template

## Overview

This document describes the administrative user interaction flow for managing output templates in the Khengleong system. This includes creating, updating, deleting, and configuring templates within the constraint of 40 predefined templates for Phase 1.

## Business Requirements Supported

- **BR 7**: User shall be able to manage (add/update/delete) output templates - Medium Priority
- **NFR 8**: Externalized, editable config files for template mappings/rules
- **NFR 10**: Audit/log all actions with timestamps and user IDs

## Template Management Flow Diagram

```mermaid
graph TD
    A[Admin User Access] --> B[Navigate to Template Management]
    B --> C[Load Template Management Dashboard]
    C --> D[Display Template Library Overview]
    D --> E{Select Management Action}
    
    E -->|View Templates| F[Template List View]
    E -->|Add Template| G[Create New Template Flow]
    E -->|Edit Template| H[Edit Existing Template Flow]
    E -->|Delete Template| I[Delete Template Flow]
    E -->|Import/Export| J[Template Import/Export Flow]
    
    %% View Templates Flow
    F --> F1[Display Template Grid]
    F1 --> F2[Filter and Search Options]
    F2 --> F3{User Action}
    F3 -->|Select Template| F4[View Template Details]
    F3 -->|Edit Template| H
    F3 -->|Delete Template| I
    F4 --> E
    
    %% Create New Template Flow
    G --> G1[Check Template Limit]
    G1 --> G2{Under 40 Limit?}
    G2 -->|No| G3[Show Limit Error]
    G2 -->|Yes| G4[Template Creation Wizard]
    G3 --> E
    G4 --> G5[Upload Excel Template File]
    G5 --> G6[Template Validation]
    G6 --> G7{Validation Success?}
    G7 -->|No| G8[Show Validation Errors]
    G7 -->|Yes| G9[Configure Template Metadata]
    G8 --> G5
    G9 --> G10[Define Data Mapping Rules]
    G10 --> G11[Set Field Validations]
    G11 --> G12[Preview Template Configuration]
    G12 --> G13{User Confirms?}
    G13 -->|No| G9
    G13 -->|Yes| G14[Save Template]
    G14 --> G15[Log Creation Activity]
    G15 --> G16[Success Confirmation]
    G16 --> E
    
    %% Edit Template Flow
    H --> H1[Load Template for Editing]
    H1 --> H2[Version Control Check]
    H2 --> H3{Template in Use?}
    H3 -->|Yes| H4[Create New Version]
    H3 -->|No| H5[Edit Current Version]
    H4 --> H6[Version Management Interface]
    H5 --> H7[Template Editor Interface]
    H6 --> H7
    H7 --> H8[Modify Template Properties]
    H8 --> H9{Save Changes?}
    H9 -->|No| H10[Discard Changes]
    H9 -->|Yes| H11[Validate Changes]
    H10 --> E
    H11 --> H12{Validation Success?}
    H12 -->|No| H13[Show Validation Errors]
    H12 -->|Yes| H14[Save Updated Template]
    H13 --> H8
    H14 --> H15[Log Update Activity]
    H15 --> H16[Success Confirmation]
    H16 --> E
    
    %% Delete Template Flow
    I --> I1[Load Template Details]
    I1 --> I2[Check Template Usage]
    I2 --> I3{Template in Use?}
    I3 -->|Yes| I4[Show Usage Warning]
    I3 -->|No| I5[Deletion Confirmation Dialog]
    I4 --> I6[Provide Usage Details]
    I6 --> I7{Force Delete?}
    I7 -->|No| E
    I7 -->|Yes| I8[Archive Active Reports]
    I5 --> I9{User Confirms?}
    I9 -->|No| E
    I9 -->|Yes| I10[Delete Template]
    I8 --> I10
    I10 --> I11[Log Deletion Activity]
    I11 --> I12[Success Confirmation]
    I12 --> E
    
    %% Import/Export Flow
    J --> J1{Import or Export?}
    J1 -->|Import| J2[Template Import Flow]
    J1 -->|Export| J3[Template Export Flow]
    
    J2 --> J4[Upload Template Package]
    J4 --> J5[Validate Import Package]
    J5 --> J6{Validation Success?}
    J6 -->|No| J7[Show Import Errors]
    J6 -->|Yes| J8[Preview Import Changes]
    J7 --> J2
    J8 --> J9{User Confirms Import?}
    J9 -->|No| E
    J9 -->|Yes| J10[Import Templates]
    J10 --> J11[Log Import Activity]
    J11 --> E
    
    J3 --> J12[Select Templates to Export]
    J12 --> J13[Configure Export Options]
    J13 --> J14[Generate Export Package]
    J14 --> J15[Download Package]
    J15 --> J16[Log Export Activity]
    J16 --> E
    
    %% Error Handling
    G6 -.->|System Error| K1[Template Validation Error]
    H11 -.->|System Error| K2[Template Update Error]
    I10 -.->|System Error| K3[Template Deletion Error]
    J5 -.->|System Error| K4[Import/Export Error]
    
    K1 --> K5[Show Error Message & Retry]
    K2 --> K6[Show Error Message & Retry]
    K3 --> K7[Show Error Message & Retry]
    K4 --> K8[Show Error Message & Retry]
    
    K5 --> G4
    K6 --> H7
    K7 --> I
    K8 --> J
    
    %% Styling
    classDef userAction fill:#e3f2fd,stroke:#1976d2,stroke-width:2px
    classDef systemProcess fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    classDef decision fill:#fff3e0,stroke:#f57c00,stroke-width:2px
    classDef error fill:#ffebee,stroke:#d32f2f,stroke-width:2px
    classDef success fill:#e8f5e8,stroke:#388e3c,stroke-width:2px
    classDef adminAction fill:#fff8e1,stroke:#ff8f00,stroke-width:2px
    
    class F3,G13,H9,I9,J9 userAction
    class C,G6,G15,H11,H15,I11,J11 systemProcess
    class E,G2,G7,H3,H12,I3,I7,J1,J6 decision
    class G3,G8,H13,K1,K2,K3,K4,K5,K6,K7,K8 error
    class G16,H16,I12 success
    class A,B,D,G4,H7,I1,J2,J3 adminAction
```

## Template Management Dashboard

### Main Interface Layout

```
┌─────────────────────────────────────────────────────────┐
│  🛠️ Template Management Dashboard                        │
│                                                         │
│  📊 Library Overview                                     │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Total Templates: 37/40        Active: 35             │ │
│  │ Recent Activity: 3 updates    Categories: 6          │ │
│  │                                                     │ │
│  │ [📝 Add New Template] [📤 Import] [📥 Export]        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  🔍 Filter Templates                                     │
│  Category: [All ▼] Status: [All ▼] Last Modified: [All ▼] │
│  Search: [Enter template name...] [🔍]                  │
│                                                         │
│  📋 Template Library                                     │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Template Name          Category    Status   Actions  │ │
│  │ ─────────────          ────────    ──────   ─────── │ │
│  │ Tencent Bond Analysis  Bond        Active   [E][D]  │ │
│  │ Xiaomi Stock Report    Stock       Active   [E][D]  │ │
│  │ CPF Quarterly Stats    Quarterly   Draft    [E][D]  │ │
│  │ UBS Bond Coverage      Bond        Active   [E][D]  │ │
│  │ Risk Assessment v2     Risk        Inactive [E][D]  │ │
│  └─────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────┘

Legend: [E] = Edit, [D] = Delete, [V] = View Details
```

## Detailed Management Flows

### 1. Create New Template Flow

#### Step 1: Template Limit Check
```mermaid
graph LR
    A[Add New Template] --> B{Check Current Count}
    B -->|< 40| C[Proceed to Creation]
    B -->|= 40| D[Show Limit Message]
    D --> E[Suggest Delete/Archive]
    E --> F[Return to Dashboard]
```

#### Step 2: Template Creation Wizard

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  📝 Create New Template - Step 1 of 4                   │
│                                                         │
│  📁 Upload Excel Template File                          │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Drag and drop your Excel template here             │ │
│  │               or                                   │ │
│  │        [Choose Excel File]                         │ │
│  │                                                     │ │
│  │ Requirements:                                       │ │
│  │ • Excel format (.xlsx, .xlsm)                     │ │
│  │ • Maximum 10MB file size                          │ │
│  │ • Named cell ranges for data fields               │ │
│  │ • No external links or macros                     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [⬅️ Cancel] [➡️ Next Step]                              │
└─────────────────────────────────────────────────────────┘
```

#### Step 3: Template Metadata Configuration

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  📝 Create New Template - Step 2 of 4                   │
│                                                         │
│  📋 Template Information                                 │
│  Template Name: [_________________________]             │
│  Description:   [_________________________]             │
│                 [_________________________]             │
│  Category:      [Bond Coverage ▼]                       │
│  Industry:      [Financial Services ▼]                  │
│  Frequency:     [Quarterly ▼]                          │
│  Complexity:    [● Basic ○ Intermediate ○ Advanced]     │
│                                                         │
│  🏷️ Tags (comma-separated):                             │
│  [bonds, tencent, analysis, quarterly]                  │
│                                                         │
│  📄 Template Preview:                                    │
│  [Excel preview showing template structure]             │
│                                                         │
│  [⬅️ Previous] [➡️ Next Step]                            │
└─────────────────────────────────────────────────────────┘
```

#### Step 4: Data Mapping Configuration

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  📝 Create New Template - Step 3 of 4                   │
│                                                         │
│  🔗 Configure Data Mapping Rules                        │
│                                                         │
│  ┌─────────────────────┐ ┌─────────────────────────────┐ │
│  │ Template Fields     │ │ Data Field Configuration    │ │
│  │                     │ │                             │ │
│  │ ✓ A1: Bond_ISIN     │ │ Field Name: Bond ISIN       │ │
│  │ ✓ B5: Credit_Rating │ │ Data Type: Text             │ │
│  │ ✓ C10: Yield_Rate   │ │ Required: ☑️                 │ │
│  │ ✓ D15: Coupon_Rate  │ │ Validation: ISIN Format     │ │
│  │ ○ E20: Maturity     │ │ Default Value: [___]        │ │
│  │ ○ F25: Risk_Score   │ │                             │ │
│  │                     │ │ [Save Field Config]         │ │
│  └─────────────────────┘ └─────────────────────────────┘ │
│                                                         │
│  Field Mapping Status: 4/6 fields configured           │
│  [⬅️ Previous] [Test Mapping] [➡️ Next Step]             │
└─────────────────────────────────────────────────────────┘
```

### 2. Edit Template Flow

#### Version Control Handling

```mermaid
graph TD
    A[Edit Template Request] --> B{Template Currently in Use?}
    B -->|Yes| C[Check Active Reports]
    B -->|No| D[Direct Edit Mode]
    
    C --> E{Reports in Progress?}
    E -->|Yes| F[Create New Version]
    E -->|No| G[Create Version Branch]
    
    F --> H[Version Management Interface]
    G --> H
    H --> I[Edit Template Version]
    I --> J[Version Testing & Validation]
    J --> K{Ready to Publish?}
    K -->|No| I
    K -->|Yes| L[Publish New Version]
    L --> M[Deprecate Old Version]
    
    D --> N[Edit Current Template]
    N --> O[Save Changes]
```

#### Template Editor Interface

**Interface Layout**:
```
┌─────────────────────────────────────────────────────────┐
│  ✏️ Edit Template: Tencent Bond Analysis v2.1           │
│                                                         │
│  ⚠️ Template in use by 3 active reports                 │
│  [📊 View Usage] [🔄 Create New Version] [⚡ Edit Current] │
│                                                         │
│  📋 Template Properties                                  │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Name: [Tencent Bond Analysis_________]              │ │
│  │ Version: [2.1___] Status: [Active ▼]               │ │
│  │ Category: [Bond Coverage ▼]                        │ │
│  │ Last Modified: 2024-01-15 by admin@company.com     │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  📄 Template File                                       │
│  Current: tencent_bond_v2.1.xlsx [📥 Download] [🔄 Replace] │
│                                                         │
│  🔗 Data Mapping Rules (6 fields configured)           │
│  [⚙️ Manage Field Mappings] [🧪 Test with Sample Data]   │
│                                                         │
│  📊 Usage Statistics                                     │
│  Used in 45 reports | Success rate: 96% | Avg time: 12s │
│                                                         │
│  [💾 Save Changes] [❌ Cancel] [🗑️ Delete Template]       │
└─────────────────────────────────────────────────────────┘
```

### 3. Delete Template Flow

#### Safety Checks and Confirmation

```mermaid
graph TD
    A[Delete Template Request] --> B[Load Template Usage Data]
    B --> C{Template in Active Use?}
    
    C -->|Yes| D[Show Usage Warning]
    C -->|No| E[Simple Confirmation Dialog]
    
    D --> F[Display Active Reports List]
    F --> G{Force Delete Option?}
    G -->|No| H[Cancel Deletion]
    G -->|Yes| I[Archive Active Reports]
    
    E --> J{User Confirms?}
    J -->|No| H
    J -->|Yes| K[Soft Delete Template]
    
    I --> L[Mark Template as Deleted]
    K --> L
    L --> M[Log Deletion Activity]
    M --> N[Update Template Count]
    N --> O[Success Confirmation]
    
    H --> P[Return to Management Dashboard]
```

#### Deletion Confirmation Interface

**For Template in Use**:
```
┌─────────────────────────────────────────────────────────┐
│  ⚠️ Delete Template: Tencent Bond Analysis               │
│                                                         │
│  🚨 WARNING: This template is currently being used      │
│                                                         │
│  Active Usage:                                          │
│  • 3 reports currently in progress                     │
│  • 2 scheduled reports using this template             │
│  • Last used: 2 hours ago                              │
│                                                         │
│  ⚙️ Options:                                            │
│  ○ Cancel deletion (recommended)                        │
│  ○ Archive template (disable new usage)                │
│  ○ Force delete (will affect active reports)           │
│                                                         │
│  [📋 View Active Reports] [❌ Cancel] [🗑️ Proceed]       │
└─────────────────────────────────────────────────────────┘
```

**For Unused Template**:
```
┌─────────────────────────────────────────────────────────┐
│  🗑️ Delete Template: Old Risk Assessment                │
│                                                         │
│  ℹ️ This template is not currently being used           │
│                                                         │
│  Template Details:                                      │
│  • Created: 2023-06-15                                 │
│  • Last used: 2023-08-22                               │
│  • Total usage: 12 reports                             │
│  • Status: Inactive                                    │
│                                                         │
│  ⚠️ This action cannot be undone                        │
│                                                         │
│  [❌ Cancel] [🗑️ Delete Permanently]                     │
└─────────────────────────────────────────────────────────┘
```

### 4. Import/Export Flow

#### Template Package Structure

```
template_package.zip
├── templates/
│   ├── template_01.xlsx
│   ├── template_02.xlsx
│   └── template_03.xlsx
├── configurations/
│   ├── template_01_config.json
│   ├── template_02_config.json
│   └── template_03_config.json
├── metadata/
│   ├── package_info.json
│   └── version_info.json
└── documentation/
    ├── index.md
    └── field_mappings.md
```

#### Import Interface

```
┌─────────────────────────────────────────────────────────┐
│  📤 Import Templates                                     │
│                                                         │
│  📁 Upload Template Package                             │
│  [Choose .zip file] or drag and drop                   │
│                                                         │
│  📋 Import Preview                                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Package: quarterly_templates_v2.1.zip              │ │
│  │ Contains: 4 templates                               │ │
│  │                                                     │ │
│  │ ✓ CPF Quarterly Report v3.0    (New)               │ │
│  │ ⚠ Risk Assessment v2.1         (Update existing)   │ │
│  │ ✓ Compliance Report v1.5       (New)               │ │
│  │ ❌ Bond Analysis v2.0           (Validation failed) │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  ⚙️ Import Options                                       │
│  ☑️ Create backup before import                         │
│  ☑️ Skip templates with validation errors               │
│  ☐ Overwrite existing templates                        │
│                                                         │
│  [❌ Cancel] [📤 Import Selected Templates]              │
└─────────────────────────────────────────────────────────┘
```

## Access Control and Permissions

### Role-Based Access

| Role | Create | Read | Update | Delete | Import/Export |
|------|--------|------|--------|--------|---------------|
| **Super Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Template Admin** | ✅ | ✅ | ✅ | ⚠️* | ✅ |
| **Analyst** | ❌ | ✅ | ⚠️** | ❌ | ❌ |
| **Viewer** | ❌ | ✅ | ❌ | ❌ | ❌ |

*Template Admin can delete only unused templates
**Analyst can update template metadata but not mapping rules

### Permission Validation

```mermaid
graph TD
    A[User Action Request] --> B[Check User Role]
    B --> C{Action Permitted?}
    C -->|Yes| D[Check Resource Permissions]
    C -->|No| E[Access Denied Message]
    
    D --> F{Resource Access OK?}
    F -->|Yes| G[Proceed with Action]
    F -->|No| H[Resource Access Denied]
    
    G --> I[Log Activity]
    E --> J[Log Access Attempt]
    H --> J
```

## Validation Rules

### Template File Validation

| Validation Type | Rules | Error Handling |
|----------------|-------|----------------|
| **File Format** | .xlsx, .xlsm only | "Only Excel files (.xlsx, .xlsm) are supported" |
| **File Size** | Maximum 10MB | "File size exceeds 10MB limit. Please compress or optimize." |
| **Structure** | Valid Excel structure | "File appears corrupted. Please check and re-upload." |
| **Macros** | No macros allowed (security) | "Macros not permitted. Please save as .xlsx format." |
| **External Links** | No external references | "External links found. Please embed all data." |
| **Named Ranges** | Required for data fields | "Named ranges required for data mapping." |

### Metadata Validation

| Field | Validation Rules | Error Messages |
|-------|------------------|----------------|
| **Template Name** | 3-100 characters, unique | "Name must be unique and 3-100 characters" |
| **Description** | Max 500 characters | "Description too long (max 500 characters)" |
| **Category** | Must exist in predefined list | "Please select a valid category" |
| **Tags** | Max 10 tags, 50 chars each | "Maximum 10 tags, 50 characters each" |

### Data Mapping Validation

```mermaid
graph TD
    A[Field Mapping] --> B[Check Field Name]
    B --> C{Valid Field Name?}
    C -->|No| D[Invalid Name Error]
    C -->|Yes| E[Check Data Type]
    
    E --> F{Compatible Type?}
    F -->|No| G[Type Mismatch Error]
    F -->|Yes| H[Check Validation Rules]
    
    H --> I{Rules Valid?}
    I -->|No| J[Validation Rule Error]
    I -->|Yes| K[Check Cell Reference]
    
    K --> L{Valid Cell Reference?}
    L -->|No| M[Cell Reference Error]
    L -->|Yes| N[Mapping Valid]
```

## Audit and Logging

### Activity Logging

All template management activities are logged with:

| Field | Description | Example |
|-------|-------------|---------|
| **Timestamp** | ISO 8601 format | 2024-01-15T14:30:25Z |
| **User ID** | Authenticated user identifier | admin@company.com |
| **Action Type** | CREATE, UPDATE, DELETE, IMPORT, EXPORT | UPDATE |
| **Template ID** | Unique template identifier | TMPL_001 |
| **Template Name** | Human-readable template name | Tencent Bond Analysis |
| **Changes** | JSON diff of changes | {"name": {"old": "...", "new": "..."}} |
| **IP Address** | User's IP address | 192.168.1.100 |
| **User Agent** | Browser/client information | Chrome/96.0 |
| **Result** | SUCCESS, FAILURE, PARTIAL | SUCCESS |
| **Error Details** | Error message if failed | null |

### Audit Trail Interface

```
┌─────────────────────────────────────────────────────────┐
│  📋 Template Management Audit Trail                     │
│                                                         │
│  🔍 Filter: [Last 30 days ▼] User: [All ▼] Action: [All ▼] │
│                                                         │
│  📊 Activity Log                                        │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ Time                Action    Template         User │ │
│  │ ────                ──────    ────────         ──── │ │
│  │ 2024-01-15 14:30   UPDATE    Tencent Bond     admin │ │
│  │ 2024-01-15 13:15   CREATE    Risk Report v2   alice │ │
│  │ 2024-01-15 11:45   DELETE    Old Template     admin │ │
│  │ 2024-01-15 10:20   IMPORT    Package v1.2     bob   │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                         │
│  [📥 Export Audit Log] [🔄 Refresh]                      │
└─────────────────────────────────────────────────────────┘
```

## Error Handling and Recovery

### Common Error Scenarios

| Error Type | Cause | Recovery Action | Prevention |
|------------|-------|-----------------|------------|
| **Template Limit Exceeded** | Trying to create 41st template | Suggest archiving unused templates | Show count in dashboard |
| **File Upload Failed** | Network/server issues | Retry mechanism with exponential backoff | Progress indicators, chunked upload |
| **Validation Failed** | Invalid template structure | Detailed error messages with examples | Pre-upload validation |
| **Concurrent Edit Conflict** | Multiple users editing same template | Version conflict resolution interface | Version locking mechanism |
| **Permission Denied** | Insufficient user permissions | Clear permission error messages | Role-based UI hiding |

### Error Recovery Mechanisms

```mermaid
graph TD
    A[Error Detected] --> B{Error Type?}
    
    B -->|Validation Error| C[Show Detailed Error]
    B -->|Permission Error| D[Show Access Message]
    B -->|System Error| E[Show Generic Error]
    B -->|Conflict Error| F[Show Conflict Resolution]
    
    C --> G[Provide Correction Guidance]
    D --> H[Suggest Contact Admin]
    E --> I[Offer Retry Option]
    F --> J[Version Merge Interface]
    
    G --> K[Return to Edit Mode]
    H --> L[Return to Dashboard]
    I --> M[Retry Operation]
    J --> N[Resolve Conflicts]
```

## Integration Points

### 1. With Template Selection Flow
- Real-time template availability updates
- Template metadata synchronization
- Usage statistics feedback

### 2. With Document Processing
- Template configuration validation
- Field mapping rule enforcement
- Processing optimization based on template complexity

### 3. With User Authentication
- Role-based access control
- Permission validation
- Activity attribution

### 4. With Audit System
- Comprehensive activity logging
- Compliance reporting
- Security monitoring

## Performance Considerations

### Scalability Measures
- **Template Caching**: Frequently accessed templates cached in memory
- **Lazy Loading**: Template details loaded on demand
- **Background Processing**: Heavy operations processed asynchronously
- **Database Optimization**: Indexed queries for template searches

### User Experience Optimization
- **Progressive Loading**: Show template list before loading details
- **Real-time Updates**: Live status updates during operations
- **Offline Capabilities**: Cache templates for offline viewing
- **Responsive Design**: Optimize for different screen sizes