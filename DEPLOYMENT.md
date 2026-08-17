# 🚀 TRACEBACK AI — Deployment & Containerization Guide

Production-ready containerization and deployment guide for the **TRACEBACK AI** SRE incident investigation engine.

---

## 🏗️ Architecture Overview

```text
               Internet / Client Browser
                           │
                           ▼ (Port 3000)
            ┌─────────────────────────────┐
            │   traceback-frontend        │
            │   (Next.js 14 Production)   │
            └──────────────┬──────────────┘
                           │ HTTP / REST
                           ▼ (Port 8000)
            ┌─────────────────────────────┐
            │   traceback-backend         │
            │   (FastAPI + LangGraph)     │
            └──────────────┬──────────────┘
                           │ AsyncPG (Port 5432)
                           ▼
            ┌─────────────────────────────┐
            │   traceback-postgres        │
            │   (PostgreSQL 16 Engine)    │
            └─────────────────────────────┘
```

---

## 📦 Container Setup (Exactly 3 Containers)

1. **`traceback-frontend`**: Next.js 14 Web Application serving the interactive SRE workspace.
2. **`traceback-backend`**: FastAPI REST API hosting the LangGraph Agent, RAG ingestion, and OpenAI/LangSmith pipelines.
3. **`traceback-postgres`**: PostgreSQL 16 relational store backed by persistent Docker volume `postgres_data`.

---

## ⚡ Quick Start (Local Docker Compose)

### 1. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your confidential keys in `.env`:
```env
OPENAI_API_KEY=sk-proj-...
LANGSMITH_API_KEY=lsv2_...
```

### 2. Build & Launch Containers
```bash
docker compose build
docker compose up -d
```

### 3. Verify Container Health
```bash
docker compose ps
```

---

## 🔍 Useful Operational Commands

### View Service Logs
```bash
# View backend logs in real-time
docker compose logs -f backend

# View frontend logs
docker compose logs -f frontend

# View database logs
docker compose logs -f postgres
```

### Rebuild Containers Without Cache
```bash
docker compose build --no-cache
docker compose up -d
```

### Stop & Down All Containers
```bash
docker compose down
```

---

## 🔒 Security & Environment Auditing

- **No Secrets in Docker Images**: All API keys and database credentials are read dynamically from runtime environment variables.
- **Git Protection**: `.env` and `.venv` are ignored via `.gitignore` and `.dockerignore`.

---

## 🐳 Docker Hub Published Images

| Service | Image Name | Base Image |
| :--- | :--- | :--- |
| **Frontend** | `ayyan119/traceback-frontend:latest` | `node:22-alpine` |
| **Backend** | `ayyan119/traceback-backend:latest` | `python:3.10-slim` |
| **Database** | `postgres:16-alpine` | Official PostgreSQL Image |

---

## ☁️ Future AWS Deployment Path

For cloud deployment to AWS:
1. Push images to **AWS ECR** (Elastic Container Registry).
2. Provision an **AWS RDS PostgreSQL** instance.
3. Deploy frontend & backend containers to **AWS ECS (Fargate)** or **AWS App Runner** with environment variable secrets managed in **AWS Secrets Manager**.
