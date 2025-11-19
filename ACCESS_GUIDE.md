# 🎯 Quick Access Guide - Your Deployed Project

## 🌐 Access Your Deployed Application

### Your App is Running at:

**http://localhost:8080**

(This is your GitHub repository that you deployed - it's now running in Kubernetes!)

### Check if it's working:

```powershell
# Test the connection
curl http://localhost:8080

# Or open in browser
start http://localhost:8080
```

---

## 📊 Monitoring URLs

### Prometheus (Metrics Collection)

- **URL**: http://localhost:30090
- **Purpose**: Collects and stores metrics from Kubernetes
- **What to do**:
  - Try queries like `up` to see all services
  - View graphs of CPU, memory, network usage

### Grafana (Visualization)

- **URL**: http://localhost:30030
- **Login**: admin / admin
- **Purpose**: Beautiful dashboards to visualize Prometheus data
- **What to do**:
  - Import dashboard ID **6417** for Kubernetes monitoring
  - Import dashboard ID **747** for pod monitoring
  - See detailed guide in `GRAFANA_GUIDE.md`

---

## 🎮 Management Dashboard

### Your Flask Control Panel

- **URL**: http://localhost:5000
- **What you can do**:
  - ✅ Login with GitHub
  - ✅ Browse repositories
  - ✅ Deploy new repositories
  - ✅ View active deployments
  - ✅ Delete deployments
  - ✅ Access monitoring links

---

## 🔍 Kubernetes Commands

### View Your Deployment

```powershell
# See your running pods
kubectl get pods

# See details
kubectl describe pod <pod-name>

# View logs from your app
kubectl logs -l app=rospl-project

# Follow logs in real-time
kubectl logs -l app=rospl-project -f
```

### View Service

```powershell
# See your service
kubectl get service rospl-project

# Get detailed info
kubectl describe service rospl-project
```

### Scale Your Application

```powershell
# Scale to 3 replicas
kubectl scale deployment rospl-project --replicas=3

# Scale back to 2
kubectl scale deployment rospl-project --replicas=2
```

### Delete Your Deployment

```powershell
# Option 1: Use the Flask dashboard (Deployments → Delete button)

# Option 2: Use kubectl
kubectl delete deployment rospl-project
kubectl delete service rospl-project
```

---

## 🚀 Complete Application Stack

```
┌─────────────────────────────────────────┐
│  Flask Dashboard                        │
│  http://localhost:5000                  │
│  (Deploy & Manage Apps)                 │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  Deployed Application                   │
│  http://localhost:8080                  │
│  (Your GitHub repo running in K8s)      │
└─────────────────────────────────────────┘
                ↓
┌─────────────────────────────────────────┐
│  Monitoring Stack                       │
│  - Prometheus: localhost:30090          │
│  - Grafana: localhost:30030             │
│  (Monitor performance & health)         │
└─────────────────────────────────────────┘
```

---

## 📝 What Each Tool Does

### Flask App (localhost:5000)

- **Control panel** for deploying applications
- Select GitHub repos and deploy them
- Manage existing deployments

### Your Deployed App (localhost:8080)

- **Your actual application** running in Kubernetes
- This is the repo you selected and deployed
- Running with 2 replicas for high availability

### Prometheus (localhost:30090)

- **Metrics database** - stores all performance data
- Collects metrics every 15 seconds
- Provides raw data and simple graphs

### Grafana (localhost:30030)

- **Dashboard tool** - makes Prometheus data beautiful
- Pre-built dashboards for Kubernetes
- Alerts and notifications
- Historical analysis

---

## 🎓 Try This Now

1. **Access your deployed app**: http://localhost:8080
2. **Check Prometheus**: http://localhost:30090
   - Enter query: `up`
   - Click "Execute"
   - See all services
3. **Check Grafana**: http://localhost:30030
   - Login: admin/admin
   - Import dashboard 6417
   - View your cluster metrics!

---

## 🆘 Troubleshooting

### "Can't access localhost:8080"

```powershell
# Check if pods are running
kubectl get pods

# Check service
kubectl get service rospl-project

# View logs
kubectl logs -l app=rospl-project
```

### "No data in Grafana"

- Wait 2-3 minutes for metrics to collect
- Verify Prometheus is running: `kubectl get pods -n monitoring`
- Check data source in Grafana

### "Deployment not working"

- Check Flask app logs
- Verify Docker Hub credentials in `.env`
- Check Kubernetes is enabled in Docker Desktop

---

**Need more help?** Check `GRAFANA_GUIDE.md` for detailed Grafana setup!
