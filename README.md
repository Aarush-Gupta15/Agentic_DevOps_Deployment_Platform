# 🐳 Phase 1 — Dockerize a Python App

Learn Docker by building a real Flask app with health checks and logging.

---

## 📂 Structure

```
phase1-docker/
├── app/
│   ├── main.py           # Flask app (health + logging)
│   └── requirements.txt
├── Dockerfile            # Multi-stage build (read comments!)
├── .dockerignore
└── README.md
```

---

## 🧪 Step 1 — Run WITHOUT Docker first

```bash
cd app
pip install -r requirements.txt
python main.py
```

Visit: http://localhost:5000
Visit: http://localhost:5000/health
Visit: http://localhost:5000/info

**What you see in terminal:** Logs printing every request ✅

---

## 🐳 Step 2 — Build Docker Image

```bash
# Run from the phase1-docker/ folder
docker build -t phase1-app:latest .
```

Watch what happens:

- Stage 1 (builder): installs pip packages
- Stage 2 (runtime): copies only what's needed
- Result: small, clean image

Check image size:

```bash
docker images phase1-app
```

---

## ▶️ Step 3 — Run the Container

```bash
docker run -d \
  --name phase1-container \
  -p 5000:5000 \
  -e APP_ENV=production \
  phase1-app:latest
```

Flags explained:

- `-d` → run in background (detached)
- `--name` → give container a name
- `-p 5000:5000` → map host port to container port
- `-e APP_ENV=production` → set environment variable

---

## 🔍 Step 4 — Explore & Learn

**See logs:**

```bash
docker logs phase1-container -f
```

**Check health status:**

```bash
docker ps
# Look at the STATUS column → should say "healthy" after 30s
```

**Go inside the container:**

```bash
docker exec -it phase1-container /bin/bash
# You're now INSIDE the container!
# Try: ls, pwd, env, hostname
```

**Test health endpoint:**

```bash
curl http://localhost:5000/health
curl http://localhost:5000/info
```

---

## 🧹 Step 5 — Cleanup

```bash
docker stop phase1-container
docker rm phase1-container
```

---

## 🧠 What You Learned

| Concept                      | Where                              |
| ---------------------------- | ---------------------------------- |
| Multi-stage builds           | Dockerfile (Stage 1 + 2)           |
| Layer caching                | requirements.txt copied first      |
| Non-root user                | `USER appuser` in Dockerfile       |
| Health checks                | `/health` endpoint + HEALTHCHECK   |
| Structured logging           | `logging.basicConfig()` in main.py |
| Environment variables        | `-e APP_ENV=production`            |
| Gunicorn vs Flask dev server | CMD in Dockerfile                  |

---

## ✅ Phase 1 Complete!

Next → **Phase 2: Kubernetes Deployment**
You'll take this same Docker image and deploy it to a K8s cluster.

# ☸️ Phase 2 — Kubernetes Deployment

Deploy your Phase 1 Docker image to Kubernetes using Minikube (local K8s cluster).

---

## 📂 Structure

```
phase2-kubernetes/
└── k8s/
    ├── deployment.yaml    # Runs your container (replicas, probes, limits)
    ├── service.yaml       # Exposes your app to traffic
    └── configmap.yaml     # Stores environment config
```

---

## 🛠 Prerequisites — Install Minikube (Local K8s)

Minikube runs a real Kubernetes cluster on your Mac locally.

```bash
# Install Minikube
brew install minikube

# Install kubectl (K8s CLI)
brew install kubectl

# Start your local cluster
minikube start

# Verify cluster is running
kubectl cluster-info
kubectl get nodes
```

---

## 🐳 Step 1 — Push Phase 1 Image to Docker Hub

Kubernetes pulls images from a registry — it can't use local images directly.

```bash
# Login to Docker Hub
docker login

# Tag your Phase 1 image
docker tag phase1-app:latest YOUR_USERNAME/phase1-app:latest

# Push to Docker Hub
docker push YOUR_USERNAME/phase1-app:latest
```

Then update `deployment.yaml` line:

```yaml
image: YOUR_USERNAME/phase1-app:latest # ← replace YOUR_USERNAME
```

---

## 🚀 Step 2 — Deploy to Kubernetes

```bash
cd k8s/

# Apply all manifests
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Check everything is running
kubectl get pods
kubectl get deployments
kubectl get services
```

---

## 🔍 Step 3 — Explore & Learn

**Watch pods start up in real time:**

```bash
kubectl get pods -w
# -w = watch (live updates)
```

**See pod details (great for debugging):**

```bash
kubectl describe pod <pod-name>
# Shows: events, probe status, resource usage, errors
```

**See logs from your Flask app:**

```bash
kubectl logs <pod-name>
kubectl logs <pod-name> -f    # -f = follow (live logs)
```

**Go inside a pod:**

```bash
kubectl exec -it <pod-name> -- /bin/bash
```

---

## 🌐 Step 4 — Access Your App

With Minikube + NodePort, use:

```bash
minikube service flask-app-service
# Opens your app in browser automatically!
```

Or get the URL manually:

```bash
minikube service flask-app-service --url
# Returns: http://192.168.x.x:XXXXX
```

Test endpoints:

```bash
curl $(minikube service flask-app-service --url)/health
curl $(minikube service flask-app-service --url)/info
```

---

## 🧪 Step 5 — Test Kubernetes Features

**Scale up replicas manually:**

```bash
kubectl scale deployment flask-app --replicas=4
kubectl get pods   # See 4 pods now!
```

**Scale down:**

```bash
kubectl scale deployment flask-app --replicas=1
```

**Simulate a pod crash (K8s auto-restarts it!):**

```bash
kubectl delete pod <pod-name>
kubectl get pods -w   # Watch K8s create a new one instantly
```

**Rolling update (deploy new image version):**

```bash
kubectl set image deployment/flask-app flask-app=YOUR_USERNAME/phase1-app:v2
kubectl rollout status deployment/flask-app
```

**Rollback if something breaks:**

```bash
kubectl rollout undo deployment/flask-app
```

---

## 🧹 Cleanup

```bash
kubectl delete -f k8s/
minikube stop
```

---

## 🧠 What You Learned

| Concept         | Where                                                  |
| --------------- | ------------------------------------------------------ |
| Deployment      | `deployment.yaml` — runs & manages pods                |
| Replicas        | `replicas: 2` — 2 copies for availability              |
| Liveness Probe  | `/health` — K8s restarts unhealthy pods                |
| Readiness Probe | `/ready` — K8s removes unready pods from traffic       |
| Resource Limits | `cpu/memory` — prevents one pod from hogging resources |
| Service         | `service.yaml` — exposes pods to traffic               |
| ConfigMap       | `configmap.yaml` — config separate from image          |
| NodePort        | Access app from outside the cluster                    |
| Rolling Update  | Zero-downtime deploys                                  |
| Self-healing    | K8s auto-restarts crashed pods                         |

---

# ✅ Phase 2 Complete!

Next → **Phase 3: CI/CD with GitHub Actions**
Every push to `main` will automatically build, push, and deploy your app!

---

## ⚙️ Phase 3 — CI/CD with GitHub Actions

Every `git push` to `main` automatically builds, pushes, and deploys your app.

## 📂 Structure

```

your-repo/
└── .github/
└── workflows/
└── ci-cd.yaml # ← GitHub reads this automatically

```

## 🔑 Step 1 — Add GitHub Secrets

Your pipeline needs 3 secrets. Never hardcode these in code!

Go to: **GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

Add these 3 secrets:

### Secret 1: DOCKER_USERNAME

```

Name: DOCKER_USERNAME
Value: aarushgupta15

```

### Secret 2: DOCKER_PASSWORD

```

Name: DOCKER_PASSWORD
Value: your-dockerhub-password-or-token

```

💡 Better: use a Docker Hub Access Token (more secure than password)
→ Docker Hub → Account Settings → Security → New Access Token

### Secret 3: KUBECONFIG

This is your cluster credentials encoded in base64.

```bash
# Run this on your Mac to get the value:
cat ~/.kube/config | base64
# Copy the entire output → paste as the secret value
```

```
Name:  KUBECONFIG
Value: (paste base64 output here)
```

---

## 🚀 Step 2 — Push to GitHub

```bash
# Initialize git (if not already)
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Add all files
git add .
git commit -m "Phase 3: Add CI/CD pipeline"
git push origin main
```

---

## 👀 Step 3 — Watch Pipeline Run

1. Go to your GitHub repo
2. Click **Actions** tab
3. You'll see your pipeline running live!

```
✅ Build & Push Image    → ~2 minutes
✅ Deploy to Kubernetes  → ~1 minute
```

---

## 🔄 How Rolling Update Works

Every push → new image tag = commit SHA (e.g. `abc123def`)

```
kubectl set image deployment/flask-app flask-app=aarushgupta15/phase1-app:abc123def
```

Kubernetes replaces pods one by one:

```
Pod 1 (old) → terminated
Pod 1 (new) → running ✅
Pod 2 (old) → terminated
Pod 2 (new) → running ✅
Zero downtime! 🎉
```

---

## ↩️ Rollback if Something Breaks

```bash
# Undo last deployment instantly
kubectl rollout undo deployment/flask-app

# Or rollback to specific version
kubectl rollout history deployment/flask-app
kubectl rollout undo deployment/flask-app --to-revision=2
```

---

## 🧠 What You Learned

| Concept        | Where                                  |
| -------------- | -------------------------------------- |
| CI/CD trigger  | `on: push: branches: main`             |
| Job dependency | `needs: build-and-push`                |
| GitHub Secrets | `${{ secrets.DOCKER_USERNAME }}`       |
| Image tagging  | `:latest` + `:${{ github.sha }}`       |
| Rolling update | `kubectl set image` + `rollout status` |
| Rollback       | `kubectl rollout undo`                 |

---

## ✅ Phase 3 Complete!

Next → **Phase 4: Terraform — provision real cloud infrastructure**

```
# ⚙️ Phase 3 — CI/CD with GitHub Actions

Every `git push` to `main` automatically builds, pushes, and deploys your app.

---

## 📂 Structure
```

your-repo/
└── .github/
└── workflows/
└── ci-cd.yaml # ← GitHub reads this automatically

```

---

## 🔑 Step 1 — Add GitHub Secrets

Your pipeline needs 3 secrets. Never hardcode these in code!

Go to: **GitHub Repo → Settings → Secrets and variables → Actions → New repository secret**

Add these 3 secrets:

### Secret 1: DOCKER_USERNAME
```

Name: DOCKER_USERNAME
Value: aarushgupta15

```

### Secret 2: DOCKER_PASSWORD
```

Name: DOCKER_PASSWORD
Value: your-dockerhub-password-or-token

````
💡 Better: use a Docker Hub Access Token (more secure than password)
→ Docker Hub → Account Settings → Security → New Access Token

### Secret 3: KUBECONFIG
This is your cluster credentials encoded in base64.
```bash
# Run this on your Mac to get the value:
cat ~/.kube/config | base64
# Copy the entire output → paste as the secret value
````

```
Name:  KUBECONFIG
Value: (paste base64 output here)
```

---

## 🚀 Step 2 — Push to GitHub

```bash
# Initialize git (if not already)
git init
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# Add all files
git add .
git commit -m "Phase 3: Add CI/CD pipeline"
git push origin main
```

---

## 👀 Step 3 — Watch Pipeline Run

1. Go to your GitHub repo
2. Click **Actions** tab
3. You'll see your pipeline running live!

```
✅ Build & Push Image    → ~2 minutes
✅ Deploy to Kubernetes  → ~1 minute
```

---

## 🔄 How Rolling Update Works

Every push → new image tag = commit SHA (e.g. `abc123def`)

```
kubectl set image deployment/flask-app flask-app=aarushgupta15/phase1-app:abc123def
```

Kubernetes replaces pods one by one:

```
Pod 1 (old) → terminated
Pod 1 (new) → running ✅
Pod 2 (old) → terminated
Pod 2 (new) → running ✅
Zero downtime! 🎉
```

---

## ↩️ Rollback if Something Breaks

```bash
# Undo last deployment instantly
kubectl rollout undo deployment/flask-app

# Or rollback to specific version
kubectl rollout history deployment/flask-app
kubectl rollout undo deployment/flask-app --to-revision=2
```

---

## 🧠 What You Learned

| Concept        | Where                                  |
| -------------- | -------------------------------------- |
| CI/CD trigger  | `on: push: branches: main`             |
| Job dependency | `needs: build-and-push`                |
| GitHub Secrets | `${{ secrets.DOCKER_USERNAME }}`       |
| Image tagging  | `:latest` + `:${{ github.sha }}`       |
| Rolling update | `kubectl set image` + `rollout status` |
| Rollback       | `kubectl rollout undo`                 |

---

## ✅ Phase 3 Complete!

Next → **Phase 4: Terraform — provision real cloud infrastructure**

```

```
