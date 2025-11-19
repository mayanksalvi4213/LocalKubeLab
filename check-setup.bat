@echo off
echo ========================================
echo   Kubernetes Deployer Setup Checker
echo ========================================
echo.

set ERROR_COUNT=0

REM Check Python
echo [1/7] Checking Python...
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Python is installed
    python --version
) else (
    echo    ❌ Python is NOT installed
    set /a ERROR_COUNT+=1
)
echo.

REM Check Docker
echo [2/7] Checking Docker...
docker --version >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Docker is installed
    docker --version
    
    REM Check if Docker is running
    docker ps >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ Docker daemon is running
    ) else (
        echo    ❌ Docker daemon is NOT running - Start Docker Desktop!
        set /a ERROR_COUNT+=1
    )
) else (
    echo    ❌ Docker is NOT installed
    set /a ERROR_COUNT+=1
)
echo.

REM Check kubectl
echo [3/7] Checking kubectl...
kubectl version --client >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ kubectl is installed
    kubectl version --client --short 2>nul
    
    REM Check if cluster is accessible
    kubectl cluster-info >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ Kubernetes cluster is accessible
        kubectl get nodes
    ) else (
        echo    ❌ Cannot connect to Kubernetes cluster
        echo    → Enable Kubernetes in Docker Desktop Settings
        set /a ERROR_COUNT+=1
    )
) else (
    echo    ❌ kubectl is NOT installed
    echo    → Install kubectl or enable Kubernetes in Docker Desktop
    set /a ERROR_COUNT+=1
)
echo.

REM Check .env file
echo [4/7] Checking .env file...
if exist .env (
    echo    ✅ .env file exists
    
    REM Check for placeholder values
    findstr /C:"your-github-client-id" .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ⚠️  WARNING: GitHub credentials not configured
        echo    → Edit .env file with your GitHub OAuth credentials
    ) else (
        echo    ✅ GitHub credentials configured
    )
    
    findstr /C:"your-dockerhub-username" .env >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ⚠️  WARNING: Docker Hub credentials not configured
        echo    → Edit .env file with your Docker Hub credentials
    ) else (
        echo    ✅ Docker Hub credentials configured
    )
) else (
    echo    ❌ .env file NOT found
    echo    → Run: copy .env.example .env
    echo    → Then edit .env with your credentials
    set /a ERROR_COUNT+=1
)
echo.

REM Check virtual environment
echo [5/7] Checking Python virtual environment...
if exist venv (
    echo    ✅ Virtual environment exists
) else (
    echo    ⚠️  Virtual environment NOT created
    echo    → Run: python -m venv venv
)
echo.

REM Check Python dependencies (if venv is activated)
echo [6/7] Checking Python dependencies...
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
    pip show Flask >nul 2>&1
    if %errorlevel% equ 0 (
        echo    ✅ Flask is installed
        pip show kubernetes >nul 2>&1
        if %errorlevel% equ 0 (
            echo    ✅ Kubernetes library is installed
        ) else (
            echo    ❌ Kubernetes library NOT installed
            echo    → Run: pip install -r requirements.txt
            set /a ERROR_COUNT+=1
        )
    ) else (
        echo    ❌ Dependencies NOT installed
        echo    → Activate venv: venv\Scripts\activate
        echo    → Then run: pip install -r requirements.txt
        set /a ERROR_COUNT+=1
    )
) else (
    echo    ⚠️  Cannot check - create venv first
)
echo.

REM Check Kubernetes RBAC
echo [7/7] Checking Kubernetes RBAC...
kubectl get namespace deployment-system >nul 2>&1
if %errorlevel% equ 0 (
    echo    ✅ Kubernetes RBAC is configured
) else (
    echo    ⚠️  Kubernetes RBAC NOT configured
    echo    → Run: kubectl apply -f k8s\rbac.yaml
)
echo.

echo ========================================
echo   Summary
echo ========================================
if %ERROR_COUNT% equ 0 (
    echo ✅ All checks passed! You're ready to go!
    echo.
    echo Next steps:
    echo 1. Make sure .env has your credentials
    echo 2. Run: venv\Scripts\activate
    echo 3. Run: python app.py
    echo 4. Open: http://localhost:5000
) else (
    echo ❌ Found %ERROR_COUNT% critical issue(s)
    echo.
    echo Please fix the issues above before running the app.
    echo See SETUP_GUIDE.md for detailed instructions.
)
echo ========================================
echo.

pause
