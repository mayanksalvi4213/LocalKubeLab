@echo off
REM Setup script for GitHub to Kubernetes Deployer (Windows)

echo 🚀 Setting up GitHub to Kubernetes Deployer...

REM Check Python installation
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.9 or higher.
    exit /b 1
)

echo ✅ Python found
python --version

REM Check Docker installation
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop.
    exit /b 1
)

echo ✅ Docker found
docker --version

REM Check Kubernetes (kubectl)
kubectl version --client >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  kubectl is not installed. Please install kubectl to deploy to Kubernetes.
) else (
    echo ✅ kubectl found
    kubectl version --client
)

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your credentials!
) else (
    echo ✅ .env file already exists
)

REM Create deployments directory
if not exist deployments mkdir deployments

echo.
echo ✨ Setup complete! Next steps:
echo.
echo 1. Edit .env file with your credentials:
echo    - GitHub OAuth credentials
echo    - Docker Hub credentials
echo.
echo 2. Activate virtual environment:
echo    venv\Scripts\activate
echo.
echo 3. Start the application:
echo    python app.py
echo.
echo 4. Open browser at:
echo    http://localhost:5000
echo.
echo 5. (Optional) Start monitoring stack:
echo    cd monitoring
echo    docker-compose up -d
echo.
echo Happy deploying! 🎉

pause
