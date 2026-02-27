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

| Concept | Where |
|---|---|
| Multi-stage builds | Dockerfile (Stage 1 + 2) |
| Layer caching | requirements.txt copied first |
| Non-root user | `USER appuser` in Dockerfile |
| Health checks | `/health` endpoint + HEALTHCHECK |
| Structured logging | `logging.basicConfig()` in main.py |
| Environment variables | `-e APP_ENV=production` |
| Gunicorn vs Flask dev server | CMD in Dockerfile |

---

## ✅ Phase 1 Complete!
Next → **Phase 2: Kubernetes Deployment**
You'll take this same Docker image and deploy it to a K8s cluster.
