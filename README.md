# 🚀 GitHub to Kubernetes Deployer

A complete web application that automates the deployment of GitHub repositories to Kubernetes clusters with Docker containerization and monitoring.

## 📋 Features

- **GitHub OAuth Integration** - Secure login with GitHub account
- **Repository Selection** - Browse and select your GitHub repositories
- **Automatic Docker Build** - Build Docker images from repository code
- **Docker Hub Push** - Automatically push images to Docker Hub
- **Kubernetes Deployment** - Deploy applications to Kubernetes cluster
- **Real-time Monitoring** - Monitor deployments with Prometheus & Grafana
- **Modern UI** - Responsive web interface built with HTML/CSS/JS

## 🏗️ Architecture

```
User → Web UI (Select GitHub Repo)
        ↓
Docker Build & Push (to DockerHub)
        ↓
Kubernetes Cluster Deployment
        ↓
Monitoring (Prometheus + Grafana)
```

## 📁 Project Structure

```
rospl/
├── app/
│   ├── __init__.py
│   ├── config.py              # Configuration management
│   ├── github_auth.py         # GitHub OAuth handling
│   ├── docker_builder.py      # Docker image building
│   └── k8s_deployer.py        # Kubernetes deployment
├── templates/
│   ├── index.html             # Landing page
│   └── dashboard.html         # Main dashboard
├── static/
│   ├── style.css              # Stylesheets
│   └── app.js                 # Frontend JavaScript
├── k8s/
│   ├── deployment.yaml        # Sample K8s deployment
│   ├── rbac.yaml              # RBAC configuration
│   └── ingress.yaml           # Ingress configuration
├── monitoring/
│   ├── prometheus.yml         # Prometheus config
│   ├── prometheus-deployment.yaml
│   ├── grafana-deployment.yaml
│   └── docker-compose.yml     # Local monitoring setup
├── app.py                     # Main Flask application
├── requirements.txt           # Python dependencies
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Docker Desktop
- Kubernetes cluster (minikube, Docker Desktop K8s, or cloud provider)
- GitHub account
- Docker Hub account

### 1. Clone the Repository

```bash
cd rospl
```

### 2. Install Dependencies

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
# source venv/bin/activate

pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your credentials:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Mac/Linux
```

Edit `.env` file:

```env
SECRET_KEY=your-secret-key

# GitHub OAuth (create at https://github.com/settings/developers)
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
GITHUB_REDIRECT_URI=http://localhost:5000/callback

# Docker Hub
DOCKERHUB_USERNAME=your-dockerhub-username
DOCKERHUB_PASSWORD=your-dockerhub-password

# Kubernetes
K8S_NAMESPACE=default
```

### 4. Setup GitHub OAuth App

1. Go to https://github.com/settings/developers
2. Click "New OAuth App"
3. Fill in:
   - **Application name**: K8s Deployer
   - **Homepage URL**: http://localhost:5000
   - **Authorization callback URL**: http://localhost:5000/callback
4. Copy the Client ID and Client Secret to your `.env` file

### 5. Setup Kubernetes

Make sure your Kubernetes cluster is running:

```bash
# For Docker Desktop: Enable Kubernetes in settings
# For minikube:
minikube start

# Verify cluster is running:
kubectl cluster-info
kubectl get nodes
```

Apply RBAC configuration:

```bash
kubectl apply -f k8s/rbac.yaml
```

### 6. Setup Monitoring (Optional)

Deploy Prometheus and Grafana to your cluster:

```bash
kubectl apply -f monitoring/prometheus-deployment.yaml
kubectl apply -f monitoring/grafana-deployment.yaml
```

Or run locally with Docker Compose:

```bash
cd monitoring
docker-compose up -d
```

Access:

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3000 (admin/admin)

### 7. Run the Application

```bash
python app.py
```

The application will be available at http://localhost:5000

## 📖 Usage Guide

### 1. Login

1. Open http://localhost:5000
2. Click "Login with GitHub"
3. Authorize the application

### 2. Deploy a Repository

1. On the dashboard, browse your repositories
2. Use the search box to filter repositories
3. Click "🚀 Deploy" on any repository
4. Watch the deployment progress:
   - Building Docker image
   - Pushing to Docker Hub
   - Deploying to Kubernetes

### 3. Manage Deployments

1. Click "Deployments" in the sidebar
2. View all active deployments
3. Check deployment status and health
4. Delete deployments when needed

### 4. Monitoring

1. Click "Monitoring" in the sidebar
2. Open Prometheus for metrics
3. Open Grafana for visualizations

## 🔧 Configuration

### Kubernetes Namespace

By default, deployments are created in the `default` namespace. Change this in `.env`:

```env
K8S_NAMESPACE=your-namespace
```

### Deployment Settings

Modify deployment settings in `app/k8s_deployer.py`:

```python
replicas = 2  # Number of pod replicas
port = 8080   # Container port
```

### Docker Build

The application automatically creates a Dockerfile if one doesn't exist. Customize the default Dockerfile in `app/docker_builder.py`.

## 🐳 Docker Commands

Useful Docker commands for troubleshooting:

```bash
# List images
docker images

# View logs
docker logs <container-id>

# Remove images
docker rmi <image-name>

# Login to Docker Hub
docker login
```

## ☸️ Kubernetes Commands

Useful kubectl commands:

```bash
# List deployments
kubectl get deployments

# List pods
kubectl get pods

# View pod logs
kubectl logs <pod-name>

# Delete deployment
kubectl delete deployment <deployment-name>

# View services
kubectl get services

# Describe deployment
kubectl describe deployment <deployment-name>
```

## 📊 Monitoring

### Prometheus

Access Prometheus at http://localhost:9090 or your cluster's Prometheus service.

Useful queries:

- `up` - Check which targets are up
- `container_cpu_usage_seconds_total` - CPU usage
- `container_memory_usage_bytes` - Memory usage

### Grafana

Access Grafana at http://localhost:3000 (default: admin/admin)

1. Add Prometheus as a data source (http://prometheus:9090)
2. Import Kubernetes dashboards
3. Create custom dashboards for your apps

## 🔒 Security Considerations

- **Never commit `.env` file** - It contains sensitive credentials
- **Use secrets in production** - Store credentials in Kubernetes secrets
- **Enable HTTPS** - Use proper SSL certificates in production
- **Restrict RBAC** - Limit Kubernetes permissions as needed
- **Secure Docker Hub** - Use access tokens instead of passwords
- **GitHub OAuth** - Review and limit scope permissions

## 🚨 Troubleshooting

### GitHub OAuth Errors

- Verify Client ID and Secret are correct
- Check callback URL matches OAuth app settings
- Ensure app is not in private mode

### Docker Build Failures

- Check Docker daemon is running: `docker ps`
- Verify Docker Hub credentials
- Check repository has buildable code
- Review error logs in deployment modal

### Kubernetes Deployment Issues

- Verify cluster is running: `kubectl cluster-info`
- Check RBAC permissions: `kubectl auth can-i create deployments`
- View pod status: `kubectl get pods`
- Check pod logs: `kubectl logs <pod-name>`

### Port Already in Use

```bash
# On Windows (find process using port 5000):
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# On Mac/Linux:
lsof -ti:5000 | xargs kill -9
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📝 License

MIT License - feel free to use this project for learning or production.

## 👨‍💻 Author

Created with ❤️ for automated Kubernetes deployments

## 🔗 Useful Links

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Docker Documentation](https://docs.docker.com/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [GitHub OAuth Apps](https://docs.github.com/en/developers/apps/building-oauth-apps)

## 📞 Support

For issues and questions:

- Check the troubleshooting section
- Review application logs
- Check Kubernetes pod logs
- Verify all prerequisites are installed

---

**Happy Deploying! 🚀**
