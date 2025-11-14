# Build and run Lengkeng UI with Docker

# Check for new code updates
Write-Host "Checking for code updates..." -ForegroundColor Yellow

# Check Git status
Write-Host "Current Git status:" -ForegroundColor Gray
git status --porcelain

# Fetch latest changes from remote
Write-Host "Fetching latest changes from remote..." -ForegroundColor Gray
git fetch origin

# Check if there are updates available
$localCommit = git rev-parse HEAD
$remoteCommit = git rev-parse origin/main

if ($localCommit -ne $remoteCommit) {
    Write-Host "New code updates found! Pulling changes..." -ForegroundColor Green
    git pull origin main

    if ($LASTEXITCODE -eq 0) {
        Write-Host "Code updated successfully!" -ForegroundColor Green
    } else {
        Write-Host "Error pulling updates. Please check for conflicts." -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "No new updates found. Using current code." -ForegroundColor Cyan
}

# Build and start the application (--build will rebuild and recreate containers)
Write-Host "Building and starting the application on port 8800..." -ForegroundColor Green
docker-compose up --build -d

Write-Host "Application is running at http://localhost:8800" -ForegroundColor Cyan
Write-Host "To stop the application, run: docker-compose down" -ForegroundColor Yellow
