## System Components

### User Management
- User accounts with roles and permissions
- Authentication and authorization
- Profile management

### Template System
- Report template creation and management
- Template versioning and validation
- Custom template configurations

### File Processing
- Multiple file format support
- Secure upload handling
- File validation and processing

### AI-Generated Content
- Smart report generation
- Template-based content creation
- AI model integration

### Storage Organization
```
storage/
├── lengkeng.db           # Main database (SQLite for dev)
├── uploads/              # User uploaded files
├── templates/            # Template files
├── generated/            # AI-generated content
└── exports/             # Exported reports
```

## Database Structure

The application uses a single database that will automatically expand to include tables for:

- **Users**: User accounts, roles, and authentication
- **Templates**: Report templates and configurations  
- **Files**: Uploaded files metadata and relationships
- **Generated Content**: AI-generated reports and content
- **Audit Logs**: System activity and changes
- **Settings**: Application configuration

The database schema is automatically created and managed by SQLAlchemy migrations.