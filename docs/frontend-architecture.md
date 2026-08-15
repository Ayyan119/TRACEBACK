# TRACEBACK — Frontend Architecture Specification

> **Product Tagline:** "Find what changed. Fix what broke."  
> **Target Persona:** Software Engineers, DevOps, Site Reliability Engineers (SRE)  
> **Platform Purpose:** AI-powered production incident investigation platform for root cause analysis, evidence correlation, and automated incident remediation recommendations.

---

## 1. Product Overview

TRACEBACK is an enterprise-grade AI production incident investigation workspace designed for rapid triage, telemetry correlation, log analysis, and root cause discovery. It transforms raw incident artifacts (logs, stack traces, metrics, APM spans, deployments, technical docs) into clear hypotheses, evidence chains, and actionable fixes.

### Key Capabilities
- **Multi-Modal Evidence Ingestion:** Ingest raw text logs, stack traces, screenshots, CSV/Prometheus metric exports, deployment manifests, and architectural docs.
- **AI-Guided Investigation Pipeline:** Single LangGraph investigation agent/workflow with specialized tools exposed via real-time execution state machines (analyzing, retrieving evidence, generating hypotheses, validating).
- **Interactive Evidence Chain & Timeline:** Reconstruct precise chronologies leading up to failure points, showing correlated code commits, deployments, and log anomalies.
- **Knowledge Base & Past Incidents Correlation:** Vector-indexed historical resolution discovery (Qdrant backplane) to prevent repeating past outages.

---

## 2. User Workflows

```
┌────────────────┐     ┌────────────────┐     ┌───────────────────────┐     ┌──────────────────────┐
│ Incident       │ ──> │ Evidence       │ ──> │ Automated             │ ──> │ Root Cause           │
│ Creation       │     │ Attachment     │     │ Investigation         │     │ & Remediation        │
│ (Manual/Alert) │     │ (Logs/Metrics) │     │ (LangGraph Execution) │     │ (Action Plan)        │
└────────────────┘     └────────────────┘     └───────────────────────┘     └──────────────────────┘
```

### Workflow A: Incident Triage & Investigation Initiator
1. Engineer receives an alert or customer report.
2. Navigates to `/incidents/new` or opens an existing unresolved incident.
3. Attaches relevant logs, stack traces, or deployment commits.
4. Triggers **"Start AI Investigation"** (`POST /incidents/{id}/investigate`).
5. Monitors real-time investigation stages in `/incidents/{id}/investigation`.
6. Reviews generated hypotheses, evidence strength, timeline events, and recommendation action plans.

### Workflow B: Post-Mortem & Knowledge Base Search
1. SRE inspects `/knowledge` to query past outages matching symptom patterns (e.g., `Redis connection pool exhaustion`).
2. Reviews past incident timelines, root causes, and post-mortem notes.
3. Links verified resolution docs to active service profiles.

### Workflow C: Service Topology & Health Inspection
1. DevOps team reviews `/services` to check component dependency trees, recent deployment changes, and associated incident history per service.

---

## 3. Page Architecture & Route Breakdown

| Route | Purpose | User Persona | Data Dependencies | API Endpoints | Key Components | Loading State | Error State | Empty State |
|---|---|---|---|---|---|---|---|---|
| `/dashboard` | System overview, active incidents, recent investigation activity | Dev, SRE, DevOps | Active incidents, service health status, recent investigations | `GET /incidents`, `GET /services` | `IncidentTable`, `ServiceCard`, `InvestigationActivity` | Skeleton cards & table | Alert banner with retry button | "No active incidents. Systems operational." |
| `/projects` | List all projects/workspaces | Dev Lead, SRE | Project metadata, service counts, active incident counts | `GET /projects` | `ProjectGrid`, `ProjectCard` | Grid skeleton cards | Error card | "No projects found. Create your first project." |
| `/projects/[projectId]` | Detailed project view with associated services & incidents | Dev, SRE | Project details, service list, project incidents | `GET /projects/{id}`, `GET /incidents`, `GET /services` | `ProjectHeader`, `ServiceList`, `IncidentTable` | Full-page skeleton | Project not found error state | "No services or incidents linked to this project." |
| `/incidents` | Incident filterable list & status tracker | Dev, SRE | Incident list with status, severity, service, timestamp | `GET /incidents` | `IncidentTable`, `IncidentFilterBar`, `SeverityBadge` | Table row skeletons | Data fetch failure banner | "No incidents match the selected filters." |
| `/incidents/new` | Create incident & upload initial evidence | Dev, SRE | Services list, deployment references | `GET /services`, `POST /incidents` | `IncidentForm`, `EvidenceUploader` | Form field loader | Validation errors, submission failure toast | N/A |
| `/incidents/[incidentId]` | Incident summary overview & evidence repository | Dev, SRE | Incident details, evidence list, attached logs | `GET /incidents/{id}`, `GET /incidents/{id}/evidence` | `IncidentHeader`, `EvidenceList`, `EvidenceUploader`, `IncidentOverview` | Detailed skeleton dashboard | Incident 404 or access denied | "No evidence attached to this incident yet." |
| `/incidents/[incidentId]/investigation` | AI Investigation workbench | Dev, SRE | Investigation state, hypotheses, timeline, recommendations | `GET /incidents/{id}/investigation`, `POST /incidents/{id}/investigate` | `InvestigationHeader`, `ExecutiveSummary`, `HypothesisCard`, `Timeline`, `EvidenceChain`, `RecommendationList` | Shimmer workbench & state indicator | Investigation failure state with restart option | "Investigation not started. Click 'Start Investigation'." |
| `/knowledge` | Knowledge base search & past incidents repository | Dev, SRE | Vector-searchable documents & historical incidents | `GET /knowledge` | `KnowledgeSearch`, `KnowledgeTable` | Table skeleton | Search error banner | "No knowledge documents indexed." |
| `/knowledge/documents` | List & upload technical docs | Dev, SRE | Document list | `GET /knowledge?type=document`, `POST /knowledge` | `KnowledgeTable`, `DocumentUploader` | Table skeleton | Document fetch failure | "No documents uploaded." |
| `/knowledge/incidents` | Historical closed incidents index | Dev, SRE | Closed incident list | `GET /knowledge?type=incident` | `KnowledgeTable` | Table skeleton | Fetch failure | "No resolved incidents recorded." |
| `/services` | Service catalog & health monitoring | DevOps, SRE | Service catalog, error rates, dependencies | `GET /services` | `ServiceGrid`, `ServiceCard`, `DependencyGraph` | Grid skeletons | Service registry error | "No services registered in catalog." |
| `/settings` | Workspace, API keys, and notification configs | Admin, Lead | Workspace configuration | Local/Mock setting endpoints | `SettingsForm`, `APIKeyManager` | Form field skeleton | Save failure toast | N/A |

---

## 4. Component Architecture

```
┌────────────────────────────────────────────────────────────────────────┐
│                          App Layout Architecture                       │
├────────────────────────────────────────────────────────────────────────┤
│ ┌────────────────────────────────────────────────────────────────────┐ │
│ │ Topbar (ProjectSelector, GlobalSearch, WorkspaceContext, ThemeToggle)│ │
│ └────────────────────────────────────────────────────────────────────┘ │
│ ┌───────────────┬────────────────────────────────────────────────────┐ │
│ │ Sidebar       │ Main Content Region (Page Views)                   │ │
│ │               │                                                    │ │
│ │ - Dashboard   │  ┌───────────────────────────────────────────────┐ │ │
│ │ - Projects    │  │ Domain Components                             │ │ │
│ │ - Incidents   │  │ (InvestigationHeader, HypothesisCard, etc.)  │ │ │
│ │ - Knowledge   │  └───────────────────────────────────────────────┘ │ │
│ │ - Services    │  ┌───────────────────────────────────────────────┐ │ │
│ │ - Settings    │  │ Base UI Components                            │ │ │
│ │               │  │ (Button, Card, Badge, Modal, Input, Spinner) │ │ │
│ └───────────────┴──┴───────────────────────────────────────────────┴─┘ │
└────────────────────────────────────────────────────────────────────────┘
```

### Component Hierarchy & Layers
1. **Primitives (`components/ui/`):** Atomic UI elements built without business logic (Button, Card, Badge, Modal, Tabs, Input, Select, Tooltip, Skeleton, Toast).
2. **Layout (`components/layout/`):** Shell components handling page framing (`Sidebar`, `Topbar`, `ProjectSelector`, `GlobalSearch`, `PageHeader`, `Container`).
3. **Domain Components:**
   - `components/incidents/`: `IncidentTable`, `IncidentCard`, `IncidentForm`, `SeverityBadge`, `StatusBadge`.
   - `components/investigation/`: `InvestigationHeader`, `ExecutiveSummary`, `ImpactPanel`, `HypothesisCard`, `EvidenceChain`, `Timeline`, `RecommendationList`, `EvidenceGapPanel`, `InvestigationActivity`.
   - `components/logs/`: `LogViewer`, `LogFilterBar`, `LogStatisticsCard`, `StackTraceFormatter`.
   - `components/evidence/`: `EvidenceUploader`, `EvidenceList`, `EvidenceItemCard`, `UploadProgressModal`.
   - `components/knowledge/`: `KnowledgeTable`, `KnowledgeSearch`, `DocumentUploader`.
   - `components/services/`: `ServiceCard`, `ServiceGrid`, `ServiceHeader`.

---

## 5. Data Architecture

### Entity Core Relations
- **Project** (1) ──> (*) **Service**
- **Project** (1) ──> (*) **Incident**
- **Incident** (1) ──> (*) **Evidence**
- **Incident** (1) ──> (0..1) **Investigation**
- **Investigation** (1) ──> (*) **Hypothesis**
- **Investigation** (1) ──> (*) **TimelineEvent**
- **Investigation** (1) ──> (*) **Recommendation**
- **Investigation** (1) ──> (*) **EvidenceGap**
- **Evidence** (1) ──> (*) **LogEvent** (when type is log)

---

## 6. State Management Strategy

To ensure high performance and prevent unnecessary re-renders, state is split into 4 clear tiers:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ Tier 1: Local Component State (React useState / useReducer)             │
│ Focus: UI state like modal open/close, dropdown toggles, draft inputs    │
├─────────────────────────────────────────────────────────────────────────┤
│ Tier 2: URL State (Next.js useSearchParams / nuqs)                      │
│ Focus: Search queries, filters, active tabs, selected timeline events   │
├─────────────────────────────────────────────────────────────────────────┤
│ Tier 3: Server State (Data-Fetching Facade with Caching)                │
│ Focus: Incident lists, investigation status, logs, knowledge base       │
├─────────────────────────────────────────────────────────────────────────┤
│ Tier 4: Application Context / Store (Zustand)                           │
│ Focus: Current active project ID, global notification toast queue       │
└─────────────────────────────────────────────────────────────────────────┘
```

> **Rule:** No Redux or heavy global state manager. Server state stays cached via the API client layer; UI transient state stays in components or URL.

---

## 7. API Integration Strategy (Facade & Adapter Pattern)

The API layer is built using an **Interface-Driven Facade Pattern**. The UI components import higher-level API functions from `lib/api/` and never directly touch `axios`, `fetch`, or mock data objects.

```
┌─────────────────────────────────────────────────────────────┐
│                      UI Components                          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Calls methods like getIncident(id)
┌──────────────────────────────▼──────────────────────────────┐
│                    API Client Facade                        │
│                   (`lib/api/index.ts`)                      │
└──────────────┬──────────────────────────────┬───────────────┘
               │ if mode == 'mock'            │ if mode == 'real'
┌──────────────▼──────────────┐┌──────────────▼──────────────┐
│       MockApiClient         ││        FastApiClient        │
│   (`lib/api/mock/`)         ││   (`lib/api/fastapi/`)      │
└─────────────────────────────┘└─────────────────────────────┘
```

- **Environment Flag:** Controlled via `NEXT_PUBLIC_API_MODE=mock|real`.
- **Zero UI Changes:** Switching between mock and real FastAPI backend requires changing 1 environment variable.

---

## 8. File Upload Architecture

Evidence files (logs, screenshots, stack traces, metrics, docs) follow a strict 6-stage lifecycle:

```
[Selected] ──> [Uploading] ──> [Uploaded] ──> [Processing] ──> [Ready]
                                                    └──> [Failed]
```

### Upload Lifecycle States
1. **`selected`:** User selects file via drag & drop or file picker. Client calculates checksum & file size.
2. **`uploading`:** File chunks are sent to presigned URL (MinIO/S3 backplane). Progress bar updates (`0-100%`).
3. **`uploaded`:** Binary upload is complete. Backend confirmation acknowledged.
4. **`processing`:** Backend pipeline parses log syntax, generates embeddings (BGE), indexes in vector DB (Qdrant), or runs OCR on screenshots.
5. **`ready`:** Parsing complete. Evidence items are attached and available for AI investigation.
6. **`failed`:** Network failure or parsing error. User can click "Retry".

---

## 9. Mock-Data Strategy

- Mock data resides strictly under `mock-data/` directory.
- Structured factories (`mock-data/incidents.ts`, `mock-data/investigations.ts`, etc.) return strongly typed domain objects matching `/types`.
- Mock API introduces artificial network latencies (`300ms - 800ms`) and optional mock error flags to test loading skeletons and error boundaries during development.

---

## 10. Backend Integration Boundary & Decoupling

The frontend communicates **exclusively with the FastAPI API gateway**. It remains strictly decoupled from all backend storage, vector retrieval, orchestration, and model inference systems.

### 10.1 Backend Technology Stack (Server Side Only)
The production backend consists of:
- **FastAPI:** Core REST API gateway and request handler
- **PostgreSQL:** Relational database for projects, incidents, metadata, and user records
- **Qdrant:** Vector database storing embedded documents, runbooks, and historical post-mortems
- **LangGraph:** Single investigation agent/workflow with specialized tools for root cause analysis
- **Open-source LLM & Multimodal LLM:** Model inference engines for log reasoning, OCR, and hypothesis generation
- **Redis & Celery:** Task queue and message broker for background job processing
- **MinIO:** Object storage for evidence files, screenshots, and raw logs
- **BGE Embeddings & BGE Reranker:** Vector embedding generation and semantic search reranking
- **OpenTelemetry:** Distributed tracing and observability telemetry ingestion

### 10.2 Frontend Boundary Rules
1. **Exclusive Communication Channel:** The frontend communicates ONLY with FastAPI (`lib/api/fastapi-client.ts`).
2. **Zero Backend Tech Leakage:** The frontend MUST NEVER directly implement, import, or manage Qdrant vector search, BGE embeddings, reranking algorithms, LangGraph execution graphs, PostgreSQL queries, Redis keys, Celery tasks, MinIO SDKs, or direct LLM prompt invocations.
3. **Single LangGraph Workflow:** The AI investigation pipeline is driven by a single LangGraph investigation workflow with specialized tools on the backend. The frontend simply consumes clean status states (`idle`, `analyzing`, `completed`, `failed`) and structured payload contracts.
4. **Knowledge UI Interface:** The `/knowledge` UI serves as a clean presentation interface for backend-powered semantic vector search (`GET /knowledge?query=...`). Vector encoding and similarity scoring occur strictly on the server.
5. **Server-Side Log Processing:** `LogViewer` relies on server-side filtering, query matching, and pagination (`GET /incidents/{id}/logs`), avoiding unnecessary client-side virtualization overhead.

---

## 11. Error, Loading, & Empty State Strategy

### Standardized UI States
- **Loading:** Every major component has a dedicated Skeleton counterpart (e.g., `IncidentTableSkeleton`, `InvestigationHeaderSkeleton`).
- **Error:** Component-level `ErrorBoundary` catches unexpected crashes; API errors show inline `AlertBanner` with diagnostic codes and a "Retry" button.
- **Empty:** Standardized `EmptyState` component with illustration/icon, clear explanation, and primary action button (e.g., "Create Incident" or "Attach Evidence").

---

## 12. Responsive Strategy

- **Desktop First for Heavy Workstations:** Primary focus on 1440px+ and 1080px resolution for dual-pane log viewing, multi-column hypothesis comparison, and timeline graphs.
- **Adaptive Breakpoints:**
  - `sm` (640px): Mobile view for status checks and incident alerts.
  - `md` (768px): Tablet layout with collapsible sidebar.
  - `lg` (1024px): Standard laptop layout.
  - `xl` (1280px+): Dual-pane workstation view.

---

## 13. Theme & Design-Token Strategy

**Design Core Principle:** *"Quiet confidence."* Enterprise terminal aesthetic for mission-critical operations. Crisp lines, high readability, zero flashy gradients or cyberpunk clutter.

### CSS Custom Properties (`index.css`)

```css
:root {
  /* Dark Theme (Default) */
  --bg-app: #0F1115;
  --bg-surface: #191D24;
  --bg-surface-hover: #222731;
  --border-color: #2A3039;
  
  --text-primary: #E7EAF0;
  --text-secondary: #9AA3B2;
  --text-muted: #6B7280;
  
  --accent-primary: #4F8CFF;
  --accent-hover: #3B7BF0;
  --accent-subtle: rgba(79, 140, 255, 0.12);
  
  --status-success: #3FB950;
  --status-warning: #D29922;
  --status-danger: #F85149;
  --status-info: #58A6FF;

  --font-sans: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
  --font-mono: 'JetBrains Mono', monospace;
}

[data-theme='light'] {
  --bg-app: #F7F8FA;
  --bg-surface: #FFFFFF;
  --bg-surface-hover: #F0F2F5;
  --border-color: #D9DEE7;
  
  --text-primary: #171A21;
  --text-secondary: #5E6878;
  --text-muted: #8892A0;
  
  --accent-primary: #356AE6;
  --accent-hover: #2655C4;
  --accent-subtle: rgba(53, 106, 230, 0.1);
  
  --status-success: #218739;
  --status-warning: #A66B00;
  --status-danger: #D1242F;
  --status-info: #0969DA;
}
```

---

## 14. Folder Structure Architecture

```
app/
├── (routes)/
│   ├── dashboard/page.tsx
│   ├── projects/
│   │   ├── page.tsx
│   │   └── [projectId]/page.tsx
│   ├── incidents/
│   │   ├── page.tsx
│   │   ├── new/page.tsx
│   │   └── [incidentId]/
│   │       ├── page.tsx
│   │       └── investigation/page.tsx
│   ├── knowledge/
│   │   ├── page.tsx
│   │   ├── documents/page.tsx
│   │   └── incidents/page.tsx
│   ├── services/page.tsx
│   └── settings/page.tsx
├── layout.tsx
├── page.tsx
└── globals.css

components/
├── ui/                 # Atomic design primitives (Button, Card, Badge, Modal, Input, Tabs)
├── layout/             # Application framing (Sidebar, Topbar, ProjectSelector, GlobalSearch)
├── incidents/          # Incident management domain components
├── investigation/      # AI investigation workbench components
├── logs/               # Log viewer & stack trace formatting
├── evidence/           # Multi-modal file upload & list components
├── knowledge/          # Knowledge base & historical incident components
└── services/           # Service catalog & health cards

lib/
├── api/                # API Client Facade Layer (Interface, Mock Client, FastAPI Client)
│   ├── index.ts        # Primary API export point
│   ├── client.ts       # Base HTTP client with interperable fetch/axios wrappers
│   ├── mock-client.ts  # Mock implementation of ApiClient interface
│   └── fastapi-client.ts # Production FastAPI client implementation
├── utils/              # Utility helpers (formatting, date tools, classnames)
└── constants/          # Application constants & status mappings

types/                  # Centralized TypeScript Type Definitions
├── project.ts
├── incident.ts
├── evidence.ts
├── investigation.ts
├── log.ts
├── knowledge.ts
└── service.ts

hooks/                  # Custom React Hooks
├── useIncident.ts
├── useInvestigation.ts
├── useFileUpload.ts
├── useRealtimeStatus.ts
└── useProjects.ts

mock-data/              # Strongly-typed mock factories & fixtures
├── projects.ts
├── incidents.ts
├── evidence.ts
├── investigations.ts
├── logs.ts
├── knowledge.ts
└── services.ts

docs/                   # System & Frontend Architecture Specs
├── frontend-architecture.md
├── data-model.md
└── api-contract.md

public/                 # Static assets, branding, icons
```

---

## 15. Naming Conventions

- **Files & Directories:** kebab-case (`evidence-uploader.tsx`, `use-investigation.ts`).
- **Components:** PascalCase (`EvidenceUploader`, `HypothesisCard`).
- **Types & Interfaces:** PascalCase (`Incident`, `EvidenceItem`, `InvestigationStatus`).
- **API Functions:** camelCase starting with verbs (`getIncident`, `createEvidence`, `startInvestigation`).
- **CSS Variables:** kebab-case with tier prefixes (`--bg-surface`, `--text-primary`, `--status-danger`).

---

## 16. Future Scalability Considerations

- **OpenTelemetry & Log Streaming:** LogViewer is built using virtualized lists (`react-window` pattern ready) to render 100,000+ log lines without UI lag.
- **WebSocket Upgrade Path:** Real-time polling client is wrapped inside `useRealtimeStatus` hook, allowing transparent drop-in upgrade to SSE or WebSockets without touching UI components.
- **Plugin Architecture for Integrations:** Service and Evidence models include extensible metadata fields for future PagerDuty, Datadog, GitHub, and Jira integrations.
