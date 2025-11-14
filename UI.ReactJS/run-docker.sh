#!/bin/bash
# Build and run Lengkeng UI with Docker

# Check for new code updates
echo -e "\033[33mChecking for code updates...\033[0m"

# Check Git status
echo -e "\033[37mCurrent Git status:\033[0m"
git status --porcelain

# Fetch latest changes from remote
echo -e "\033[37mFetching latest changes from remote...\033[0m"
git fetch origin

# Check if there are updates available
LOCAL_COMMIT=$(git rev-parse HEAD)
REMOTE_COMMIT=$(git rev-parse origin/main)

if [ "$LOCAL_COMMIT" != "$REMOTE_COMMIT" ]; then
    echo -e "\033[32mNew code updates found! Pulling changes...\033[0m"
    git pull origin main

    if [ $? -eq 0 ]; then
        echo -e "\033[32mCode updated successfully!\033[0m"
    else
        echo -e "\033[31mError pulling updates. Please check for conflicts.\033[0m"
        exit 1
    fi
else
    echo -e "\033[36mNo new updates found. Using current code.\033[0m"
fi

# Build and start the application (--build will rebuild and recreate containers)
echo -e "\033[32mBuilding and starting the application on port 8800...\033[0m"
docker compose up --build -d

echo -e "\033[36mApplication is running at http://localhost:8800\033[0m"
echo -e "\033[33mTo stop the application, run: docker-compose down\033[0m"
