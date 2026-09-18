# Sentriq AI-SOC: End-to-End Step-by-Step User Journey & Technical Process Guide

This document provides a complete, step-by-step walkthrough of how a user interacts with the **Sentriq Autonomous AI-SOC** platform, what happens behind the scenes at every step (Frontend, FastAPI, PostgreSQL, Machine Learning, SHAP, and Multi-Agent layers), what output is generated, and how all components connect together.

---

## Architecture Quick Reference

```
  ┌─────────────────┐       HTTP / REST        ┌──────────────────┐       Async SQL       ┌────────────────────────┐
  │  React 18 UI    │ ───────────────────────> │  FastAPI Backend │ ────────────────────> │  PostgreSQL 16 DB      │
  │  (Port 5173)    │ <─────────────────────── │  (Port 8000)     │ <──────────────────── │  (Docker Port 5432)    │
  └─────────────────┘      WebSocket Stream    └──────────────────┘                       └────────────────────────┘
          ▲                   (/ws/soc-telemetry)        │
          │                                              ▼
          │                                    ┌──────────────────┐
          └─────────────────────────────────── │ ML & XAI Engine  │
                  Predictions & SHAP           │ (Random Forest & │
                                               │  TreeExplainer)  │
                                               └──────────────────┘
```

---

# Phase-by-Phase User Journey

---

## Step 1: Starting the Platform

### 1.1 What the User Does
The user starts the three core services:
1. Ensure **Docker Desktop** is running.
2. The PostgreSQL database container starts via `docker compose up -d db`.
3. The FastAPI backend starts in Python virtual environment:
   ```powershell
   .venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
4. The React Vite frontend starts:
   ```powershell
   npm run dev -- --host 127.0.0.1 --port 5173
   ```
*(Alternatively, running `.\start.ps1` automates all of the above).*

### 1.2 What Happens Under the Hood
- **Database Initialization**: PostgreSQL 16 container `sentriq-postgres` starts on port 5432. The database `sentriq_soc` is created with user `sentriq_admin`.
- **Backend Startup**: FastAPI initializes an async database connection pool via SQLAlchemy 2.0 (`asyncpg`). It registers all REST routes (`/api/v1/events`, `/api/v1/incidents`, `/api/v1/ml`, `/api/v1/investigation`) and creates the WebSocket broadcast hub at `/ws/soc-telemetry`.
- **ML Artifact Loading**: The backend verifies the serialized Random Forest models (`binary_rf_model.joblib`, `multiclass_rf_model.joblib`) and preprocessor (`preprocessor.joblib`) in `models_store/`.
- **Frontend Startup**: Vite compiles TypeScript and serves the React application at `http://127.0.0.1:5173`.

### 1.3 What the User Sees
- Terminal shows:
  ```
  [INFO] Application startup complete. Uvicorn running on http://127.0.0.1:8000
  VITE v5.4.21 ready in 382 ms. Local: http://127.0.0.1:5173/
  ```

---

## Step 2: Landing on the Centralized SOC Dashboard

### 2.1 What the User Does
The user opens a web browser and navigates to `http://localhost:5173`.

### 2.2 What Happens Under the Hood
1. The frontend `Navbar` component sends a background ping to `GET /api/v1/health`.
2. The backend responds:
   ```json
   {
     "status": "healthy",
     "project": "Sentriq",
     "version": "1.0.0",
     "database": "connected",
     "database_engine": "PostgreSQL 16 (Docker Desktop)"
   }
   ```
3. The `Dashboard.tsx` page executes two parallel API calls:
   - `GET /api/v1/incidents/summary` (retrieves active incident counts, critical/high breakdowns, recent incidents).
   - `GET /api/v1/events/stats` (retrieves total processed events, threat vs benign counts, attack distributions).

### 2.3 What the User Sees on the Screen
- **Top Navigation Bar**:
  - Live UTC Telemetry Clock ticking in real time.
  - Green status badge: `● Docker PostgreSQL 16 Connected`.
  - Blue button: **"Faculty Demo Mode"**.
- **Top KPI Cards**:
  - **Total Events Processed**: Cumulative security records in the database.
  - **Active Incidents**: Total security incidents awaiting resolution.
  - **Critical Incidents**: High-priority incidents with risk score $\ge 80$.
  - **High-Risk Incidents**: Incidents with risk score between $60$ and $79$.
- **Interactive Charts**:
  - **24-Hour Threat Trend**: Dynamic Recharts area chart showing hourly threat volume.
  - **Attack Category Distribution**: Horizontal bar chart showing counts for *DoS, Brute Force, Port Scan, Web Attack, Exploitation, and Normal*.
- **Recent Incidents Table**:
  - Displays recent incident IDs (e.g. `INC-2026-0059`), severity badges (*Critical, High, Medium, Low*), status (*Open, Investigating*), attack category, and relative timestamps.
  - Clicking any incident row redirects directly to its detailed investigation page (`/incidents/:id`).

---

## Step 3: Security Logs Explorer & Ingesting Datasets

### 3.1 What the User Does
The user clicks on **"Security Logs"** in the left sidebar navigation (`/logs`).

### 3.2 What the User Sees Initially
- A search and filter bar (filter by severity, attack category, data source, or free text).
- Telemetry stats banner: Total Processed Events, Threat Detections, Benign Network Flows, and Benchmark Flow Records.
- An action bar with dedicated buttons:
  - **Load UNSW-NB15**
  - **Load CIC-IDS2017**
  - **Upload Dataset CSV** (green button with upload icon)
  - Scenario simulation buttons (*Brute Force, DoS Burst, Port Recon, Benign*).
- A paginated table of security events displaying: Timestamp, Source, Event Type, Source IP $\rightarrow$ Destination IP, Protocol, Attack Type, Severity, and Verification Label.

---

## Step 4: Loading or Uploading Datasets Live

Here the user has three options to bring data into the system:

### Option A: One-Click Loading of UNSW-NB15 Benchmark
1. **User Action**: The user clicks the blue button **"Load UNSW-NB15"**.
2. **System Processing**:
   - Frontend sends `POST /api/v1/events/ingest-benchmark?dataset=unsw`.
   - Backend service `BenchmarkLoader.load_unsw_sample()` opens `data/benchmark/unsw_nb15_sample.csv`.
   - It parses authentic flow records with features: `dur, proto, service, spkts, dpkts, sbytes, dbytes, rate, sttl, dttl, sload, dload, ct_*`.
   - Each row is normalized into a `SecurityEvent` ORM object with `is_simulated = False` and `source = "unsw_nb15_network_tap"`.
   - All rows are written to PostgreSQL via an async transaction.
3. **UI Result**:
   - A blue toast banner appears: `Ingested 20 authentic records from UNSW-NB15 benchmark dataset.`
   - The table refreshes with UNSW-NB15 flow records marked with low/high severities.

### Option B: One-Click Loading of CIC-IDS2017 Benchmark
1. **User Action**: The user clicks the indigo button **"Load CIC-IDS2017"**.
2. **System Processing**:
   - Frontend sends `POST /api/v1/events/ingest-benchmark?dataset=cic`.
   - Backend service `BenchmarkLoader.load_cic_sample()` reads `data/benchmark/cic_ids2017_sample.csv`.
   - It parses bidirectional flow records: `Flow Duration, Protocol, Total Fwd/Bwd Packets, Flow Bytes/s, Flow Packets/s, Destination Port, Label`.
   - It normalizes labels (*DoS Hulk, DDoS, PortScan, Web Attack, Infiltration, BENIGN*) into unified attack types.
   - Each record is saved into PostgreSQL with `is_simulated = False` and `source = "cic_ids2017_network_tap"`.
3. **UI Result**:
   - A toast banner appears: `Ingested 20 authentic records from CIC-IDS2017 benchmark dataset.`
   - The **Benchmark Flow Records** card updates to show: `(UNSW: 20 | CIC: 20)`.

### Option C: Manual Upload of a Custom Dataset CSV (Live Demo)
1. **User Action**: The user clicks the green button **"Upload Dataset CSV"**.
2. A Windows file picker dialog opens. The user selects any `.csv` file from their computer and clicks **Open**.
3. **System Processing**:
   - Frontend sends a multipart form-data request to `POST /api/v1/events/upload-csv`.
   - Backend parses the CSV headers dynamically:
     - If it detects headers like `attack_cat` or `dur` $\rightarrow$ it recognizes **UNSW-NB15 format**.
     - If it detects headers like `Flow Duration` or `Total Fwd Packets` $\rightarrow$ it recognizes **CIC-IDS2017 format**.
     - If it detects generic log headers (`source_ip`, `event_type`) $\rightarrow$ it recognizes **Custom Log format**.
   - It extracts the features, validates numerical columns, and saves the rows to PostgreSQL.
4. **UI Result**:
   - A green toast banner appears:
     ```
     Successfully ingested 20 records in CIC-IDS2017 format.
     ```
   - The table instantly refreshes with the uploaded records.

---

## Step 5: Inspecting Raw Features & Explaining with SHAP

### 5.1 What the User Does
The user clicks on any row in the Security Logs table (for example, a `DoS Hulk` or `Brute Force` event).

### 5.2 What Happens Under the Hood
1. A slide-over drawer opens from the right side of the screen (`SecurityLogs.tsx` drawer).
2. The drawer displays:
   - **Event Metadata**: Event ID, Timestamp, Source IP, Destination IP, Protocol, Port, Severity badge.
   - **Raw Feature Vector (JSON)**: The complete feature dictionary extracted from the CSV:
     ```json
     {
       "dur": 0.85,
       "spkts": 75,
       "dpkts": 90,
       "sbytes": 42000,
       "dbytes": 120000,
       "rate": 194.11,
       "sttl": 62,
       "dttl": 252,
       "proto": "TCP",
       "service": "http"
     }
     ```
   - A "Copy JSON" button to copy the feature payload to the clipboard.

### 5.3 Triggering Explainable AI (SHAP)
1. Inside the drawer, the user clicks **"Explain with SHAP"**.
2. An explainability modal opens (`ExplainabilityDrawer.tsx`).
3. Frontend sends `GET /api/v1/ml/explain/{event_id}`.
4. Backend `XAIExplainerService` passes the event's features into `shap.TreeExplainer(multiclass_rf_model)`.
5. It computes exact Shapley values:
   - Base Expected Value: $E[f(x)] = 0.65$
   - Feature Attributions:
     - `sbytes` ($+0.24$ push towards DoS)
     - `rate` ($+0.19$ push towards DoS)
     - `proto=TCP` ($+0.05$ push towards DoS)
     - `dur` ($-0.08$ push away from DoS)
6. A **Rule-to-XAI Consensus Check** verifies whether the statistical SHAP attribution agrees with deterministic rule logic (verdict: `Consensual`).
7. **UI Result**: The user sees a **Diverging Horizontal Bar Chart** (Recharts) showing green bars for negative contributions and red bars for positive risk drivers.

---

## Step 6: Machine Learning Threat Analysis Testbench

### 6.1 What the User Does
The user clicks on **"Threat Analysis"** in the left sidebar (`/analysis`).

### 6.2 What Happens Under the Hood
1. Frontend calls `GET /api/v1/ml/model-info`:
   - Returns: Active model architecture (`RandomForestClassifier`), versions, training date, binary accuracy (**96.67%**), multi-class accuracy (**96.67%**), and supported classes.
2. The user has two options to test inference:
   - **Option 1**: Select an existing event from the database dropdown.
   - **Option 2**: Click a quick preset button (*"Brute Force Preset"*, *"DoS Burst Preset"*, *"Port Recon Preset"*, or *"Benign Traffic Preset"*). The 14 numerical input fields populate automatically.
3. The user clicks **"Run Threat Inference"**.
4. Frontend sends `POST /api/v1/ml/predict` with the feature vector.
5. Backend `ThreatInferenceService`:
   - Preprocesses features using `preprocessor.transform()`.
   - Runs `binary_rf_model.predict_proba()` $\rightarrow$ calculates `P(attack) = 87.2%`.
   - Runs `multiclass_rf_model.predict_proba()` $\rightarrow$ calculates probabilities across all 6 classes:
     - `Normal`: 2.1%
     - `Brute Force`: 87.2%
     - `DoS`: 4.3%
     - `Port Scan`: 3.8%
     - `Web Attack`: 1.6%
     - `Exploitation`: 1.0%
   - Generates natural language heuristic reasoning explaining the verdict.

### 6.3 What the User Sees on Screen
- **Threat Verdict Card**: Displays a large badge: `MALICIOUS` (Confidence: 87.2%), Predicted Category: `Brute Force`.
- **Probability Distribution Bar Chart**: Recharts bar graph displaying probability percentages across all 6 attack categories.
- **Explainable Evidence Box**: Synthesizes bullet points:
  - *"High connection concentration to authentication port (22/SSH)."*
  - *"Packet size distribution matches repetitive credential transmission."*

---

## Step 7: Incident Timeline & Transparent 4-Factor Risk Scoring

### 7.1 What the User Does
The user navigates to **"Incidents"** (`/incidents`) and clicks on an incident (e.g. `INC-2026-0059`).

### 7.2 What Happens Under the Hood
1. When security events enter the system, the **15-Minute Sliding-Window Correlation Engine** (`correlation_engine.py`) automatically groups unassigned events that:
   - Originate from the same Attacker Source IP.
   - Target the same Destination Asset / Service.
   - Occur within a 15-minute sliding temporal window.
   - Match sequential attack stages (e.g. Recon $\rightarrow$ Brute Force $\rightarrow$ Privilege Escalation).
2. The engine condenses multiple raw alerts into a single unified incident (achieving **93.3% alert noise reduction**).
3. The **Risk Engine** (`risk_engine.py`) calculates the incident's risk score using the deterministic 4-factor formula:
   $$\text{Total Risk} = (\text{Severity} \times 0.3) + (\text{ML Confidence} \times 0.3) + (\text{Asset Criticality} \times 0.2) + (\text{Attack Impact} \times 0.2)$$
   - Example calculation for `INC-2026-0059`:
     - Severity: High ($75 \times 0.3 = 22.5$)
     - ML Confidence: 87% ($87 \times 0.3 = 26.1$)
     - Asset Criticality: Critical Auth Server ($100 \times 0.2 = 20.0$)
     - Attack Impact: Privilege Escalation ($100 \times 0.2 = 20.0$)
     - **Total Risk Score**: $22.5 + 26.1 + 20.0 + 20.0 = \mathbf{88.6 / 100}$ $\rightarrow$ **CRITICAL LEVEL**.

### 7.3 What the User Sees on Screen (`IncidentDetails.tsx`)
- **Top Header**: Incident Code, Title, Current Status (`Investigating`), Severity badge (`Critical`), and Asset affected (`auth-service`).
- **Transparent Risk Breakdown Card**:
  - A circular percentage score ring displaying `89/100`.
  - Four progress bars displaying the exact contribution of each factor:
    - *Peak Event Severity (30% weight)*: 75/100
    - *ML Model Confidence (30% weight)*: 87/100
    - *Asset Criticality (20% weight)*: 100/100
    - *Attack Impact (20% weight)*: 100/100
  - Natural Language Factor Attribution Narrative explaining how the risk score was calculated.
- **Correlated Attack Timeline**:
  - A vertical chronological timeline showing every correlated event in order:
    - Stage 1 ($T+0\text{s}$): Port Recon Scan against port 22.
    - Stage 2 ($T+15\text{s}$): Repeated SSH authentication failures for user `admin`.
    - Stage 3 ($T+45\text{s}$): Suspicious authentication success from external IP `198.51.100.45`.
    - Stage 4 ($T+120\text{s}$): Privilege escalation command executed (`sudo -i`).

---

## Step 8: Multi-Agent AI Investigation & Grounded Copilot

### 8.1 What the User Does
On the same Incident Details page, the user scrolls down to the **Multi-Agent Dossier** or clicks **"Open AI SOC Copilot"** in the top action bar.

### 8.2 What Happens Under the Hood
1. When the page loads, frontend calls `POST /api/v1/investigation/analyze/{incident_id}`.
2. The backend **`MultiAgentOrchestrator`** triggers 4 specialized AI agents:
   - **Agent 1: Investigation Agent**: Performs root-cause analysis, identifies the entry vector (`Remote SSH Credential Brute-Force`), maps MITRE ATT&CK techniques (`T1110 - Brute Force`, `T1078 - Valid Accounts`, `T1548 - Abuse Elevation Control`), and determines the blast radius (`High - Direct root shell access`).
   - **Agent 2: Correlation Agent**: Synthesizes the chronological attack progression and confirms kill-chain phase alignment.
   - **Agent 3: Response Agent**: Generates actionable containment recommendations:
     1. *Network Perimeter*: Block external IP `198.51.100.45` on edge firewall (`iptables -A INPUT -s 198.51.100.45 -j DROP`).
     2. *Identity & Access*: Temporarily lock account `admin` and revoke active SSH sessions.
     3. *Host Quarantine*: Terminate unauthorized terminal PID `4821`.
     - **PRD FR-10 Safety Guardrail**: All containment actions are inserted into PostgreSQL with status `Pending Review`. **No destructive action is executed automatically.**
   - **Agent 4: Reporting Agent**: Compiles an executive Markdown incident report.
3. The user opens the **Grounded Copilot Drawer** and asks:
   *"What was the attacker's initial access method?"*
4. Backend `InvestigationAgent.answer_copilot_query()` executes a grounded database query:
   - It searches only verified PostgreSQL event records for that incident.
   - It answers with zero hallucination, citing the exact database event IDs and timestamps.

### 8.3 What the User Sees on Screen
- **Multi-Agent Dossier Card** (`MultiAgentDossierCard.tsx`):
  - Agent status indicators showing all 4 agents active.
  - Entry vector summary banner.
  - MITRE ATT&CK badges with technique codes.
  - Interactive Indicators of Compromise (IOC) table (IP addresses, usernames, ports) with copy buttons.
- **AI Copilot Drawer** (`GroundedCopilotDrawer.tsx`):
  - Quick query chips (*"Explain Attack Narrative"*, *"What is the Blast Radius?"*, *"List Recommended Actions"*).
  - Grounded answers with an expandable **"Grounded Database Facts"** accordion showing the exact PostgreSQL rows cited.

---

## Step 9: Human-in-the-Loop (HITL) Containment Response

### 9.1 What the User Does
The user looks at the **Containment Actions Card** (`ContainmentActionsCard.tsx`) on the Incident Details page.

### 9.2 What the User Sees Initially
- A list of proposed response actions, each displaying:
  - A pulsating amber badge: `Pending Review`.
  - Risk Level badge (`Critical` or `High`).
  - The exact shell/firewall command (e.g. `iptables -A INPUT -s 198.51.100.45 -j DROP`).
  - An input box for analyst justification notes.
  - Two buttons: **"Approve & Apply"** (green) and **"Reject"** (red).

### 9.3 What Happens When User Clicks "Approve & Apply"
1. User clicks **"Approve & Apply"**.
2. Frontend calls `POST /api/v1/investigation/actions/{action_id}/review`:
   ```json
   {
     "status": "Approved",
     "analyst_notes": "Confirmed malicious brute force from external IP."
   }
   ```
3. Backend updates the database record:
   - Status changes from `Pending Review` to `Approved`.
   - Sets `executed = True`.
   - Records reviewer name, timestamp, and analyst justification notes in the immutable audit log.
4. **UI Result**:
   - The badge flips to a solid green badge: `Approved (Executed)`.
   - An audit trail record appears below the action showing who approved it and when.
   - A success notification confirms the containment rule has been recorded.

---

## Step 10: Executive Incident Report Export

### 10.1 What the User Does
The user clicks the **"Executive Report"** button at the top of the Incident Details page.

### 10.2 What Happens Under the Hood
1. Frontend calls `GET /api/v1/investigation/report/{incident_id}`.
2. Backend `ReportingAgent` generates a formal academic/executive incident report in GitHub-flavored Markdown.
3. The report compiles:
   - Executive Incident Summary
   - Incident Metadata & Classification
   - Deterministic 4-Factor Risk Breakdown
   - MITRE ATT&CK Matrix Mapping
   - Chronological Attack Timeline
   - Verified Indicators of Compromise (IOCs)
   - Containment & Remediation Audit Log (with analyst approvals)
4. A preview modal opens (`ExecutiveReportModal.tsx`) showing formatted Markdown with syntax highlighting.
5. The user clicks **"Download .md"** or **"Copy Markdown"** to save the report to their local machine.

---

## Step 11: Real-Time Stream Simulation & WebSocket Hub

### 11.1 What the User Does
The user visits the Dashboard or Logs page and notices the **Live Control Bar** at the bottom of the screen (`LiveControlBar.tsx`).

### 11.2 What Happens Under the Hood
1. When the browser opens, a bidirectional WebSocket connection is established with `ws://localhost:8000/ws/soc-telemetry`.
2. The user can interact with the controls:
   - **Play / Pause**: Starts or pauses the background event streamer.
   - **Speed Multiplier**: Selects $1\times$ (normal speed), $2\times$, or $5\times$ (fast-forward).
   - **Quick Inject Scenarios**: Dropdown to inject an immediate burst of Brute Force, DoS, or Port Scan events.
3. As events stream from the background worker:
   - They pass through the ML preprocessor and Random Forest classifier in flight.
   - The backend broadcasts the evaluated event payload over the WebSocket.
4. **UI Result**:
   - The **Live Marquee Alert Ticker** scrolls across the screen showing the latest threat alert.
   - The 24-hour threat trend area chart updates dynamically without refreshing the web page.

---

## Step 12: Faculty Demo Mode (One-Click Defense Scenario)

### 12.1 What the User Does
During a presentation to faculty or evaluators, the user clicks the blue **"Faculty Demo Mode"** button in the top navigation bar.

### 12.2 What Happens Under the Hood
1. An interactive modal opens (`FacultyDemoModal.tsx`).
2. The modal provides:
   - **One-Click Attack Injection**:
     - *Inject PRD Sec 12 Brute Force Scenario*
     - *Inject Volumetric DoS Flood*
     - *Inject Port Reconnaissance*
   - **Interactive Guided Tour Tabs**: 8 tabs explaining every architectural module (*Foundation, Ingestion, ML Detection, Risk Scoring, WebSockets, XAI/SHAP, Multi-Agent HITL, Benchmark Evaluation*).
3. When the user clicks **"Inject Brute Force Scenario"**:
   - The backend ingests the 5 sequential stages of the PRD Section 12 attack.
   - The ML model classifies the threat.
   - The correlation engine creates incident `INC-2026-0059`.
   - The modal provides a direct link: *"View Created Incident INC-2026-0059"*.
4. The user clicks the link and walks the review committee through the complete attack story in under 3 minutes.

---

# Summary of Files and Where Logic Lives

| Layer | Key File | Responsibility |
| :--- | :--- | :--- |
| **Database Models** | [`backend/app/models/`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/models/) | `SecurityEvent`, `Incident`, `ResponseAction` tables |
| **Data Ingestion** | [`benchmark_loader.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/services/benchmark_loader.py) | Ingests UNSW-NB15, CIC-IDS2017, and custom CSV uploads |
| **Synthetic Scenarios** | [`data_generator.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/services/data_generator.py) | Generates benign traffic & PRD Section 12 attack sequences |
| **ML Preprocessing** | [`preprocessing.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/ml/preprocessing.py) | `ColumnTransformer` (14 numerical + 3 categorical features) |
| **ML Inference** | [`inference.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/ml/inference.py) | Binary & Multi-Class Random Forest threat prediction |
| **Explainable AI** | [`xai_service.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/services/xai_service.py) | SHAP TreeExplainer & Rule-to-XAI consensus check |
| **Risk Scoring** | [`risk_engine.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/services/risk_engine.py) | Deterministic 4-Factor mathematical scoring formula |
| **Event Correlation** | [`correlation_engine.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/services/correlation_engine.py) | 15-minute sliding-window temporal incident correlation |
| **Multi-Agent AI** | [`backend/app/agents/`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/agents/) | Investigation, Correlation, Response, and Reporting Agents |
| **WebSockets** | [`websocket_hub.py`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/services/websocket_hub.py) | Real-time telemetry broadcasting hub |
| **REST APIs** | [`backend/app/api/v1/`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/backend/app/api/v1/) | Endpoints for events, incidents, ML, and investigation |
| **Frontend UI** | [`frontend/src/pages/`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/frontend/src/pages/) | Dashboard, SecurityLogs, ThreatAnalysis, Incidents |

