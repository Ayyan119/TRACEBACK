# TRACEBACK — REST API Contract Specifications

This document defines the HTTP REST API interface contract between the TRACEBACK frontend client and backend services (FastAPI).

---

## Standard Error Response Format

All error responses strictly follow the RFC 7807 Problem Details schema:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "The requested incident does not exist.",
    "details": {
      "incidentId": "inc-999"
    },
    "timestamp": "2026-08-14T08:00:00Z"
  }
}
```

---

## 1. Projects Endpoints

### `GET /projects`
Retrieves a list of accessible workspace projects.

- **Query Parameters:** `search` (optional string), `environment` (optional string)
- **Response `200 OK`:**
```json
{
  "projects": [
    {
      "id": "proj-01",
      "name": "Payments Ecosystem",
      "slug": "payments-ecosystem",
      "description": "Core payment gateway and billing infrastructure",
      "environment": "production",
      "serviceCount": 4,
      "activeIncidentCount": 1,
      "createdAt": "2026-01-10T12:00:00Z",
      "updatedAt": "2026-08-14T07:30:00Z"
    }
  ],
  "total": 1
}
```

### `GET /projects/{id}`
Retrieves detailed metadata for a specific project.

- **Response `200 OK`:** Returns single `Project` entity object.
- **Errors:** `404 Not Found` if project ID does not exist.

---

## 2. Incidents Endpoints

### `GET /incidents`
Lists incidents with filtering and pagination support.

- **Query Parameters:** 
  - `projectId` (optional string)
  - `serviceId` (optional string)
  - `severity` (optional `SEV-0` | `SEV-1` | `SEV-2` | `SEV-3`)
  - `status` (optional `open` | `investigating` | `identified` | `mitigated` | `resolved`)
  - `page` (default `1`)
  - `limit` (default `20`)
- **Response `200 OK`:**
```json
{
  "incidents": [
    {
      "id": "inc-101",
      "projectId": "proj-01",
      "serviceId": "srv-payment-api",
      "title": "Payment API 504 Gateway Timeouts during Peak Load",
      "description": "504 Gateway timeouts spiked to 18% following v2.4.1 deployment.",
      "severity": "SEV-1",
      "status": "investigating",
      "reporter": "Datadog Alert Bot",
      "startedAt": "2026-08-14T06:15:00Z",
      "resolvedAt": null,
      "tags": ["payment", "timeout", "redis", "postgres"],
      "createdAt": "2026-08-14T06:16:10Z",
      "updatedAt": "2026-08-14T07:45:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "totalPages": 1
  }
}
```

### `POST /incidents`
Creates a new incident record.

- **Request Body:**
```json
{
  "projectId": "proj-01",
  "serviceId": "srv-payment-api",
  "title": "Database Connection Pool Exhaustion in Auth Service",
  "description": "Auth service failing authentication requests due to pool timeout.",
  "severity": "SEV-0",
  "startedAt": "2026-08-14T07:50:00Z",
  "tags": ["auth", "database", "connection-pool"]
}
```
- **Response `201 Created`:** Returns created `Incident` object.

### `GET /incidents/{id}`
Retrieves full details for a specific incident.

- **Response `200 OK`:** Single `Incident` entity object.
- **Errors:** `404 Not Found`.

---

## 3. Evidence Endpoints

### `POST /incidents/{id}/evidence`
Attaches evidence file or raw text snippet to an incident.

- **Request Format:** `multipart/form-data` or `application/json`
- **JSON Payload Example:**
```json
{
  "type": "log",
  "title": "auth-service-stdout.log",
  "source": "CloudWatch Upload",
  "rawContent": "[ERROR] 2026-08-14T07:51:02Z - Connection pool timeout: failed to acquire client after 3000ms"
}
```
- **Response `201 Created`:**
```json
{
  "id": "ev-501",
  "incidentId": "inc-101",
  "type": "log",
  "title": "auth-service-stdout.log",
  "source": "CloudWatch Upload",
  "fileUrl": "https://storage.traceback.internal/evidence/ev-501.log",
  "status": "processing",
  "uploadedAt": "2026-08-14T07:52:00Z"
}
```

### `GET /incidents/{id}/evidence`
Lists all evidence attached to an incident.

- **Response `200 OK`:**
```json
{
  "evidence": [
    {
      "id": "ev-501",
      "incidentId": "inc-101",
      "type": "log",
      "title": "auth-service-stdout.log",
      "source": "CloudWatch Upload",
      "status": "ready",
      "uploadedAt": "2026-08-14T07:52:00Z"
    }
  ]
}
```

---

## 4. Investigation Endpoints

### `POST /incidents/{id}/investigate`
Triggers or restarts the multi-agent AI root cause investigation pipeline.

- **Request Body:**
```json
{
  "forceRestart": false,
  "focusAreas": ["database", "recent_deployments"]
}
```
- **Response `202 Accepted`:**
```json
{
  "investigationId": "inv-301",
  "incidentId": "inc-101",
  "status": "starting",
  "message": "AI multi-agent investigation pipeline initialized."
}
```

### `GET /incidents/{id}/investigation`
Retrieves current investigation execution state, hypotheses, timeline, and recommendations.

- **Response `200 OK`:**
```json
{
  "id": "inv-301",
  "incidentId": "inc-101",
  "status": "completed",
  "progress": 100,
  "currentStep": "Investigation complete. Root cause identified.",
  "executiveSummary": "PostgreSQL connection pool exhaustion caused by unclosed DB connections in new v2.4.1 refund handler.",
  "rootCause": "Unclosed database transaction block in payment-service refund route introduced in commit d8f3a9e.",
  "confidenceScore": 0.94,
  "startedAt": "2026-08-14T07:55:00Z",
  "completedAt": "2026-08-14T07:58:30Z",
  "hypotheses": [
    {
      "id": "hyp-01",
      "investigationId": "inv-301",
      "title": "Unclosed Postgres Connection Leak in Refund Route",
      "description": "Commit d8f3a9e introduced a missing defer db.Close() statement in the refund API execution path.",
      "probability": 0.94,
      "status": "confirmed",
      "supportingEvidenceIds": ["ev-501", "ev-502"]
    }
  ],
  "timeline": [
    {
      "id": "tl-01",
      "investigationId": "inv-301",
      "timestamp": "2026-08-14T06:00:00Z",
      "title": "Deployment of v2.4.1",
      "description": "Deployed commit d8f3a9e to production",
      "category": "deployment",
      "severity": "info"
    }
  ],
  "recommendations": [
    {
      "id": "rec-01",
      "investigationId": "inv-301",
      "title": "Rollback payment-service to v2.4.0",
      "actionType": "rollback",
      "priority": "immediate",
      "command": "kubectl rollout undo deployment/payment-service -n production",
      "status": "proposed"
    }
  ],
  "evidenceGaps": []
}
```

---

## 5. Logs Endpoints

### `GET /incidents/{id}/logs`
Queries parsed log events attached to an incident.

- **Query Parameters:** `level` (`ERROR` | `WARN` | `INFO`), `search` (text query), `page`, `limit`
- **Response `200 OK`:**
```json
{
  "logs": [
    {
      "id": "log-901",
      "evidenceId": "ev-501",
      "timestamp": "2026-08-14T07:51:02Z",
      "level": "ERROR",
      "service": "payment-service",
      "message": "FATAL: remaining connection slots are reserved for non-replication superuser connections",
      "stackTrace": "goroutine 421 [running]:\ngithub.com/payments/db.AcquireClient(...)"
    }
  ],
  "total": 1
}
```

### `GET /incidents/{id}/logs/statistics`
Retrieves aggregated log distribution by error level and time buckets.

- **Response `200 OK`:**
```json
{
  "totalLogs": 1420,
  "errorCount": 382,
  "warnCount": 110,
  "infoCount": 928,
  "levelBreakdown": {
    "ERROR": 382,
    "WARN": 110,
    "INFO": 928
  }
}
```

---

## 6. Knowledge Endpoints

### `GET /knowledge`
Searches vector knowledge base for past incident post-mortems and runbooks.

- **Query Parameters:** `query` (semantic search term), `type` (`runbook` | `post_mortem`)
- **Response `200 OK`:**
```json
{
  "documents": [
    {
      "id": "kn-101",
      "title": "Post-Mortem: Q2 Connection Pool Spike",
      "type": "post_mortem",
      "summary": "Detailed breakdown of connection leak in PgBouncer pooler.",
      "tags": ["postgres", "pgbouncer", "connection-leak"],
      "updatedAt": "2026-05-10T10:00:00Z"
    }
  ]
}
```

### `POST /knowledge`
Uploads new technical runbook or post-mortem document.

- **Response `201 Created`:** Created `KnowledgeDocument` object.

---

## 7. Services Endpoints

### `GET /services`
Lists registered services and their real-time health statuses.

- **Query Parameters:** `projectId` (optional)
- **Response `200 OK`:**
```json
{
  "services": [
    {
      "id": "srv-payment-api",
      "projectId": "proj-01",
      "name": "payment-api",
      "type": "backend",
      "status": "degraded",
      "ownerTeam": "Payments Platform",
      "createdAt": "2026-01-10T12:00:00Z"
    }
  ]
}
```
