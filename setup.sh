#!/bin/bash

# Setup script for GitHub to Kubernetes Deployer

echo "🚀 Setting up GitHub to Kubernetes Deployer..."

# Check Python installation
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.9 or higher."
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Check Docker installation
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker Desktop."
    exit 1
fi

echo "✅ Docker found: $(docker --version)"

# Check Kubernetes (kubectl)
if ! command -v kubectl &> /dev/null; then
    echo "⚠️  kubectl is not installed. Please install kubectl to deploy to Kubernetes."
else
    echo "✅ kubectl found: $(kubectl version --client --short 2>/dev/null || kubectl version --client)"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your credentials!"
else
    echo "✅ .env file already exists"
fi

# Create deployments directory
mkdir -p deployments

echo ""
echo "✨ Setup complete! Next steps:"
echo ""
echo "1. Edit .env file with your credentials:"
echo "   - GitHub OAuth credentials"
echo "   - Docker Hub credentials"
echo ""
echo "2. Start the application:"
echo "   python app.py"
echo ""
echo "3. Open browser at:"
echo "   http://localhost:5000"
echo ""
echo "4. (Optional) Start monitoring stack:"
echo "   cd monitoring && docker-compose up -d"
echo ""
echo "Happy deploying! 🎉"
