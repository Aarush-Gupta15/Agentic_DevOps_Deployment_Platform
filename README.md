# 🚀 Agentic DevOps Deployment Platform

> An AI-powered DevOps system that provisions infrastructure and deploys applications automatically using natural language commands.

---

## 💼 Interview Pitch

> "I built an Agentic DevOps system where an AI agent provisions infrastructure and deploys applications dynamically using Terraform, Docker, Kubernetes, and a GitHub Actions CI/CD pipeline."

---

## 🏗 Project Structure

```
agentic-devops/
├── app/                            # Flask application
│   ├── main.py                     # 4 endpoints: / /health /ready /info
│   └── requirements.txt
│
├── terraform/                      # Infrastructure as Code (AWS EKS)
│   ├── main.tf                     # Root — calls VPC + EKS modules
│   ├── variables.tf                # All configurable variables
│   ├── outputs.tf                  # Printed after apply
│   ├── modules/
│   │   ├── vpc/                    # VPC, Subnets, IGW, Route Table
│   │   └── eks/                    # IAM, EKS Cluster, Node Group
│   └── environments/
│       ├── dev/terraform.tfvars    # t3.micro, 1 node (free tier)
│       └── staging/terraform.tfvars
│
├── k8s/                            # Kubernetes manifests
│   ├── deployment.yaml             # 2 replicas, probes, resource limits
│   ├── service.yaml                # NodePort service
│   └── configmap.yaml              # Environment config
│
├── agent/                          # AI Agent (Phase 5)
│   └── devops_agent.py             # LangChain agent (coming soon)
│
├── .github/
│   └── workflows/
│       └── ci-cd.yaml              # GitHub Actions pipeline
│
├── Dockerfile                      # Multi-stage build
├── docker-compose.yml              # Local testing
└── README.md
```

---

## 📦 Phases

### ✅ Phase 1 — Dockerize a Python App
- Flask app with `/health`, `/ready`, `/info` endpoints
- Multi-stage Dockerfile (smaller image)
- Structured logging on every request
- Docker Compose for local testing

**Run locally:**
```bash
docker compose up --build
# Visit: http://localhost:5001/health
```

---

### ✅ Phase 2 — Kubernetes Deployment
- 2 replicas for high availability
- Liveness probe → K8s restarts unhealthy pods
- Readiness probe → K8s removes unready pods from traffic
- Resource limits (CPU + memory)
- Deployed on kind cluster

**Deploy:**
```bash
kubectl apply -f configmap.yaml
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml
kubectl get pods
```

---

### ✅ Phase 3 — CI/CD with GitHub Actions
- Every `git push` → auto build + push Docker image
- Image tagged with `:latest` + `:commit-sha` (for rollbacks)
- Prints deploy command automatically

**Pipeline flow:**
```
git push → Build Image → Push to Docker Hub → Print kubectl command ✅
```

**Manual deploy after pipeline:**
```bash
kubectl set image deployment/flask-app flask-app=aarushgupta15/phase1-app:latest
kubectl rollout status deployment/flask-app
```

---

### ✅ Phase 4 — Infrastructure as Code (Terraform)
- Provisions AWS EKS cluster using Terraform modules
- VPC, Subnets, Security Groups, IAM Roles, Node Group
- Remote state stored in S3
- Dev + Staging environments separated

**Deploy infrastructure:**
```bash
cd terraform/
terraform init
terraform plan -var-file=environments/dev/terraform.tfvars
terraform apply -var-file=environments/dev/terraform.tfvars

# Connect kubectl to EKS
aws eks update-kubeconfig --region us-east-1 --name agentic-devops-dev
```

⚠️ Always destroy when done to avoid AWS charges:
```bash
terraform destroy -var-file=environments/dev/terraform.tfvars
```

---

### ⏳ Phase 5 — AI Agent (Coming Soon)
- Natural language commands → DevOps actions
- Level 1: Deploy, scale, status via chat
- Level 2: Auto-scale based on CPU usage
- Level 3: AI troubleshooter — reads logs, explains errors

**Example:**
```
You: "Deploy app with 3 replicas in staging"
You: "Scale production to 5 pods"
You: "Why is my pod crashing?"
```

---

## 🧠 What This Project Demonstrates

| Skill | Tool |
|---|---|
| Containerization | Docker, multi-stage builds |
| Container Orchestration | Kubernetes, probes, resource limits |
| CI/CD | GitHub Actions |
| Infrastructure as Code | Terraform, AWS EKS |
| Cloud Infrastructure | AWS VPC, EKS, IAM, S3 |
| AI Agents | LangChain, tool calling |
| Python Backend | Flask, Gunicorn |

---

## 🛠 Tech Stack

`Python` `Flask` `Docker` `Kubernetes` `Terraform` `AWS EKS` `GitHub Actions` `LangChain` `kind` `kubectl`

---

## 👤 Author

**Aarush Gupta**
GitHub: [@Aarush-Gupta15](https://github.com/Aarush-Gupta15)
