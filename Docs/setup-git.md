# Guide to Setting Up a Git Repository

To enable MkDocs to display the creation and modification dates of documents, you need to set up a Git repository.

## Initialize Git Repository

```bash
# Initialize git repo
git init

# Add all files
git add .

# First commit
git commit -m "Initial commit: Setup MkDocs documentation"

# (Optional) Add remote repository
git remote add origin https://source.cmcglobal.com.vn/Khengleong-docs.git
git push -u origin main
```

## After Setting Up Git

1. **Git revision dates will work** - MkDocs will display creation and modification dates.
2. **Warnings will disappear** - The git-revision-date plugin will pull information from git logs.
3. **Dates will update automatically** - Each commit will automatically update the dates.

## Recommended Workflow

```bash
# Add new files or edit existing ones
git add docs/new-file.md

# Commit with a clear message
git commit -m "Add new documentation: [description]"

# Push to remote (if applicable)
git push
```

## Integration with MkDocs

The `mkdocs.yml` file has been configured with the plugin:

```yaml
plugins:
  - git-revision-date-localized:
      enable_creation_date: true
```

This plugin will:
- Display the creation date of the first file
- Show the most recent modification date
- Automatically format according to the locale