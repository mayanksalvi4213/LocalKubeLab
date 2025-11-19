@echo off
REM Docker Cleanup Script

echo ========================================
echo   Docker Cleanup Tool
echo ========================================
echo.

echo 🔍 Current Docker Images:
docker images
echo.

echo ⚠️  This will remove:
echo    - Stopped containers
echo    - Unused images
echo    - Unused networks
echo    - Build cache
echo.

set /p confirm="Do you want to continue? (y/n): "
if /i not "%confirm%"=="y" (
    echo Cancelled.
    pause
    exit /b
)

echo.
echo 🧹 Cleaning up...
echo.

REM Remove stopped containers
echo [1/4] Removing stopped containers...
docker container prune -f

REM Remove dangling images
echo [2/4] Removing unused images...
docker image prune -a -f

REM Remove unused networks
echo [3/4] Removing unused networks...
docker network prune -f

REM Remove build cache
echo [4/4] Removing build cache...
docker builder prune -f

echo.
echo ========================================
echo ✅ Cleanup Complete!
echo ========================================
echo.

echo Remaining images:
docker images

echo.
echo Disk space reclaimed:
docker system df

echo.
pause
