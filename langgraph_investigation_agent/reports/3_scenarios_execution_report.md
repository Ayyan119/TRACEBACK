# TRACEBACK AI Investigation Agent — 3 Scenario Empirical Execution Report

This report presents the complete input payloads, step-by-step state trajectories, evidence filtering results, Self-RAG decisions, and final hypothesis outputs for **3 distinct production outage scenarios**.

---

## 1. Scenario 1: PostgreSQL Connection Pool Exhaustion & Row Lock Contention

### A. Input Payload
```json
{
  "investigation_id": "inv-scenario-1-db-lock",
  "project_id": "art-gallary",
  "incident_id": "INC-2001",
  "incident_description": "Checkout service returning HTTP 504 Gateway Timeouts during flash sale launch. PostgreSQL active connections reached 100/100 limit due to unindexed row locks on the orders table.",
  "incident_log_reference": {
    "file_name": "checkout_app.log",
    "file_size_bytes": 1258291
  },
  "services": ["checkout-service", "postgresql_db"],
  "incident_documents": [
    {
      "name": "PostgreSQL_Pool_Diagnostics.pdf",
      "content": "Diagnostics report showing connection pool max_connections=100 limit reached. Long transactions on orders table holding exclusive row locks."
    },
    {
      "name": "Employee_Onboarding_Guide.pdf",
      "content": "Welcome to art-gallary engineering workspace onboarding notes."
    }
  ],
  "incident_images": [
    {
      "title": "Grafana_504_Latency_Spike.png",
      "file_url": "/tmp/grafana_504_error.png"
    },
    {
      "title": "Company_Logo.jpg",
      "file_url": "/tmp/logo.jpg"
    }
  ]
}
```

### B. Graph Trajectory & Evidence Filtering
1. **Parallel Vision & Doc Nodes**:
   - `Grafana_504_Latency_Spike.png`: **ACCEPTED** (Relevant, confidence 0.92)
   - `Company_Logo.jpg`: **REJECTED** (Irrelevant logo asset)
   - `PostgreSQL_Pool_Diagnostics.pdf`: **ACCEPTED** (Relevant, confidence 0.90)
   - `Employee_Onboarding_Guide.pdf`: **REJECTED** (Irrelevant onboarding document)
2. **Log Tool Reasoning**: Tool iteration 1 queried `checkout-service` logs, returning structured pool exhaustion records.
3. **Self-RAG Decision**: `retrieval_required = True`. Search query: `"PostgreSQL database connection pool troubleshooting runbook"`.
4. **Qdrant Retrieval & Reranking**: Retrieved top 3 runbook chunks + 1 atomic past incident (`INC-1001`), reranked and kept 4 high-relevance items.

### C. Output Hypothesis
- **Primary Root Cause**: **PostgreSQL Connection Pool Exhaustion due to Unindexed Query Lock Contention**
- **Confidence**: **94.5%**
- **Likely Mechanism**: Missing index on foreign key `customer_id` causing full table scans and row locks during peak checkout traffic.
- **Recommended Action**: Run `EXPLAIN ANALYZE` on checkout queries and scale PostgreSQL `max_connections` from 100 to 250.

---

## 2. Scenario 2: Redis Cluster Memory Eviction & Latency Spike

### A. Input Payload
```json
{
  "investigation_id": "inv-scenario-2-redis-eviction",
  "project_id": "art-gallary",
  "incident_id": "INC-2002",
  "incident_description": "User authentication and session verification service returning HTTP 500 Internal Server Errors. Redis cluster memory hit 100% maxmemory limit causing blocking key evictions and 2000ms latency spikes.",
  "incident_log_reference": {
    "file_name": "auth_session.log",
    "file_size_bytes": 870400
  },
  "services": ["auth-service", "redis_cache"],
  "incident_documents": [
    {
      "name": "Redis_Eviction_SOP.docx",
      "content": "Standard operating procedure for Redis memory eviction. When memory usage hits 100%, blocking sync evictions introduce P95 latency spikes."
    }
  ],
  "incident_images": [
    {
      "title": "Redis_Memory_Grafana.png",
      "file_url": "/tmp/redis_grafana_error.png"
    }
  ]
}
```

### B. Graph Trajectory & Evidence Filtering
1. **Parallel Vision & Doc Nodes**:
   - `Redis_Memory_Grafana.png`: **ACCEPTED** (Relevant telemetry screenshot)
   - `Redis_Eviction_SOP.docx`: **ACCEPTED** (Relevant runbook document)
2. **Log Tool Reasoning**: Queried `auth-service` logs, returning Redis read timeout error entries.
3. **Self-RAG Decision**: `retrieval_required = True`. Search query: `"Redis cache timeout latency SOP"`.
4. **Qdrant Retrieval & Reranking**: Retrieved top runbooks, kept 4 items.

### C. Output Hypothesis
- **Primary Root Cause**: **Redis Cluster Memory Exhaustion & LRU Key Eviction Latency Throttling**
- **Confidence**: **96.0%**
- **Likely Mechanism**: Active user session storage hit 100% of the 2GB `maxmemory` limit. Synchronous LRU key evictions introduced 2000ms latency spikes on `auth-service`.
- **Recommended Action**: Increase Redis `maxmemory` from 2GB to 4GB and configure `maxmemory-policy` to `volatile-lru`.

---

## 3. Scenario 3: Kubernetes Container OOMKilled & CrashLoopBackOff

### A. Input Payload
```json
{
  "investigation_id": "inv-scenario-3-k8s-oom",
  "project_id": "art-gallary",
  "incident_id": "INC-2003",
  "incident_description": "Payment gateway microservice pods continuously restarting in CrashLoopBackOff state. Worker memory limit of 512MB exceeded due to unclosed HTTP client connection leak in payment processor.",
  "incident_log_reference": {
    "file_name": "payment_gateway_k8s.log",
    "file_size_bytes": 2202010
  },
  "services": ["payment-service", "k8s_cluster"],
  "incident_documents": [
    {
      "name": "Kubernetes_OOMKilled_Policy.pdf",
      "content": "Kubernetes pod memory limits policy. Exit code 137 indicates OOMKilled state triggered by cgroup memory limit overflow."
    }
  ],
  "incident_images": [
    {
      "title": "K8s_Pod_Status_Console.png",
      "file_url": "/tmp/k8s_crashloop_error.png"
    }
  ]
}
```

### B. Graph Trajectory & Evidence Filtering
1. **Parallel Vision & Doc Nodes**:
   - `K8s_Pod_Status_Console.png`: **ACCEPTED** (Relevant CrashLoopBackOff screenshot)
   - `Kubernetes_OOMKilled_Policy.pdf`: **ACCEPTED** (Relevant OOMKilled policy doc)
2. **Log Tool Reasoning**: Queried `payment-service` logs, returning Exit Code 137 OOMKilled events.
3. **Self-RAG Decision**: `retrieval_required = True`. Search query: `"Kubernetes Pod Resource Limits & Memory Exhaustion Policy"`.
4. **Qdrant Retrieval & Reranking**: Reranked 3 candidate items, keeping 3 high-relevance items.

### C. Output Hypothesis
- **Primary Root Cause**: **Kubernetes Worker Container OOMKilled (Exit Code 137) due to HTTP Connection Memory Leak**
- **Confidence**: **95.5%**
- **Likely Mechanism**: Worker pods for `payment-service` exceeded the 512Mi cgroup memory limit due to unclosed HTTP client connection leaks in the payment processor module.
- **Recommended Action**: Apply HTTP connection pooling with explicit response body closing and scale container memory request/limit to 1Gi.
