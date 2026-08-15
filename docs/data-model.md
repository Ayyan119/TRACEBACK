# TRACEBACK — Frontend Data Models & Schema Specifications

This document defines the core data contracts for the TRACEBACK platform. These entity specifications are mirrored 1:1 between the TypeScript definitions (`/types`) and the target backend FastAPI Pydantic models.

---

## 1. Project

**Purpose:** Represents an isolated workspace or product ecosystem grouping related services, team members, and incidents.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `name` | `string` | Required | Project name (e.g. "Payment Gateway", "Core Infrastructure") |
| `slug` | `string` | Required | URL-safe slug identifier |
| `description` | `string` | Optional | Detailed description of the project scope |
| `environment` | `'production' \| 'staging' \| 'development'` | Required | Deployment environment tier |
| `serviceCount` | `number` | Required | Aggregated count of registered services |
| `activeIncidentCount` | `number` | Required | Count of open / investigating incidents |
| `createdAt` | `string` (ISO 8601) | Required | Creation timestamp |
| `updatedAt` | `string` (ISO 8601) | Required | Last modification timestamp |

**Relationships:**
- Has many `Service` entities (`Project 1:N Service`)
- Has many `Incident` entities (`Project 1:N Incident`)

---

## 2. Service

**Purpose:** Represents a microservice, monolithic application, database, or cloud infrastructure component monitored by TRACEBACK.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `projectId` | `string` | Required | Foreign key to parent `Project` |
| `name` | `string` | Required | Service name (e.g. `auth-service`, `payment-processor`) |
| `type` | `'backend' \| 'frontend' \| 'database' \| 'queue' \| 'third-party'` | Required | System tier type |
| `status` | `'healthy' \| 'degraded' \| 'critical' \| 'unknown'` | Required | Real-time health classification |
| `repositoryUrl` | `string` | Optional | Version control repository link |
| `ownerTeam` | `string` | Optional | Team responsible for maintaining service |
| `activeDeploymentId` | `string` | Optional | Currently deployed commit / release version |
| `createdAt` | `string` (ISO 8601) | Required | Service registration timestamp |

**Relationships:**
- Belongs to `Project` (`Service N:1 Project`)
- Has many `Deployment` entities (`Service 1:N Deployment`)
- Associated with `Incident` entities (`Service 1:N Incident`)

---

## 3. Incident

**Purpose:** Represents a reported production failure, alert spike, system outage, or performance degradation event under investigation.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `projectId` | `string` | Required | Foreign key to parent `Project` |
| `serviceId` | `string` | Optional | Foreign key to primary affected `Service` |
| `title` | `string` | Required | Human-readable title of the outage |
| `description` | `string` | Required | Detailed description or reporter notes |
| `severity` | `'SEV-0' \| 'SEV-1' \| 'SEV-2' \| 'SEV-3'` | Required | Outage severity classification |
| `status` | `'open' \| 'investigating' \| 'identified' \| 'mitigated' \| 'resolved'` | Required | Current incident state |
| `reporter` | `string` | Required | User or automated system (e.g. Datadog Alert) reporting |
| `startedAt` | `string` (ISO 8601) | Required | Estimated timestamp when problem began |
| `resolvedAt` | `string` (ISO 8601) | Optional | Outage resolution timestamp |
| `tags` | `string[]` | Required | System tags (e.g. `['database', 'timeout', '500-errors']`) |
| `createdAt` | `string` (ISO 8601) | Required | Record creation timestamp |
| `updatedAt` | `string` (ISO 8601) | Required | Last update timestamp |

**Relationships:**
- Belongs to `Project` (`Incident N:1 Project`)
- Optionally linked to `Service` (`Incident N:1 Service`)
- Has many `Evidence` items (`Incident 1:N Evidence`)
- Has one `Investigation` (`Incident 1:1 Investigation`)

---

## 4. Evidence

**Purpose:** Represents raw telemetry data or artifacts attached to an incident (logs, stack traces, metrics, screenshots, architecture docs).

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `incidentId` | `string` | Required | Foreign key to parent `Incident` |
| `type` | `'log' \| 'screenshot' \| 'metric' \| 'stack_trace' \| 'deployment' \| 'document'` | Required | Multi-modal evidence artifact type |
| `title` | `string` | Required | Display name or file name |
| `source` | `string` | Required | Origin system (e.g. Datadog, CloudWatch, User Upload) |
| `fileUrl` | `string` | Optional | Storage location URL (MinIO bucket path) |
| `fileSize` | `number` | Optional | File size in bytes |
| `mimeType` | `string` | Optional | Standard MIME type string |
| `status` | `'selected' \| 'uploading' \| 'uploaded' \| 'processing' \| 'ready' \| 'failed'` | Required | Processing lifecycle state |
| `rawContent` | `string` | Optional | Text payload for log snippets or stack traces |
| `metadata` | `Record<string, unknown>` | Optional | Structured Key-Value attributes |
| `uploadedAt` | `string` (ISO 8601) | Required | Upload timestamp |

**Relationships:**
- Belongs to `Incident` (`Evidence N:1 Incident`)
- Has many `LogEvent` entities if `type === 'log'` (`Evidence 1:N LogEvent`)

---

## 5. Investigation

**Purpose:** Encapsulates the overall state, multi-agent AI execution, hypotheses, evidence correlation, and recommendations for an incident.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `incidentId` | `string` | Required | Foreign key to parent `Incident` |
| `status` | `'idle' \| 'starting' \| 'analyzing' \| 'retrieving_evidence' \| 'generating_hypotheses' \| 'validating' \| 'completed' \| 'failed'` | Required | AI pipeline lifecycle state |
| `progress` | `number` | Required | Overall progress percentage (0 - 100) |
| `currentStep` | `string` | Required | Human-readable explanation of active task |
| `executiveSummary` | `string` | Optional | High-level summary of root cause analysis |
| `rootCause` | `string` | Optional | Definitive identified failure origin |
| `confidenceScore` | `number` | Optional | AI confidence level (0.0 to 1.0) |
| `startedAt` | `string` (ISO 8601) | Optional | Investigation initiation time |
| `completedAt` | `string` (ISO 8601) | Optional | Investigation completion time |
| `errorMessage` | `string` | Optional | Failure description if status is 'failed' |

**Relationships:**
- Belongs to `Incident` (`Investigation 1:1 Incident`)
- Has many `Hypothesis` entities (`Investigation 1:N Hypothesis`)
- Has many `TimelineEvent` entities (`Investigation 1:N TimelineEvent`)
- Has many `Recommendation` entities (`Investigation 1:N Recommendation`)
- Has many `EvidenceGap` entities (`Investigation 1:N EvidenceGap`)

---

## 6. Hypothesis

**Purpose:** Represents a plausible explanation generated by the AI model explaining why the outage occurred, backed by probability scores and evidence links.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `investigationId` | `string` | Required | Foreign key to parent `Investigation` |
| `title` | `string` | Required | Concise statement of hypothesis |
| `description` | `string` | Required | In-depth technical breakdown |
| `probability` | `number` | Required | Calculated likelihood score (0.00 to 1.00) |
| `status` | `'validating' \| 'confirmed' \| 'rejected' \| 'inconclusive'` | Required | Verification status |
| `supportingEvidenceIds` | `string[]` | Required | List of evidence IDs validating this hypothesis |
| `refutingEvidenceIds` | `string[]` | Optional | List of evidence IDs contradicting this hypothesis |

**Relationships:**
- Belongs to `Investigation` (`Hypothesis N:1 Investigation`)
- Links to `Evidence` (`Hypothesis N:M Evidence`)

---

## 7. TimelineEvent

**Purpose:** Represents a chronological milestone leading up to, during, or following an incident (e.g. config change, error spike, deployment, alert).

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `investigationId` | `string` | Required | Foreign key to parent `Investigation` |
| `timestamp` | `string` (ISO 8601) | Required | Precise occurrence time |
| `title` | `string` | Required | Event title |
| `description` | `string` | Required | Detailed event breakdown |
| `category` | `'deployment' \| 'alert' \| 'anomaly' \| 'config_change' \| 'action'` | Required | Event type taxonomy |
| `severity` | `'info' \| 'warning' \| 'critical'` | Required | Impact level |
| `relatedEvidenceId` | `string` | Optional | Linked evidence ID |

**Relationships:**
- Belongs to `Investigation` (`TimelineEvent N:1 Investigation`)
- Optionally links to `Evidence` (`TimelineEvent N:1 Evidence`)

---

## 8. Recommendation

**Purpose:** Represents a suggested fix, mitigation step, rollback command, or long-term preventive action generated by TRACEBACK.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `investigationId` | `string` | Required | Foreign key to parent `Investigation` |
| `title` | `string` | Required | Summary of recommended action |
| `actionType` | `'rollback' \| 'config_update' \| 'code_fix' \| 'scale_resource' \| 'post_mortem'` | Required | Categorization of fix |
| `priority` | `'immediate' \| 'short_term' \| 'long_term'` | Required | Urgency tier |
| `command` | `string` | Optional | Executable CLI / kubectl / git command snippet |
| `codeDiff` | `string` | Optional | Unified code diff snippet showing patch |
| `status` | `'proposed' \| 'applied' \| 'dismissed'` | Required | Resolution status |

**Relationships:**
- Belongs to `Investigation` (`Recommendation N:1 Investigation`)

---

## 9. EvidenceGap

**Purpose:** Identifies missing data points required by AI agents to achieve higher confidence in root cause determination.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `investigationId` | `string` | Required | Foreign key to parent `Investigation` |
| `missingDataType` | `'application_logs' \| 'database_metrics' \| 'git_diff' \| 'network_spans'` | Required | Category of missing information |
| `description` | `string` | Required | Explanation of why this data is needed |
| `impact` | `'high' \| 'medium' \| 'low'` | Required | Effect of missing data on hypothesis confidence |
| `actionPrompt` | `string` | Required | Suggested user action (e.g. "Upload DB connection pool logs") |

**Relationships:**
- Belongs to `Investigation` (`EvidenceGap N:1 Investigation`)

---

## 10. LogEvent

**Purpose:** Structured log record parsed from log files or telemetry streams for display in the LogViewer.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `evidenceId` | `string` | Required | Foreign key to parent `Evidence` artifact |
| `timestamp` | `string` (ISO 8601) | Required | Log entry timestamp |
| `level` | `'DEBUG' \| 'INFO' \| 'WARN' \| 'ERROR' \| 'FATAL'` | Required | Standard log level |
| `service` | `string` | Required | Emitting service name |
| `message` | `string` | Required | Raw log message text |
| `stackTrace` | `string` | Optional | Full stack trace string if log level is ERROR/FATAL |
| `attributes` | `Record<string, unknown>` | Optional | Structured JSON fields (e.g. `trace_id`, `user_id`) |

**Relationships:**
- Belongs to `Evidence` (`LogEvent N:1 Evidence`)

---

## 11. KnowledgeDocument

**Purpose:** Technical documentation, runbooks, architectural diagrams, or historical post-mortems stored in vector database (Qdrant) for similarity retrieval.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `title` | `string` | Required | Document title |
| `type` | `'runbook' \| 'post_mortem' \| 'architecture_doc' \| 'api_spec'` | Required | Knowledge category |
| `summary` | `string` | Required | High-level summary |
| `content` | `string` | Optional | Full markdown content |
| `sourceUrl` | `string` | Optional | Link to original document (Confluence, Notion, GitHub) |
| `tags` | `string[]` | Required | Classification tags |
| `updatedAt` | `string` (ISO 8601) | Required | Last update timestamp |

---

## 12. Deployment

**Purpose:** Metadata tracking code or infrastructure deployments associated with services.

| Field Name | Type | Required / Optional | Description |
|---|---|---|---|
| `id` | `string` | Required | Unique UUID string |
| `serviceId` | `string` | Required | Foreign key to `Service` |
| `commitHash` | `string` | Required | Git commit SHA |
| `author` | `string` | Required | Engineer who authored / deployed release |
| `environment` | `string` | Required | Deployment environment (`production`) |
| `deployedAt` | `string` (ISO 8601) | Required | Deployment timestamp |
| `changelog` | `string` | Optional | Summary of changes included |
