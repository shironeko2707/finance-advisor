# Script to create symbolic link for node_modules
# This helps save disk space by linking to a shared node_modules location

param(
    [string]$TargetPath = "",
    [string]$SourcePath = "",
    [switch]$Help,
    [switch]$Remove
)

if ($Help) {
    Write-Host "Usage: .\link_node_module.ps1 [-SourcePath <path>] [-TargetPath <path>] [-Remove] [-Help]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Parameters:" -ForegroundColor Yellow
    Write-Host "  -SourcePath   Path to the actual node_modules directory (e.g., C:\shared\node_modules)" -ForegroundColor White
    Write-Host "  -TargetPath   Path where the link will be created (default: current directory)" -ForegroundColor White
    Write-Host "  -Remove       Remove existing symbolic link or junction" -ForegroundColor White
    Write-Host "  -Help         Show this help message" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\link_node_module.ps1 -SourcePath C:\shared\node_modules -TargetPath C:\myproject" -ForegroundColor White
    Write-Host "  .\link_node_module.ps1 -Remove" -ForegroundColor White
    Write-Host "  .\link_node_module.ps1" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Script will try to create a symbolic link first, and fall back to junction if permissions are insufficient." -ForegroundColor Cyan
    exit 0
}

# Interactive mode - ask for parameters if not provided
if ([string]::IsNullOrWhiteSpace($SourcePath) -and -not $Remove) {
    Write-Host ""
    Write-Host "=== Interactive Mode ===" -ForegroundColor Cyan
    Write-Host "Please provide the source directory (actual node_modules location)" -ForegroundColor Yellow
    Write-Host "Example: C:\shared\node_modules or D:\GlobalNodeModules\node_modules" -ForegroundColor Gray
    $inputSource = Read-Host "Source directory (actual node_modules path)"

    if ([string]::IsNullOrWhiteSpace($inputSource)) {
        Write-Host "❌ Source path is required!" -ForegroundColor Red
        exit 1
    }

    $SourcePath = $inputSource.Trim('"').Trim("'")
} elseif (-not [string]::IsNullOrWhiteSpace($SourcePath)) {
    $SourcePath = $SourcePath.Trim('"').Trim("'")
}

if ([string]::IsNullOrWhiteSpace($TargetPath) -and -not $Remove) {
    Write-Host "Please provide the target directory (where node_modules link will be created)" -ForegroundColor Yellow
    Write-Host "Press Enter to use current directory: $(Get-Location)" -ForegroundColor Gray
    $inputTarget = Read-Host "Target directory"

    if ([string]::IsNullOrWhiteSpace($inputTarget)) {
        $TargetPath = Get-Location
    } else {
        $TargetPath = $inputTarget.Trim('"').Trim("'")
    }
} elseif ([string]::IsNullOrWhiteSpace($TargetPath)) {
    $TargetPath = Get-Location
} else {
    $TargetPath = $TargetPath.Trim('"').Trim("'")
}

# Validate target path
if (-not (Test-Path $TargetPath)) {
    Write-Host "❌ Target path does not exist: $TargetPath" -ForegroundColor Red
    exit 1
}

$nodeModulesPath = Join-Path $TargetPath "node_modules"

Write-Host "Node.js Link Manager (SymLink/Junction)" -ForegroundColor Cyan
Write-Host "Target directory: $TargetPath" -ForegroundColor Gray

# Check if removing link
if ($Remove) {
    if (Test-Path $nodeModulesPath) {
        $item = Get-Item $nodeModulesPath
        if ($item.LinkType -eq "SymbolicLink" -or $item.LinkType -eq "Junction") {
            Write-Host "Removing $($item.LinkType.ToLower())..." -ForegroundColor Yellow
            Remove-Item $nodeModulesPath -Force
            Write-Host "✅ $($item.LinkType) removed successfully!" -ForegroundColor Green
        } else {
            Write-Host "❌ node_modules is not a symbolic link or junction, it's a regular directory" -ForegroundColor Red
            Write-Host "Use 'Remove-Item node_modules -Recurse -Force' to delete regular directory" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ node_modules directory does not exist" -ForegroundColor Red
    }
    exit 0
}

# Validate source path (only for non-remove operations)
if (-not (Test-Path $SourcePath)) {
    Write-Host "❌ Source path does not exist: $SourcePath" -ForegroundColor Red
    exit 1
}

# Function to try creating symbolic link with fallback to junction
function Create-LinkWithFallback {
    param(
        [string]$LinkPath,
        [string]$SourcePath
    )

    # First, try creating a symbolic link
    Write-Host "Attempting to create symbolic link..." -ForegroundColor Yellow
    try {
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $SourcePath -ErrorAction Stop | Out-Null
        Write-Host "✅ Symbolic link created successfully!" -ForegroundColor Green
        return "SymbolicLink"
    } catch {
        Write-Host "⚠️  Failed to create symbolic link: $($_.Exception.Message)" -ForegroundColor Yellow
        Write-Host "Falling back to junction..." -ForegroundColor Yellow

        # Fallback to junction
        try {
            New-Item -ItemType Junction -Path $LinkPath -Target $SourcePath -ErrorAction Stop | Out-Null
            Write-Host "✅ Junction created successfully!" -ForegroundColor Green
            return "Junction"
        } catch {
            Write-Host "❌ Failed to create junction: $($_.Exception.Message)" -ForegroundColor Red
            throw "Both symbolic link and junction creation failed"
        }
    }
}

# Check if node_modules already exists
if (Test-Path $nodeModulesPath) {
    $item = Get-Item $nodeModulesPath
    if ($item.LinkType -eq "SymbolicLink" -or $item.LinkType -eq "Junction") {
        Write-Host "⚠️  $($item.LinkType) already exists" -ForegroundColor Yellow
        Write-Host "Current target: $($item.Target)" -ForegroundColor Gray
        $replace = Read-Host "Do you want to replace it? (y/N)"
        if ($replace -eq "y" -or $replace -eq "Y") {
            Remove-Item $nodeModulesPath -Force
            Write-Host "✅ Removed existing $($item.LinkType.ToLower())" -ForegroundColor Green
        } else {
            exit 0
        }
    } else {
        Write-Host "⚠️  Regular node_modules directory already exists in target location" -ForegroundColor Yellow
        $backup = Read-Host "Do you want to backup the existing node_modules and replace it with link? (y/N)"
        if ($backup -eq "y" -or $backup -eq "Y") {
            $backupPath = "$nodeModulesPath.backup.$(Get-Date -Format 'yyyyMMdd-HHmmss')"
            Move-Item $nodeModulesPath $backupPath
            Write-Host "✅ Backed up existing node_modules to: $backupPath" -ForegroundColor Green
        } else {
            exit 0
        }
    }
}

# Create link with fallback
Write-Host "Creating link..." -ForegroundColor Yellow
Write-Host "Link Path: $nodeModulesPath" -ForegroundColor Gray
Write-Host "Source: $SourcePath" -ForegroundColor Gray

try {
    $linkType = Create-LinkWithFallback -LinkPath $nodeModulesPath -SourcePath $SourcePath

    # Verify the link
    $link = Get-Item $nodeModulesPath
    if ($link.LinkType -eq $linkType) {
        Write-Host "✅ Verification passed - $($linkType.ToLower()) is working" -ForegroundColor Green
        Write-Host "Points to: $($link.Target)" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Failed to create any type of link: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "This might be due to:" -ForegroundColor Yellow
    Write-Host "1. Insufficient privileges (try running as Administrator)" -ForegroundColor White
    Write-Host "2. Source path is invalid or inaccessible" -ForegroundColor White
    Write-Host "3. File system doesn't support links" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "🎉 Done! Your node_modules is now linked." -ForegroundColor Green
Write-Host "Link created at: $nodeModulesPath" -ForegroundColor Cyan
Write-Host "Points to: $SourcePath" -ForegroundColor Cyan
