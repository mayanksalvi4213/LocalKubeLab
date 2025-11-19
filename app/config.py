import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Flask config
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # GitHub OAuth
    GITHUB_CLIENT_ID = os.getenv('GITHUB_CLIENT_ID')
    GITHUB_CLIENT_SECRET = os.getenv('GITHUB_CLIENT_SECRET')
    GITHUB_REDIRECT_URI = os.getenv('GITHUB_REDIRECT_URI', 'http://localhost:5000/callback')
    
    # Docker Hub
    DOCKERHUB_USERNAME = os.getenv('DOCKERHUB_USERNAME')
    DOCKERHUB_PASSWORD = os.getenv('DOCKERHUB_PASSWORD')
    
    # Kubernetes
    K8S_NAMESPACE = os.getenv('K8S_NAMESPACE', 'default')
    KUBECONFIG_PATH = os.getenv('KUBECONFIG_PATH', '~/.kube/config')
    
    # App settings
    DEPLOYMENT_DIR = os.getenv('DEPLOYMENT_DIR', './deployments')
