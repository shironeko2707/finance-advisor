param(
    [switch]$alone,
    [switch]$down,
    [switch]$logs,
    [switch]$help,
    [switch]$no_update
)

function Check-GitUpdate {
    if (-not $no_update) {
        Write-Host "Checking for code updates..." -ForegroundColor Yellow

        # Check Git status
        Write-Host "Current Git status:" -ForegroundColor Gray
        git status --porcelain

        # Fetch latest changes from remote
        Write-Host "Fetching latest changes from remote..." -ForegroundColor Gray
        git fetch origin

        # Check if there are updates available
        $localCommit = git rev-parse HEAD
        $remoteCommit = git rev-parse origin/main 2>$null

        if (-not $remoteCommit) {
            $remoteCommit = git rev-parse origin/master 2>$null
        }

        if ($localCommit -ne $remoteCommit) {
            Write-Host "New code updates found! Pulling changes..." -ForegroundColor Green
            git pull origin main 2>$null
            if ($LASTEXITCODE -ne 0) {
                git pull origin master 2>$null
            }

            if ($LASTEXITCODE -eq 0) {
                Write-Host "Code updated successfully!" -ForegroundColor Green
            } else {
                Write-Host "Error pulling updates. Please check for conflicts." -ForegroundColor Red
                exit 1
            }
        } else {
            Write-Host "No new updates found. Using current code." -ForegroundColor Cyan
        }
    }
}

if ($help) {
    Write-Host "Usage: .\run_docker.ps1 [OPTIONS]" -ForegroundColor Green
    Write-Host "  -alone        Run only the main application (uses existing PostgreSQL/RabbitMQ)" -ForegroundColor White
    Write-Host "  -down         Stop all containers" -ForegroundColor White
    Write-Host "  -logs         Show logs" -ForegroundColor White
    Write-Host "  -no_update    Skip Git update check" -ForegroundColor White
    Write-Host "  -help         Show this help" -ForegroundColor White
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\run_docker.ps1                 # Pull latest code, build and run all services" -ForegroundColor Gray
    Write-Host "  .\run_docker.ps1 -alone          # Pull latest code, build main app only (use existing DB/MQ)" -ForegroundColor Gray
    Write-Host "  .\run_docker.ps1 -no_update      # Skip Git update, build and run all services" -ForegroundColor Gray
    Write-Host "  .\run_docker.ps1 -down           # Stop all services" -ForegroundColor Gray
    exit 0
}

# Create storage directories if they don't exist
$storageDirectories = @("storage", "storage\uploads", "storage\templates", "storage\generated", "storage\exports", "storage\cache", "storage\logs")
foreach ($dir in $storageDirectories) {
    if (-not (Test-Path $dir)) {
        Write-Host "Creating directory: $dir" -ForegroundColor Yellow
        New-Item -ItemType Directory -Path $dir -Force | Out-Null
    }
}

# Check for Git updates (unless --no-update is specified)
Check-GitUpdate

if ($down) {
    Write-Host "Stopping containers..." -ForegroundColor Yellow
    docker-compose down -v --remove-orphans
    exit $LASTEXITCODE
}

if ($logs) {
    Write-Host "Showing logs..." -ForegroundColor Yellow
    docker-compose logs -f
    exit $LASTEXITCODE
}

$services = @()
if ($alone) {
    Write-Host "Running in ALONE mode - using existing PostgreSQL and RabbitMQ instances" -ForegroundColor Cyan
    Write-Host "Only starting the main application..." -ForegroundColor Yellow
    $services = @("lengkeng-api")
} else {
    Write-Host "Running in FULL mode - all services" -ForegroundColor Green
}

# Always build images (removed --build parameter as requested)
if ($alone) {
    # In alone mode, use separate compose file that doesn't have dependencies
    $cmdArgs = @("-f", "docker-compose.alone.yml", "up", "-d", "--build")
} else {
    # In full mode, start all services
    $cmdArgs = @("up", "-d", "--build")
}

Write-Host "Executing: docker-compose $($cmdArgs -join ' ')" -ForegroundColor Gray
docker-compose @cmdArgs

if ($LASTEXITCODE -eq 0) {
    Write-Host "Services started successfully!" -ForegroundColor Green
    if ($alone) {
        Write-Host "Main Application: http://localhost:8080" -ForegroundColor Green
        Write-Host "PostgreSQL: Using existing instance (localhost:5432)" -ForegroundColor Cyan
        Write-Host "RabbitMQ: Using existing instance (localhost:5672)" -ForegroundColor Cyan
    } else {
        Write-Host "Main Application: http://localhost:8080" -ForegroundColor Green
        Write-Host "PostgreSQL: localhost:5432" -ForegroundColor Green
        Write-Host "RabbitMQ Management: http://localhost:15672" -ForegroundColor Green
        Write-Host "RabbitMQ AMQP: localhost:5672" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "Useful commands:" -ForegroundColor Yellow
    Write-Host "  View logs: .\run_docker.ps1 -logs" -ForegroundColor Gray
    Write-Host "  Stop services: .\run_docker.ps1 -down" -ForegroundColor Gray
} else {
    Write-Error "Failed to start services"
    exit 1
}
