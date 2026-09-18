# Sentriq AI-SOC: Phase-by-Phase Implementation Prompts

This document provides structured, production-ready, copy-pasteable prompts to build the **Autonomous AI Security Operations Center (AI-SOC)** platform incrementally from scratch, strictly following the system requirements in [`PRD.md`](PRD.md).

---

## Quick Navigation

- [Phase 1: Core Foundation & Dockerized Infrastructure](#phase-1-core-foundation--dockerized-infrastructure)
  - [Prompt 1.1: Docker Desktop PostgreSQL & Project Scaffolding](#prompt-11-docker-desktop-postgresql--project-scaffolding)
  - [Prompt 1.2: FastAPI Backend Core & Database Setup](#prompt-12-fastapi-backend-core--database-setup)
  - [Prompt 1.3: React + Vite + Tailwind Enterprise Frontend](#prompt-13-react--vite--tailwind-enterprise-frontend)
- [Phase 2: Security Event Data Layer & Ingestion Pipeline](#phase-2-security-event-data-layer--ingestion-pipeline)
  - [Prompt 2.1: Common Security Event Model & Database Schema](#prompt-21-common-security-event-model--database-schema)
  - [Prompt 2.2: Synthetic Generator & Benchmark Data Ingestion](#prompt-22-synthetic-generator--benchmark-data-ingestion)
  - [Prompt 2.3: Security Logs API & Log Explorer Frontend](#prompt-23-security-logs-api--log-explorer-frontend)
- [Phase 3: Machine Learning Threat Detection Pipeline](#phase-3-machine-learning-threat-detection-pipeline)
  - [Prompt 3.1: ML Preprocessing & Feature Engineering](#prompt-31-ml-preprocessing--feature-engineering)
  - [Prompt 3.2: Model Training & Benchmark Evaluation (Binary + Multi-Class)](#prompt-32-model-training--benchmark-evaluation-binary--multi-class)
  - [Prompt 3.3: Inference Engine API & Threat Analysis Testbench](#prompt-33-inference-engine-api--threat-analysis-testbench)
- [Phase 4: Transparent Risk Scoring & Event Correlation Engine](#phase-4-transparent-risk-scoring--event-correlation-engine)
  - [Prompt 4.1: Deterministic Weighted Risk Scoring Engine](#prompt-41-deterministic-weighted-risk-scoring-engine)
  - [Prompt 4.2: Time-Window Event Correlation Engine](#prompt-42-time-window-event-correlation-engine)
  - [Prompt 4.3: Incident Management Lifecycle & Timeline UI](#prompt-43-incident-management-lifecycle--timeline-ui)
- [Phase 5: Real-Time Stream Simulation & WebSocket Telemetry](#phase-5-real-time-stream-simulation--websocket-telemetry)
  - [Prompt 5.1: Background Event Streamer & WebSocket Hub](#prompt-51-background-event-streamer--websocket-hub)
  - [Prompt 5.2: Live SOC Telemetry Dashboard with Real-Time KPIs & Charts](#prompt-52-live-soc-telemetry-dashboard-with-real-time-kpis--charts)
- [Phase 6: Explainable AI (XAI) & Threat Attribution](#phase-6-explainable-ai-xai--threat-attribution)
  - [Prompt 6.1: SHAP Model Explainability Engine & Feature Attribution](#prompt-61-shap-model-explainability-engine--feature-attribution)
  - [Prompt 6.2: Explainability Dashboard UI & Rule-to-XAI Bridge](#prompt-62-explainability-dashboard-ui--rule-to-xai-bridge)
- [Phase 7: AI-Assisted SOC Investigation & Multi-Agent Copilot](#phase-7-ai-assisted-soc-investigation--multi-agent-copilot)
  - [Prompt 7.1: Multi-Agent SOC Investigation Orchestrator](#prompt-71-multi-agent-soc-investigation-orchestrator)
  - [Prompt 7.2: Human-in-the-Loop Response Actions & Audit Log](#prompt-72-human-in-the-loop-response-actions--audit-log)
  - [Prompt 7.3: Automated Incident Report Generation (PDF/Markdown)](#prompt-73-automated-incident-report-generation-pdfmarkdown)
- [Phase 8: Comprehensive Evaluation, Docker Packaging & Faculty Demo](#phase-8-comprehensive-evaluation-docker-packaging--faculty-demo)
  - [Prompt 8.1: Full Benchmark Evaluation & Performance Metrics](#prompt-81-full-benchmark-evaluation--performance-metrics)
  - [Prompt 8.2: Complete Docker Desktop Multi-Container Compose](#prompt-82-complete-docker-desktop-multi-container-compose)
  - [Prompt 8.3: End-to-End Demonstration Script & Seed Scenarios](#prompt-83-end-to-end-demonstration-script--seed-scenarios)

---

## Architectural & Design Guidelines

Every phase must strictly adhere to these architectural standards:
1. **Design System & Palette (PRD Section 17)**:
   - **Theme**: Professional Enterprise SOC, calm, data-dense, dark mode.
   - **Background**: Deep navy-charcoal (`#0B1120` / `#0F172A`).
   - **Panels & Cards**: Dark slate (`#1E293B` / `#334155`).
   - **Borders**: Slate gray (`#334155` / `#475569`).
   - **Accents**: Steel blue (`#38BDF8`), muted teal (`#14B8A6`).
   - **Severity**: Low (Muted Green `#22C55E`), Medium (Warm Amber `#F59E0B`), High (Burnt Orange `#F97316`), Critical (Deep Red `#EF4444`).
   - **Prohibited**: Neon gradients, pink/purple AI glows, heavy glassmorphism, floating decorative cards.
2. **Database & Infrastructure**:
   - **PostgreSQL 16** containerized locally via **Docker Desktop** (`docker-compose.yml`) on port 5432 with persistent volume storage.
   - SQLAlchemy 2.0 with async sessions (`asyncpg`) or synchronous (`psycopg2`), managed with clean connection pooling.
3. **Backend Standards**:
   - Python 3.11+, FastAPI, Pydantic v2, clean layered architecture (`api/`, `core/`, `models/`, `schemas/`, `services/`, `ml/`).
4. **Frontend Standards**:
   - React 18+, TypeScript (strict mode), Vite, Tailwind CSS, Lucide React icons, Recharts, Axios.

---

## Phase 1: Core Foundation & Dockerized Infrastructure

### Prompt 1.1: Docker Desktop PostgreSQL & Project Scaffolding

```text
Act as a Senior Principal Cloud & DevOps Architect.
We are starting the implementation of the "Sentriq Autonomous AI-SOC" project based on PRD.md.
Our first objective is setting up the containerized infrastructure using Docker Desktop and scaffolding the root project structure.

Please perform the following tasks:
1. Create a root `docker-compose.yml` configured for Docker Desktop:
   - Service `db`: image `postgres:16-alpine`, container name `sentriq-postgres`, mapped to host port `5432:5432`.
   - Environment: `POSTGRES_DB=sentriq_soc`, `POSTGRES_USER=sentriq_admin`, `POSTGRES_PASSWORD=sentriq_secure_pass`.
   - Healthcheck using `pg_isready -U sentriq_admin -d sentriq_soc` (interval 5s, timeout 5s, retries 5).
   - Volume: `sentriq_pgdata` mounted to `/var/lib/postgresql/data` for persistent storage.
   - (Optional) Service `pgadmin`: image `dpage/pgadmin4:latest` on port `5050:80` for easy database visual management during development.
2. Create root project directory structure:
   - `backend/` (FastAPI application, models, services, ML engine)
   - `frontend/` (React + TypeScript + Vite dashboard)
   - `data/` (raw datasets, simulated logs, benchmark splits)
   - `models_store/` (serialized ML models and scalers)
   - `scripts/` (initialization, database seeding, data ingestion)
3. Create `.env.example` and `.gitignore` configured for Python (venv, __pycache__, .pytest_cache), Node (node_modules, dist), Docker data, and model binaries.
4. Provide clear verification instructions to run `docker compose up -d` in Docker Desktop and verify container health via PowerShell.
```

---

### Prompt 1.2: FastAPI Backend Core & Database Setup

```text
Act as a Lead Backend Engineer specializing in FastAPI and SQLAlchemy.
We are building Phase 1.2 of the Sentriq AI-SOC backend.

Requirements:
1. Initialize the `backend/` package with `pyproject.toml` or `requirements.txt` containing:
   - `fastapi`, `uvicorn[standard]`, `pydantic>=2.6`, `pydantic-settings`, `sqlalchemy>=2.0`, `psycopg2-binary`, `asyncpg`, `alembic`, `python-dotenv`, `pytest`, `httpx`.
2. Configure settings management in `backend/app/core/config.py` using `pydantic_settings.BaseSettings`:
   - Database connection string pointing to Docker Desktop PostgreSQL (`postgresql+asyncpg://sentriq_admin:sentriq_secure_pass@localhost:5432/sentriq_soc`).
   - CORS origins (allow `http://localhost:5173`).
   - Application metadata (Title: "Sentriq AI-SOC API", version: "1.0.0").
3. Create database session manager in `backend/app/core/database.py`:
   - Async engine with connection pooling (`pool_size=10`, `max_overflow=20`).
   - `Base` declarative model class with common mixins (`id` UUID/Int, `created_at`, `updated_at`).
   - Dependency `get_db()` providing an async database session with automatic commit/rollback.
4. Create initial database models in `backend/app/models/`:
   - `Incident` model: id, title, description, attack_category, severity (Low/Medium/High/Critical), status (Open/Investigating/Resolved/Closed), risk_score (Float 0-100), risk_level, confidence (Float), created_at, updated_at.
5. Create Pydantic schemas in `backend/app/schemas/incident.py` for request validation and response serialization.
6. Create REST endpoints in `backend/app/api/v1/incidents.py`:
   - `GET /api/v1/incidents`: list with pagination, status filter, and severity filter.
   - `GET /api/v1/incidents/{id}`: incident detail.
   - `POST /api/v1/incidents`: create incident.
   - `PATCH /api/v1/incidents/{id}/status`: transition status (Open -> Investigating -> Resolved -> Closed).
7. Implement health check endpoint `GET /api/v1/health` returning system status, database connectivity check, and timestamp.
8. Wire up `backend/app/main.py` with FastAPI app, CORS middleware, API router `/api/v1`, and graceful lifespan startup to verify DB connection.
9. Include an automatic database table creation or migration script so tables are immediately ready upon startup.
```

---

### Prompt 1.3: React + Vite + Tailwind Enterprise Frontend

```text
Act as a Senior Principal Frontend Engineer specializing in React, TypeScript, and Enterprise Security Dashboards.
We are implementing the Sentriq frontend application according to PRD Section 17 (UI/UX and Visual Design System).

Requirements:
1. Initialize the `frontend/` application using Vite (`react-ts` template) with dependencies:
   - `tailwindcss`, `postcss`, `autoprefixer`, `lucide-react`, `recharts`, `axios`, `react-router-dom`, `clsx`, `tailwind-merge`.
2. Configure `tailwind.config.js` with the PRD Section 17 enterprise palette:
   - Dark background: `soc-bg` (`#0B1120`), `soc-card` (`#1E293B`), `soc-card-hover` (`#334155`), `soc-border` (`#334155`).
   - Accents: `soc-accent` (`#38BDF8`), `soc-teal` (`#14B8A6`).
   - Severity: `soc-low` (`#22C55E`), `soc-medium` (`#F59E0B`), `soc-high` (`#F97316`), `soc-critical` (`#EF4444`).
   - Avoid purple/pink AI gradients, neon highlights, or blurry glassmorphism. Maintain a calm, professional, high-density layout.
3. Build common UI component library in `frontend/src/components/ui/`:
   - `Card`, `Badge` (with severity color mapping), `Button`, `Table`, `Modal`, `AlertIndicator`.
4. Create enterprise App Shell in `frontend/src/components/layout/`:
   - Top navigation bar: Sentriq logo/shield, system health pill (connected to Docker Desktop PostgreSQL), live clock (UTC/local), active alerts indicator.
   - Sidebar navigation: Dashboard, Security Logs, Threat Analysis, Incidents, Investigation Copilot, System Settings.
5. Create initial Dashboard page (`frontend/src/pages/Dashboard.tsx`):
   - 4 KPI cards: Processed Events, Active Incidents, Critical Incidents, High-Risk Detections.
   - Charts using Recharts: Threat Trend over time (Area/Line chart), Attack Category Distribution (Bar/Donut chart).
   - Recent Incidents table with severity badges, risk score progress bar, and status pill.
6. Configure API client in `frontend/src/services/api.ts` with Axios, base URL `http://localhost:8000/api/v1`, and response error interceptors.
```

---

## Phase 2: Security Event Data Layer & Ingestion Pipeline

### Prompt 2.1: Common Security Event Model & Database Schema

```text
Act as a Lead Security Data Architect.
According to PRD Section 7 (Core Security Event Model) and Section 6, we must design the foundational Security Event schema that serves as the common language across Ingestion, Machine Learning, Risk Scoring, and Correlation.

Requirements:
1. Create SQLAlchemy model `SecurityEvent` in `backend/app/models/event.py`:
   - `id`: UUID primary key.
   - `timestamp`: DateTime with timezone (indexed).
   - `source`: String (e.g., 'firewall', 'auth_service', 'ids', 'web_server', 'endpoint').
   - `event_type`: String (e.g., 'login_attempt', 'connection_request', 'port_probe', 'http_request').
   - `source_ip`: String (indexed).
   - `destination_ip`: String (indexed).
   - `source_port`: Integer nullable.
   - `destination_port`: Integer nullable.
   - `protocol`: String (e.g., 'TCP', 'UDP', 'ICMP', 'HTTP').
   - `user_identity`: String nullable (e.g., username).
   - `attack_type`: String (e.g., 'Normal', 'Brute Force', 'DoS', 'Port Scan', 'Web Attack', 'Exploitation').
   - `severity`: String ('Low', 'Medium', 'High', 'Critical').
   - `message`: Text / description.
   - `raw_features`: JSONB column storing original benchmark dataset features (e.g., packet rate, byte count, flag counts, connection duration).
   - `is_attack`: Boolean flag (0=Normal, 1=Attack).
   - `is_simulated`: Boolean flag (True for synthetic demo streams, False for benchmark data).
   - `incident_id`: Foreign key referencing `incidents.id` (nullable, for correlated events).
2. Create corresponding Pydantic v2 schemas in `backend/app/schemas/event.py`:
   - `SecurityEventBase`, `SecurityEventCreate`, `SecurityEventResponse`, `SecurityEventFilter`.
3. Create migration or table initialization script to apply this schema to the Docker Desktop PostgreSQL database with proper composite indexes on `(timestamp, source_ip)` and `(attack_type, severity)`.
```

---

### Prompt 2.2: Synthetic Generator & Benchmark Data Ingestion

```text
Act as a Senior Security Data Engineer.
We need to populate our Sentriq database with both realistic synthetic security logs and preprocessed public benchmark data (UNSW-NB15 / CIC-IDS2017 schema mapping) as required by PRD Section 6 and Section 12.

Requirements:
1. Implement a Synthetic Event Generator in `backend/app/services/data_generator.py`:
   - Generates benign baseline traffic: normal user logins, routine API traffic, internal microservice queries.
   - Implements PRD Section 12 Brute Force Scenario: Sequence of 5 to 15 failed authentication events from a single external IP (`198.51.100.45`) targeting user `admin` on SSH/Auth portal, followed by a suspicious successful login and privilege change.
   - Generates DoS traffic: burst of SYN/UDP floods with abnormal packet counts.
   - Generates Port Scanning: rapid sequential destination port queries (21, 22, 23, 80, 443, 8080, 3389) across target IP range.
   - Clearly flags all generated events with `is_simulated=True` and `[SIMULATED DEMO DATA]` prefix in messages.
2. Implement a Benchmark Dataset Loader in `backend/app/services/benchmark_loader.py`:
   - Parses UNSW-NB15 / CIC-IDS2017 CSV samples from `data/benchmark/`.
   - Maps raw columns (dur, proto, service, sbytes, dbytes, sttl, smean, attack_cat, label) into our standard `SecurityEvent` schema.
3. Create a CLI utility in `backend/scripts/seed_data.py`:
   - Option `--simulate-scenario brute_force` (injects Section 12 scenario).
   - Option `--seed-benchmark` (loads sample benchmark records).
   - Option `--clear` (clears existing test events).
4. Verify by running the seed script against Docker Desktop PostgreSQL and inspecting record counts.
```

---

### Prompt 2.3: Security Logs API & Log Explorer Frontend

```text
Act as a Full-Stack Security Engineer.
Build the Security Logs exploration capabilities for analysts as defined in PRD FR-02.

Requirements:
1. Backend REST Endpoints in `backend/app/api/v1/events.py`:
   - `GET /api/v1/events`:
     - Query parameters: `page`, `page_size`, `severity`, `attack_type`, `source`, `search` (text search in message/IP), `start_time`, `end_time`, `is_simulated`.
     - Returns paginated list with total count, pages, and summary metrics.
   - `GET /api/v1/events/{id}`: returns complete event details including `raw_features` JSON.
   - `POST /api/v1/events/simulate`: triggers generation of a test attack sequence on demand.
2. Frontend Log Explorer Page (`frontend/src/pages/SecurityLogs.tsx`):
   - Multi-filter bar: Search input, Severity dropdown (Low/Medium/High/Critical), Attack Type filter, Source filter, Simulated toggle.
   - Dense, high-readability security log table:
     - Columns: Timestamp, Severity Badge, Source, Event Type, Attack Category, Source IP -> Dest IP, Message, Actions.
   - Slide-over / Drawer panel on clicking an event:
     - Detailed overview, formatted JSON viewer for `raw_features`, detection attribution, and quick action "Analyze with ML Model".
   - Pagination controls and "Trigger Simulated Attack Scenario" button with toast notification.
```

---

## Phase 3: Machine Learning Threat Detection Pipeline

### Prompt 3.1: ML Preprocessing & Feature Engineering

```text
Act as a Senior Machine Learning Engineer specializing in Cyber Threat Detection.
We are implementing Phase 3 of Sentriq according to PRD Section 5.3, Section 6.3, and Section 21.

Requirements:
1. Create a reproducible feature engineering pipeline in `backend/app/ml/preprocessing.py`:
   - Define numeric features: packet counts, byte volumes, duration, port numbers, failure count in window.
   - Define categorical features: protocol, service, event source, flag types.
   - Use `scikit-learn`'s `ColumnTransformer` with `StandardScaler` for numeric columns and `OneHotEncoder(handle_unknown='ignore')` for categorical features.
   - Ensure target labels are isolated to prevent target leakage.
2. Build data pipeline validation:
   - Handle missing values gracefully (imputation with median for numeric, 'unknown' for categorical).
   - Export and version preprocessing artifacts using `joblib` in `models_store/preprocessor.joblib`.
3. Provide automated unit tests verifying that arbitrary raw security event dictionaries can be normalized into expected feature matrices without dimension mismatch.
```

---

### Prompt 3.2: Model Training & Benchmark Evaluation (Binary + Multi-Class)

```text
Act as a Principal ML Scientist.
Implement model training, cross-validation, and rigorous evaluation for Sentriq's threat classification layer following PRD Section 5.3, Section 10, and Section 21.

Requirements:
1. Create training script `backend/app/ml/train.py`:
   - Model 1: Binary Threat Classifier (`RandomForestClassifier(n_estimators=100, max_depth=15, random_state=42)`):
     - Predicts: `Normal` (0) vs `Attack` (1).
   - Model 2: Multi-Class Attack Classifier (`RandomForestClassifier(n_estimators=120, max_depth=20, random_state=42)`):
     - Predicts supported attack classes: `Normal`, `Brute Force`, `DoS`, `Port Scan`, `Web Attack`, `Exploitation`.
2. Implement robust evaluation pipeline in `backend/app/ml/evaluate.py`:
   - Train/Test split (80/20) with stratification.
   - Compute metrics: Accuracy, Precision, Recall, F1 Score (macro and weighted), Confusion Matrix, and False Positive Rate (FPR).
   - Generate evaluation report saved to `models_store/evaluation_report.json`.
3. Save trained model artifacts using `joblib`:
   - `models_store/binary_rf_model.joblib`
   - `models_store/multiclass_rf_model.joblib`
   - `models_store/metadata.json` containing training timestamp, dataset provenance, feature list, and classification metrics.
4. Distinguish clearly in metadata between simulated training vs full benchmark training.
```

---

### Prompt 3.3: Inference Engine API & Threat Analysis Testbench

```text
Act as a Senior ML Systems Engineer and Full-Stack Developer.
Integrate the trained ML models into Sentriq's API and create an interactive threat analysis workbench for SOC analysts (PRD FR-03, FR-04, and Section 27 Step 3-4).

Requirements:
1. Build ML Inference Service in `backend/app/ml/inference.py`:
   - Singleton model loader with thread-safe prediction caching.
   - Methods:
     - `predict_event(features: dict) -> MLPredictionResult`:
       - Returns: binary prediction (`is_threat`), threat probability (0.0 to 1.0), predicted attack category, multiclass confidence distribution across all categories, model version, and rule-assisted primary detection reasons (e.g. "Elevated destination port scan frequency exceeding threshold").
2. Expose API Endpoints in `backend/app/api/v1/ml.py`:
   - `POST /api/v1/ml/predict`: accepts a raw event payload and returns prediction with probabilities.
   - `POST /api/v1/ml/analyze-event/{event_id}`: pulls an existing event from PostgreSQL, runs inference, stores prediction, and returns analysis.
   - `GET /api/v1/ml/model-info`: returns model versions, loaded features, and training evaluation metrics.
3. Build Frontend Threat Analysis Workbench (`frontend/src/pages/ThreatAnalysis.tsx`):
   - Interactive Event Selector / JSON testbench to select a recent event or input custom network features.
   - "Run AI Threat Detection" action button with loading state.
   - Detection Result Panel:
     - Threat Verdict pill (`MALICIOUS` / `BENIGN`) with confidence gauge.
     - Predicted Attack Category badge (e.g., `Brute Force` - 94.2% confidence).
     - Multi-class probability distribution bar chart.
     - Explainable Detection Reason box (identifying anomalous traffic signals).
```

---

## Phase 4: Transparent Risk Scoring & Event Correlation Engine

### Prompt 4.1: Deterministic Weighted Risk Scoring Engine

```text
Act as a Principal Cyber Risk Engineer.
Implement the transparent risk scoring algorithm defined in PRD Section 13 and FR-05. Risk scores must be deterministic, transparent, and accompanied by factor contributions rather than an opaque hallucinated number.

Requirements:
1. Implement the Risk Engine in `backend/app/services/risk_engine.py`:
   - Risk Formula (0 to 100):
     `Total Risk = (Severity * 0.30) + (ML_Confidence * 0.30) + (Asset_Importance * 0.20) + (Attack_Impact * 0.20)`
   - Factor definitions:
     - `Severity Score`: Low = 20, Medium = 50, High = 75, Critical = 100.
     - `ML Confidence Score`: Model confidence percentage (0 to 100).
     - `Asset Importance`: Configurable asset registry lookup (e.g., Database Server / Domain Controller = 90-100, Web Server = 70, Internal Workstation = 40, Guest Network = 20; default = 50).
     - `Attack Impact`: Brute Force = 65, DoS = 80, Port Scan = 40, Web Attack = 75, Exploitation = 95, Normal = 0.
   - Risk Level Mapping (PRD 13.4):
     - 0–29: `Low` (Muted Green)
     - 30–59: `Medium` (Warm Amber)
     - 60–79: `High` (Burnt Orange)
     - 80–100: `Critical` (Deep Red)
   - Narrative Explanation Generator:
     - Returns clear factor breakdown showing exactly how much each parameter contributed to the final score (e.g., "Risk score 84/100 (Critical): Driven by Critical event severity (+30.0), 96% ML attack confidence (+28.8), Domain Controller asset criticality (+18.0), and Exploitation category impact (+19.0)").
2. Write comprehensive unit tests in `backend/tests/test_risk_engine.py` validating edge cases and score boundaries.
```

---

### Prompt 4.2: Time-Window Event Correlation Engine

```text
Act as a Senior SIEM & Detection Engineer.
Implement the Event Correlation Engine specified in PRD Section 14 and FR-06. The correlation engine turns disconnected security events into unified security incidents.

Requirements:
1. Implement Correlation Service in `backend/app/services/correlation_engine.py`:
   - Configurable sliding time window (default: 15 minutes).
   - Correlation Criteria:
     - Rule 1 (Credential Attack Chain): Multiple failed logins from the same source IP / user within window, followed by successful authentication or privilege escalation -> Create `Account Compromise / Brute Force Incident`.
     - Rule 2 (Reconnaissance to Exploitation): Port scan from an IP followed within the window by HTTP exploit payloads or connection floods -> Create `Targeted Multi-Stage Attack Incident`.
     - Rule 3 (Volumetric Flood): Clustered DoS/DDoS traffic targeting a specific asset IP -> Create `Denial of Service Incident`.
   - Prevent duplicate incidents: check if an active incident already exists for the matching source/target/category within the open window; if so, append new events to the existing incident and recompute risk score.
2. Link correlated `SecurityEvent` records to the parent `Incident` via foreign key `incident_id`.
3. Auto-generate incident title, summary narrative, overall severity, and aggregated risk score based on the highest-severity correlated event.
```

---

### Prompt 4.3: Incident Management Lifecycle & Timeline UI

```text
Act as a Full-Stack Security Engineer.
Implement the complete Incident Management Lifecycle and Interactive Incident Details view (PRD FR-07, Section 15, and Section 27 Step 6-7).

Requirements:
1. Backend Incident APIs in `backend/app/api/v1/incidents.py`:
   - `GET /api/v1/incidents/{id}/timeline`: returns chronologically sorted events attached to the incident with delta timestamps (+0s, +45s, +2m 10s).
   - `PATCH /api/v1/incidents/{id}/status`: validates and updates status (`Open` -> `Investigating` -> `Resolved` -> `Closed`) with audit log of who changed status and when.
   - `POST /api/v1/incidents/{id}/notes`: append analyst investigation notes.
2. Frontend Incident Details Page (`frontend/src/pages/IncidentDetails.tsx`):
   - Header: Incident title, Incident ID (`INC-2026-0042`), status dropdown pill, severity badge, risk gauge.
   - Left Column (Attack Story & Timeline):
     - Interactive vertical timeline showing each correlated event in sequence with icons (Failed Auth, Port Probe, Exploit Attempt, Escalation).
     - Time diff indicators, source/dest IPs, and expandable event payload.
   - Right Column (Risk & Impact Breakdown):
     - Weighted risk breakdown progress bars (Severity, ML Confidence, Asset Importance, Attack Impact).
     - Human-readable risk explanation card.
     - Affected assets and entities card.
   - Bottom Section: Analyst notes editor and response action triggers.
```

---

## Phase 5: Real-Time Stream Simulation & WebSocket Telemetry

### Prompt 5.1: Background Event Streamer & WebSocket Hub

```text
Act as a Senior Distributed Systems Engineer.
Implement near-real-time telemetry and streaming simulation for Sentriq as defined in PRD Phase 5 and FR-01.

Requirements:
1. Create WebSocket Connection Manager in `backend/app/core/websocket_hub.py`:
   - Thread-safe manager tracking active client connections.
   - Broadcast method to publish typed messages: `EVENT_INGESTED`, `DETECTION_ALERT`, `INCIDENT_CREATED`, `INCIDENT_UPDATED`, `METRICS_UPDATE`.
2. Implement WebSocket route in `backend/app/api/v1/ws.py`:
   - Endpoint: `/ws/soc-telemetry`.
   - Supports heartbeat ping/pong and client subscription filtering.
3. Build Background Event Streamer in `backend/app/services/streamer.py`:
   - Async worker using `asyncio` that simulates a live stream of network events into PostgreSQL.
   - Intersperses benign traffic with intermittent attack scenarios.
   - Automatically executes the ML detection, risk assessment, and correlation pipeline for each streamed event.
   - Broadcasts real-time updates over the WebSocket hub.
   - Controllable via REST API: `POST /api/v1/simulation/start`, `POST /api/v1/simulation/stop`, `POST /api/v1/simulation/speed` (1x, 2x, 5x).
```

---

### Prompt 5.2: Live SOC Telemetry Dashboard with Real-Time KPIs & Charts

```text
Act as a Senior Frontend Engineer.
Transform Sentriq's Dashboard into a live, interactive Security Operations Center telemetry hub with real-time WebSocket updates.

Requirements:
1. Build WebSocket Client Hook in `frontend/src/hooks/useSocWebSocket.ts`:
   - Auto-reconnect with exponential backoff.
   - Connection status indicator (Live / Reconnecting / Offline).
   - Event dispatcher updating global or local state without causing full re-renders.
2. Enhance Dashboard components with live telemetry:
   - Live Alert Ticker: animated notification banner at top of dashboard showing incoming alerts as they happen.
   - Dynamic KPI counters: smoothly animating numbers for Processed Events, Active Alerts, and Critical Incidents.
   - Live Threat Trend Chart: Recharts area chart that appends incoming event volume data in 5-second bins.
   - Real-time Incident Feed: new incidents dynamically slide in at the top of the Active Incidents table.
3. Add Simulation Control Bar in dashboard header:
   - Play/Pause toggle, Speed selector (1x, 2x, 5x), and "Inject Scenario" dropdown (Brute Force, DoS Burst, Port Recon) with instant visual feedback.
```

---

## Phase 6: Explainable AI (XAI) & Threat Attribution

### Prompt 6.1: SHAP Model Explainability Engine & Feature Attribution

```text
Act as a Principal AI Research Scientist.
Implement Explainable AI (XAI) for the Sentriq threat detection models using SHAP (SHapley Additive exPlanations) according to PRD FR-08 and Phase 6.

Requirements:
1. Install and configure `shap` in the backend ML environment.
2. Build SHAP Explainer Engine in `backend/app/ml/explainer.py`:
   - Initialize `shap.TreeExplainer` on the trained Random Forest classifier.
   - Precompute and cache background summary distributions for fast real-time inference.
   - Method `explain_event(event_features: dict) -> XAIExplanation`:
     - Computes SHAP values for each feature against the predicted class.
     - Identifies top 5 positive feature contributors (factors driving the prediction toward Attack).
     - Identifies top 3 negative feature contributors (factors supporting Normal traffic).
     - Computes baseline model expected value.
     - Synthesizes human-readable narrative explanation based on top feature attributions (e.g. "`destination_port_count=184` contributed +34% towards Port Scan; `packet_rate=12500` contributed +28%").
3. Create API Endpoint in `backend/app/api/v1/ml.py`:
   - `GET /api/v1/ml/explain/{event_id}`: returns detailed SHAP feature importance vectors, baseline values, and generated narrative.
4. Cache explanations in PostgreSQL or Redis to avoid recalculating SHAP values for identical historical events.
```

---

### Prompt 6.2: Explainability Dashboard UI & Rule-to-XAI Bridge

```text
Act as a Senior UI/UX Data Visualization Engineer.
Build the Explainable AI presentation components within Sentriq's analyst interface (PRD Section 16 & Section 27).

Requirements:
1. Create XAI Visualization component in `frontend/src/components/xai/FeatureAttributionChart.tsx`:
   - Horizontal Diverging Bar Chart (using Recharts or custom SVG):
     - Red/Amber bars pushing right for features increasing threat likelihood.
     - Green/Teal bars pushing left for features indicating normal baseline behavior.
     - Clean typography displaying feature names, actual observed values, and percentage impact.
2. Build Explainability Modal / Drawer in the Security Logs and Threat Analysis views:
   - Header with Model Version, Inference Latency (ms), and Confidence.
   - Natural Language Explanation summary banner ("Why was this detected?").
   - Detailed Feature Breakdown table with columns: Feature Name, Value, Contribution Weight, Baseline Average.
   - Rule comparison note: displays whether the heuristic rule-based check agrees with the ML feature attribution.
```

---

## Phase 7: AI-Assisted SOC Investigation & Multi-Agent Copilot

### Prompt 7.1: Multi-Agent SOC Investigation Orchestrator

```text
Act as a Principal AI Agent Architect.
Implement the AI-Assisted Investigation system specified in PRD Section 1.3, FR-09, and Phase 7. Build a modular multi-agent workflow using LangChain, LlamaIndex, or lightweight native Python agent patterns with support for local LLMs (via Ollama) or cloud providers (OpenAI / Gemini API).

Requirements:
1. Define specialized agent roles in `backend/app/agents/`:
   - `InvestigationAgent`: inspects incident events, extracts IOCs (IPs, domains, hashes, user accounts), queries event logs for historical patterns.
   - `CorrelationAgent`: evaluates whether neighboring alerts belong to the same threat campaign.
   - `ResponseRecommendationAgent`: formulates targeted, human-in-the-loop remediation steps (e.g., host isolation, firewall IP block rule, credential reset).
   - `ReportingAgent`: synthesizes findings into a professional executive incident summary.
2. Implement Agent Orchestrator in `backend/app/agents/orchestrator.py`:
   - Manages state machine: Gather Context -> Analyze Threat -> Propose Response -> Generate Summary.
   - Grounded context injection: enforces strict factuality by providing database events directly in prompts (zero hallucination of IPs or attack vectors).
3. Expose API Endpoints in `backend/app/api/v1/investigation.py`:
   - `POST /api/v1/investigation/analyze/{incident_id}`: runs multi-agent workflow and returns structured investigation dossier.
   - `POST /api/v1/investigation/chat`: analyst interactive chat assistant grounded in current incident data.
```

---

### Prompt 7.2: Human-in-the-Loop Response Actions & Audit Log

```text
Act as a Full-Stack Security Engineer.
Implement the Human-in-the-Loop Response Recommendation and Approval subsystem required by PRD FR-10, Section 4.2, and Section 26. High-impact remediation actions must NEVER execute without explicit analyst approval.

Requirements:
1. Create Response Action schema and database model in `backend/app/models/response_action.py`:
   - `id`: UUID.
   - `incident_id`: FK to `incidents.id`.
   - `action_type`: Enum (`ISOLATE_HOST`, `BLOCK_IP_FIREWALL`, `RESET_CREDENTIALS`, `RATE_LIMIT_ENDPOINT`, `APPLY_WAF_RULE`).
   - `target`: String (e.g., IP address `198.51.100.45`, user `admin`).
   - `reason`: Explanation provided by the AI agent or rule.
   - `status`: Enum (`PENDING_APPROVAL`, `APPROVED`, `REJECTED`, `EXECUTED`, `FAILED`).
   - `approved_by`: String analyst username.
   - `approved_at`: DateTime nullable.
   - `execution_log`: Text audit log.
2. Implement REST endpoints in `backend/app/api/v1/responses.py`:
   - `GET /api/v1/incidents/{id}/responses`: list recommended response actions.
   - `POST /api/v1/responses/{id}/approve`: analyst approves action (triggers simulated remediation sandbox execution).
   - `POST /api/v1/responses/{id}/reject`: analyst rejects action with mandatory comment.
3. Frontend Response Action Card in `frontend/src/pages/IncidentDetails.tsx`:
   - Recommended actions display with clear warning indicators.
   - "Approve & Execute" button (styled in Steel Blue / Green) and "Reject" button (Muted Gray).
   - Confirmation modal emphasizing: "Human Analyst Approval Required. This will simulate containment on target host."
   - Audit trail widget recording analyst decision.
```

---

### Prompt 7.3: Automated Incident Report Generation (PDF/Markdown)

```text
Act as a Senior Full-Stack Engineer.
Implement the automated Incident Report Generation feature specified in PRD Section 24 and FR-11.

Requirements:
1. Implement Report Generation Service in `backend/app/services/report_generator.py`:
   - Compiles complete incident dossier:
     1. Executive Incident Summary
     2. Threat Detection & ML Model Details
     3. Calculated Risk Score & Factor Breakdown
     4. Correlated Event Timeline & Evidence Table
     5. AI Agent Investigation Findings
     6. Recommended & Approved Response Actions
     7. Current Status and Audit Sign-off
   - Generates both clean Markdown (`.md`) and styled PDF export (using `reportlab` or HTML-to-PDF template with Sentriq branding).
2. Create API Endpoints in `backend/app/api/v1/reports.py`:
   - `GET /api/v1/reports/{incident_id}/markdown`: returns markdown text.
   - `GET /api/v1/reports/{incident_id}/download-pdf`: returns downloadable PDF file.
3. Add "Export Incident Report" dropdown in the frontend Incident view with preview modal and one-click PDF download.
```

---

## Phase 8: Comprehensive Evaluation, Docker Packaging & Faculty Demo

### Prompt 8.1: Full Benchmark Evaluation & Performance Metrics

```text
Act as an Academic Research Lead & ML Evaluation Specialist.
Implement the full evaluation framework specified in PRD Section 21 and Section 23 to generate academic-grade Major Project evaluation metrics.

Requirements:
1. Build Evaluation Script `backend/scripts/evaluate_benchmarks.py`:
   - Evaluates performance across UNSW-NB15 / CIC-IDS2017 test splits.
   - Calculates exact quantitative metrics:
     - Accuracy, Precision, Recall, Macro F1, Weighted F1.
     - Per-class detection metrics (Brute Force, DoS, Port Scan, Web Attack, Exploitation, Normal).
     - False Positive Rate (FPR) and False Discovery Rate (FDR).
     - Inference Latency per event (mean, p95, p99 in milliseconds).
     - Event Correlation alert reduction percentage (raw alerts vs created incidents).
2. Save output as structured JSON and Markdown report in `docs/EVALUATION_RESULTS.md`.
3. Generate high-resolution confusion matrix heatmaps and ROC/AUC curves saved to `docs/figures/` for academic report and presentation slides.
```

---

### Prompt 8.2: Complete Docker Desktop Multi-Container Compose

```text
Act as a Senior DevOps & Release Engineer.
Containerize the entire Sentriq platform for unified deployment on Docker Desktop using Docker Compose, adhering to PRD Phase 8.

Requirements:
1. Create `backend/Dockerfile`:
   - Multi-stage build using `python:3.11-slim`.
   - Install dependencies, copy source, download/verify ML models.
   - Entrypoint running `uvicorn app.main:app --host 0.0.0.0 --port 8000`.
2. Create `frontend/Dockerfile`:
   - Multi-stage build: Node.js 20 build stage (`npm run build`), Nginx alpine production stage serving static files with proxy pass to backend `/api/`.
3. Update root `docker-compose.yml` orchestrating all services:
   - `db`: PostgreSQL 16 on Docker Desktop with healthchecks and persistent volume.
   - `backend`: depends on `db` being healthy, exposes port `8000`.
   - `frontend`: depends on `backend`, exposes port `3000` (or `80`).
   - `pgadmin` (optional dev profile): port `5050`.
4. Include startup script `start.ps1` (PowerShell for Windows) that verifies Docker Desktop is running, starts the containers, runs migrations, seeds initial demonstration data, and opens the browser.
```

---

### Prompt 8.3: End-to-End Demonstration Script & Seed Scenarios

```text
Act as a Solutions Architect and Project Demo Specialist.
Create an end-to-end automated demonstration workflow and walkthrough guide tailored for the Academic Faculty Review based on PRD Section 27.

Requirements:
1. Implement seed scenario script `backend/scripts/demo_orchestrator.py`:
   - Scenario: PRD Section 12 Brute Force Account Compromise.
   - Plays out in real-time or fast-forward:
     1. Ingests benign baseline traffic.
     2. Injects 10 failed SSH/auth attempts from an external attacker IP.
     3. Triggers ML threat detection (flags Brute Force with high confidence).
     4. Triggers Risk Engine (calculates 85/100 Critical Risk).
     5. Triggers Event Correlation (creates single unified incident `INC-BRUTEFORCE-01`).
     6. Injects successful attacker login -> updates incident timeline.
     7. AI Agent proposes account lockout and IP block.
2. Create `DEMO_GUIDE.md`:
   - Step-by-step faculty presentation script following PRD Section 27 (Dashboard -> Logs -> ML Analysis -> Risk -> Incident Timeline -> AI Copilot -> Approved Response -> Report Export).
   - Expected talking points, metrics to highlight, and architectural defensibility tips.
```

