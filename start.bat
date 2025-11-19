@echo off
echo ========================================
echo   Quick Start - K8s Deployer
echo ========================================
echo.

REM Check if virtual environment exists
if not exist venv (
    echo ❌ Virtual environment not found!
    echo.
    echo Run setup first:
    echo    setup.bat
    echo.
    pause
    exit /b 1
)

REM Check if .env exists
if not exist .env (
    echo ❌ .env file not found!
    echo.
    echo Creating .env from template...
    copy .env.example .env
    echo.
    echo ⚠️  IMPORTANT: Edit .env file with your credentials!
    echo.
    echo You need to add:
    echo   - GitHub OAuth credentials
    echo   - Docker Hub credentials
    echo.
    pause
    notepad .env
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate

REM Check if dependencies are installed
pip show Flask >nul 2>&1
if %errorlevel% neq 0 (
    echo 📥 Installing dependencies...
    pip install -r requirements.txt
)

REM Check Docker
echo.
echo 🐳 Checking Docker...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not running!
    echo.
    echo Please start Docker Desktop and try again.
    pause
    exit /b 1
)
echo ✅ Docker is running

REM Check Kubernetes
echo.
echo ☸️  Checking Kubernetes...
kubectl cluster-info >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Kubernetes is not running!
    echo.
    echo Please enable Kubernetes in Docker Desktop:
    echo   1. Open Docker Desktop
    echo   2. Go to Settings → Kubernetes
    echo   3. Check "Enable Kubernetes"
    echo   4. Click Apply and Restart
    pause
    exit /b 1
)
echo ✅ Kubernetes is running

REM Check RBAC
kubectl get namespace deployment-system >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo 🔐 Setting up Kubernetes RBAC...
    kubectl apply -f k8s\rbac.yaml
)

echo.
echo ========================================
echo   Starting Flask Application
echo ========================================
echo.
echo The app will be available at:
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.
echo ========================================
echo.

REM Start the Flask app
python app.py
