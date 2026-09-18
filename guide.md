# Sentriq AI-SOC: Official User Manual & Operations Guide

---

## Document Information
- **Product Name**: Sentriq Autonomous AI Security Operations Center (AI-SOC)
- **Version**: 1.0.0 Enterprise Release
- **Target Audience**: Security Analysts, SOC Engineers, System Administrators, and Technical Evaluators
- **Document Type**: Comprehensive Software User Manual

---

# Table of Contents
1. [System Overview & Architecture](#1-system-overview--architecture)
2. [Prerequisites & System Startup](#2-prerequisites--system-startup)
3. [User Access & Identity Model](#3-user-access--identity-model)
4. [User Interface Navigation & Global Layout](#4-user-interface-navigation--global-layout)
5. [Module 1: SOC Dashboard (`/`)](#5-module-1-soc-dashboard-)
6. [Module 2: Security Logs Explorer (`/logs`)](#6-module-2-security-logs-explorer-logs)
7. [Module 3: Benchmark & Custom Dataset Ingestion](#7-module-3-benchmark--custom-dataset-ingestion)
8. [Module 4: Machine Learning Threat Analysis (`/analysis`)](#8-module-4-machine-learning-threat-analysis-analysis)
9. [Module 5: Explainable AI & SHAP Attribution](#9-module-5-explainable-ai--shap-attribution)
10. [Module 6: Incident Management & Attack Timelines (`/incidents`)](#10-module-6-incident-management--attack-timelines-incidents)
11. [Module 7: Deterministic 4-Factor Risk Engine](#11-module-7-deterministic-4-factor-risk-engine)
12. [Module 8: Multi-Agent AI Investigation & Grounded Copilot](#12-module-8-multi-agent-ai-investigation--grounded-copilot)
13. [Module 9: Human-in-the-Loop (HITL) Containment](#13-module-9-human-in-the-loop-hitl-containment)
14. [Module 10: Executive Incident Report Generation](#14-module-10-executive-incident-report-generation)
15. [Module 11: Real-Time Stream Simulation & WebSocket Hub](#15-module-11-real-time-stream-simulation--websocket-hub)
16. [System Verification & Troubleshooting](#16-system-verification--troubleshooting)

---

# 1. System Overview & Architecture

**Sentriq** is an intelligent security operations platform designed to ingest high-volume network security logs, detect intrusions with trained machine learning classifiers, explain detection rationale mathematically, correlate isolated events into chronological attack stories, assess risk transparently, and generate human-approved containment workflows.

### System Architecture Diagram
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   PRESENTATION TIER                                    │
│  React 18 + TypeScript + Vite + Tailwind CSS + Recharts (Port 5173 / Port 80 in Docker)│
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ HTTP REST / WebSocket Hub
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    APPLICATION TIER                                    │
│  FastAPI Backend (Python 3.11+) + Uvicorn Async Server (Port 8000)                     │
│  ├── Ingestion & Normalization Layer (UNSW-NB15 & CIC-IDS2017 Parsers)                 │
│  ├── ML Inference Engine (Random Forest Binary & Multi-Class Classifiers)              │
│  ├── Explainable AI (SHAP TreeExplainer & Rule-to-XAI Consensus Bridge)                 │
│  ├── Deterministic 4-Factor Risk Engine (Severity, Confidence, Asset, Impact)          │
│  ├── 15-Minute Sliding-Window Temporal Correlation Engine                              │
│  ├── Multi-Agent Orchestrator (Investigation, Correlation, Response, Reporting Agents) │
│  └── Telemetry Streamer & WebSocket Hub (`/ws/soc-telemetry`)                          │
└───────────────────────────────────────────┬────────────────────────────────────────────┘
                                            │ Asyncpg Connection Pool (SQLAlchemy 2.0)
                                            ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                      DATA TIER                                         │
│  PostgreSQL 16 Alpine in Docker Desktop Container `sentriq-postgres` (Port 5432)       │
│  ├── security_events (Normalized Flow Telemetry & Raw Feature JSON)                    │
│  ├── incidents (Correlated Incidents & Risk Breakdowns)                                │
│  └── response_actions (Containment Proposals & Audit Trail)                            │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

# 2. Prerequisites & System Startup

### 2.1 Prerequisites
- **Operating System**: Windows 10/11, macOS, or Linux
- **Docker Desktop**: Installed and running (for PostgreSQL 16)
- **Node.js**: Version 18.x or 20.x
- **Python**: Version 3.11+ with virtual environment configured

### 2.2 Starting the Platform
To launch all services, open a terminal in the project directory:

#### Option A: One-Click Windows Startup Script (Recommended)
```powershell
.\start.ps1
```
*This script automatically verifies Docker Desktop, launches the PostgreSQL container, validates database migrations, verifies ML models, starts the FastAPI backend, and starts the Vite React frontend.*

#### Option B: Manual Service Startup
1. **Start Database**:
   ```powershell
   docker compose up -d db
   ```
2. **Start Backend API**:
   ```powershell
   cd backend
   .venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000
   ```
3. **Start Frontend Dashboard**:
   ```powershell
   cd frontend
   npm run dev -- --host 127.0.0.1 --port 5173
   ```

### 2.3 Verification of Active Services
Once started, the services operate on the following URLs:
- **Frontend Dashboard**: [http://localhost:5173](http://localhost:5173)
- **FastAPI Interactive Swagger Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check Endpoint**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
- **PostgreSQL Database**: `localhost:5432` (`db: sentriq_soc`, `user: sentriq_admin`)

---

# 3. User Access & Identity Model

### 3.1 Platform Access (Analyst Console)
Sentriq operates as an enterprise SOC workspace. When launched, the platform opens directly into the authenticated **Security Analyst Console**:
- **Security Analyst Role**: Inspects live alerts, loads benchmark datasets, triggers ML inferences, reviews AI agent findings, and approves or rejects containment playbooks.
- **Security Administrator Role**: Manages infrastructure settings, reviews system health, and inspects database connection metrics.

### 3.2 Monitored Enterprise Identities (Telemetry Layer)
Inside the security telemetry database, Sentriq tracks network sessions and authentication events associated with various enterprise identities:
- **Administrative Accounts**: `admin`, `dev-operator`
- **Internal Service Accounts**: `svc-payment`, `api-gateway`
- **Regular Employees**: `alice`, `bob`, `carol`, `david`

*Example Use*: In brute-force attack scenarios, the system flags repeated failed authentication attempts targeting the `admin` account over SSH (port 22), followed by unauthorized privilege escalation (`sudo -i`).

---

# 4. User Interface Navigation & Global Layout

The user interface follows a professional, data-dense enterprise dark theme (`#0B1120`, `#131C2E`, `#38BDF8`).

### 4.1 Global Navigation Elements
1. **Top Navigation Bar**:
   - **UTC Telemetry Clock**: Displays live Coordinated Universal Time with real-time seconds ticking.
   - **Database Connection Pill**: A live health indicator (`● Docker PostgreSQL 16 Connected`). If the database disconnects, it turns amber/red.
   - **Faculty Demo Mode Button**: A blue button in the top bar opening a guided walkthrough modal.
2. **Left Sidebar**:
   - **Dashboard** (`/`): Executive metrics, 24-hour threat trend area chart, attack distributions.
   - **Security Logs** (`/logs`): Ingestion, log filtering, raw JSON feature extraction, and SHAP explainability.
   - **Threat Analysis** (`/analysis`): Machine learning testing workbench and probability distributions.
   - **Incidents** (`/incidents`): Correlated multi-stage attack incidents and investigation timelines.
   - **Settings** (`/settings`): System configuration, database engine stats, and service statuses.
3. **Bottom Telemetry Control Bar**:
   - Fixed at the bottom of the screen, providing streaming controls (*Play/Pause, 1x/2x/5x speed*, scenario injection, and a live marquee alert ticker).

---

# 5. Module 1: SOC Dashboard (`/`)

### Purpose
The **Dashboard** serves as the executive mission-control center for the Security Operations Center. It provides high-level visibility over processed events, active threats, and system posture.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                   DASHBOARD OVERVIEW                                   │
├───────────────────┬───────────────────┬────────────────────────┬───────────────────────┤
│ TOTAL PROCESSED   │ ACTIVE INCIDENTS  │ CRITICAL INCIDENTS     │ HIGH-RISK INCIDENTS   │
│       347         │        12         │           4            │           6           │
└───────────────────┴───────────────────┴────────────────────────┴───────────────────────┘
┌───────────────────────────────────────────────┬────────────────────────────────────────┐
│ 24-HOUR THREAT TREND (AREA CHART)             │ ATTACK CATEGORY DISTRIBUTION (BAR CHART│
│ [ Dynamic hourly volume of malicious traffic] │ [ DoS, Brute Force, Port Scan, etc.  ] │
└───────────────────────────────────────────────┴────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ RECENT INCIDENTS TABLE (Code, Title, Attack Type, Severity Badge, Status, Timestamp)   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Elements & How to Use Them:
1. **KPI Cards**:
   - **Total Events Processed**: Cumulative count of all raw flow records and logs in PostgreSQL.
   - **Active Incidents**: Incidents currently in `Open` or `Investigating` status.
   - **Critical Incidents**: Incidents with a 4-factor risk score $\ge 80$.
   - **High-Risk Incidents**: Incidents with a risk score between $60$ and $79$.
2. **24-Hour Threat Trend**: An interactive Recharts area graph. Hover your cursor over any data point to inspect the exact timestamp and event count.
3. **Attack Category Distribution**: A horizontal bar chart displaying the frequency of each attack family (*Normal, Brute Force, DoS, Port Scan, Web Attack, Exploitation*).
4. **Recent Incidents Table**:
   - Lists the latest security incidents.
   - Click any incident code (e.g. `INC-2026-0059`) to navigate directly to its detailed attack timeline.

---

# 6. Module 2: Security Logs Explorer (`/logs`)

### Purpose
The **Security Logs Explorer** provides deep visibility into normalized network events, individual connection features, and ingestion telemetry.

### User Interface Controls:
1. **Search & Filter Bar**:
   - **Search Input**: Filter logs by keyword, IP address (e.g. `198.51.100.45`), port, or username.
   - **Severity Dropdown**: Filter by `Critical`, `High`, `Medium`, or `Low`.
   - **Attack Type Dropdown**: Filter by `Brute Force`, `DoS`, `Port Scan`, `Web Attack`, `Exploitation`, or `Normal`.
   - **Source Dropdown**: Filter by network sensor, benchmark tap, or auth service.
2. **Telemetry Stats Banner**: Displays real-time counts for Total Events, Threats, Benign Flows, and Benchmark Records (`UNSW: 40 | CIC: 20`).
3. **The Security Events Table**: Displays timestamp, source, event type, source/destination endpoints, protocol, attack classification, severity badge, and benchmark status.

### How to Inspect an Event:
1. Click on any row in the table.
2. A **Slide-Over Inspection Drawer** opens from the right side of the screen.
3. The drawer displays:
   - Full event metadata (Event ID, IPs, Ports, Protocol, User Identity).
   - **Raw Feature Vector (JSON)**: The authentic mathematical features extracted from the CSV or network flow (`dur`, `spkts`, `dpkts`, `sbytes`, `rate`, `sttl`, `proto`, etc.).
   - **Copy JSON Button**: Copies the complete raw feature payload to your clipboard.
   - **Explain with SHAP Button**: Launches the Explainable AI attribution drawer.

---

# 7. Module 3: Benchmark & Custom Dataset Ingestion

Sentriq supports both pre-configured benchmark datasets and arbitrary user-uploaded CSV datasets.

```
                    ┌───────────────────────────────────────────────┐
                    │          DATA INGESTION ACTION BAR            │
                    ├───────────────┬───────────────┬───────────────┤
                    │ Load UNSW-NB15│ Load CIC-IDS17│ Upload CSV    │
                    └───────────────┴───────────────┴───────────────┘
```

### 7.1 Option 1: Loading the UNSW-NB15 Benchmark
- **Action**: Click the blue button **"Load UNSW-NB15"**.
- **What Happens**: The backend reads [`data/benchmark/unsw_nb15_sample.csv`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/data/benchmark/unsw_nb15_sample.csv), normalizes the 44 authentic flow attributes (`dur`, `proto`, `service`, `spkts`, `dpkts`, `sbytes`, `rate`, `sttl`, `ct_*`), and saves the records to PostgreSQL with `is_simulated = False` and `source = "unsw_nb15_network_tap"`.
- **Notification**: A toast banner confirms: `Ingested 20 authentic records from UNSW-NB15 benchmark dataset.`

### 7.2 Option 2: Loading the CIC-IDS2017 Benchmark
- **Action**: Click the indigo button **"Load CIC-IDS2017"**.
- **What Happens**: The backend reads [`data/benchmark/cic_ids2017_sample.csv`](file:///d:/23331A4749/Final%20Year%20Project/Sentriq/data/benchmark/cic_ids2017_sample.csv), parses bidirectional flow features (`Flow Duration`, `Total Fwd/Bwd Packets`, `Flow Packets/s`, `Protocol`, `Destination Port`), and inserts them with `is_simulated = False` and `source = "cic_ids2017_network_tap"`.
- **Notification**: A toast banner confirms: `Ingested 20 authentic records from CIC-IDS2017 benchmark dataset.`

### 7.3 Option 3: Uploading a Custom Dataset CSV
- **Action**: Click the green button **"Upload Dataset CSV"**.
- **What Happens**:
  1. A file browser opens. Select any `.csv` file on your machine.
  2. The frontend sends the file to `POST /api/v1/events/upload-csv`.
  3. The backend **Intelligent Schema Detector** examines the headers:
     - Detects `dur` / `attack_cat` $\rightarrow$ parses as **UNSW-NB15 format**.
     - Detects `Flow Duration` / `Total Fwd Packets` $\rightarrow$ parses as **CIC-IDS2017 format**.
     - Detects generic headers $\rightarrow$ parses as **Custom Security Logs format**.
  4. Records are normalized and committed to PostgreSQL in an async batch.
- **Notification**: A green toast confirms: `Successfully ingested X records in [Detected Schema] format.`

---

# 8. Module 4: Machine Learning Threat Analysis (`/analysis`)

### Purpose
The **Threat Analysis Workbench** allows analysts and evaluators to interact directly with the trained Machine Learning models and test custom feature vectors.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ MODEL STATUS: Random Forest Ensemble | Binary Acc: 96.67% | Weighted F1: 0.9669        │
├────────────────────────────────────────┬───────────────────────────────────────────────┤
│ FEATURE WORKBENCH / EVENT SELECTOR     │ THREAT VERDICT & PROBABILITY DISTRIBUTION     │
│ [ Preset: DoS Burst / Brute Force ]    │ Verdict: MALICIOUS (87.2% Confidence)         │
│ dur: 0.85      spkts: 75    rate: 194  │ [ Recharts Probability Bar Chart - 6 Classes] │
│ proto: TCP     service: http           │ Explainable Heuristic Reasoning Box           │
└────────────────────────────────────────┴───────────────────────────────────────────────┘
```

### Step-by-Step Usage:
1. **Inspect Active Model Status**: The top banner displays the algorithm (`RandomForestClassifier`), version, binary accuracy (**96.67%**), weighted F1 score (**0.9669**), and supported attack categories.
2. **Select or Populate Features**:
   - **Method A**: Select an existing security event from the database dropdown.
   - **Method B**: Click any quick preset button (*"DoS Burst Preset"*, *"Brute Force Preset"*, *"Port Recon Preset"*, *"Benign Traffic Preset"*). The 14 numerical fields will populate automatically.
   - **Method C**: Manually type custom numbers into the duration, packet count, or byte volume inputs.
3. **Execute Prediction**: Click the blue button **"Run Threat Inference"**.
4. **Interpret Output**:
   - **Threat Verdict Card**: Displays either `MALICIOUS` (red) or `BENIGN` (green) with exact confidence percentage.
   - **Class Probability Distribution**: A horizontal bar chart displaying model confidence across all 6 classes (*Normal, Brute Force, DoS, Port Scan, Web Attack, Exploitation*).
   - **Explainable Evidence Box**: Synthesizes rule-assisted heuristic reasoning (e.g. *"Elevated packet rate and byte volume on web port 80 indicates volumetric flooding"*).

---

# 9. Module 5: Explainable AI & SHAP Attribution

### Purpose
In mission-critical security environments, "black-box" machine learning predictions cannot be trusted without proof. Sentriq uses **SHAP (SHapley Additive exPlanations)** based on cooperative game theory to quantify the exact contribution of each feature to the model's verdict.

### How to View SHAP Explanations:
1. On the **Security Logs** page, click any event row to open the side drawer.
2. Click the **"Explain with SHAP"** button.
3. The **Explainability Drawer** opens:
   - **Base Value ($E[f(x)]$ = 0.65)**: The baseline probability across the training corpus.
   - **Diverging Attribution Bar Chart**:
     - **Red Bars (Positive Values)**: Features that pushed the AI towards flagging the event as an attack (e.g. `ct_dst_sport_ltm = +0.24`, `rate = +0.18`).
     - **Green Bars (Negative Values)**: Features that pushed the AI towards classifying the event as benign (e.g. `dur = -0.08`).
   - **Rule-to-XAI Consensus Check**: Evaluates whether the statistical SHAP mathematical attribution agrees with deterministic security heuristic rules (displays `Consensual` badge).

---

# 10. Module 6: Incident Management & Attack Timelines (`/incidents`)

### Purpose
Raw security alerts in isolation create alert fatigue. Sentriq's **15-Minute Sliding-Window Event Correlation Engine** (`correlation_engine.py`) condenses isolated alerts into multi-stage attack incidents.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              INCIDENT INC-2026-0059                                    │
│ Title: Multi-Stage SSH Brute Force & Privilege Escalation | Asset: auth-service        │
├──────────────────────────────────────┬─────────────────────────────────────────────────┤
│ TRANSPARENT 4-FACTOR RISK BREAKDOWN  │ CORRELATED CHRONOLOGICAL ATTACK TIMELINE        │
│ [ Risk Score: 89/100 - CRITICAL ]    │ • T+0s: Port Recon Scan (Port 22 probe)         │
│ Severity: 75/100 (30% weight)        │ • T+15s: 8x Failed SSH Logins (User: admin)     │
│ ML Confidence: 87/100 (30% weight)   │ • T+45s: Successful Login from 198.51.100.45    │
│ Asset Importance: 100/100 (20% weight│ • T+120s: Privilege Escalation (sudo -i command)│
│ Attack Impact: 100/100 (20% weight)  │                                                 │
└──────────────────────────────────────┴─────────────────────────────────────────────────┘
```

### How to Investigate an Incident:
1. Navigate to **Incidents** (`/incidents`) from the left sidebar.
2. Click on an incident row (e.g. `INC-2026-0059`).
3. The **Incident Details** page (`IncidentDetails.tsx`) displays:
   - **Incident Header**: Incident identifier, severity badge, lifecycle state dropdown (`Open`, `Investigating`, `Resolved`, `Closed`), and affected asset.
   - **Correlated Attack Timeline**: Chronological vertical sequence displaying relative time deltas ($T+0\text{s}$, $T+15\text{s}$, $T+45\text{s}$), protocol details, source/destination endpoints, and user accounts.
   - **Analyst Investigation Notes**: An auditable log where analysts can record observations and findings.

---

# 11. Module 7: Deterministic 4-Factor Risk Engine

Unlike commercial tools that generate opaque or arbitrary risk ratings, Sentriq implements a strict, transparent mathematical formula based on PRD Section 13:

$$\text{Total Risk} = (\text{Severity} \times 0.3) + (\text{ML Confidence} \times 0.3) + (\text{Asset Criticality} \times 0.2) + (\text{Attack Impact} \times 0.2)$$

### Factor Mappings:
1. **Severity (30% Weight)**: Derived from the peak severity of correlated events:
   - Low = 25, Medium = 50, High = 75, Critical = 100.
2. **ML Confidence (30% Weight)**: Scaled linearly from model prediction probability ($0.0 - 1.0 \rightarrow 0 - 100$).
3. **Asset Criticality (20% Weight)**: Based on affected infrastructure:
   - Critical Core Database / Authentication Servers = 100
   - Internal Application Servers = 70
   - DMZ Web Servers = 50
   - General Workstations = 30
4. **Attack Impact (20% Weight)**: Based on potential consequence:
   - Remote Code Execution / Privilege Escalation = 100
   - Account Compromise / Brute Force = 80
   - Denial of Service (Availability) = 70
   - Port Scanning / Reconnaissance = 30

### Risk Levels:
- **Critical**: $\ge 80$
- **High**: $60 - 79$
- **Medium**: $30 - 59$
- **Low**: $< 30$

The incident page renders a circular risk gauge and weighted progress bars displaying each factor's exact contribution.

---

# 12. Module 8: Multi-Agent AI Investigation & Grounded Copilot

Sentriq deploys **4 Specialized AI Agents** coordinated by an orchestrator to automate Tier-1 analyst triage:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                MULTI-AGENT TRIAGE                                      │
├────────────────────┬────────────────────┬────────────────────┬─────────────────────────┤
│ INVESTIGATION AGENT│ CORRELATION AGENT  │ RESPONSE AGENT     │ REPORTING AGENT         │
│ • Root-Cause Entry │ • Attack Chain Map │ • Containment Plan │ • Executive Markdown    │
│ • MITRE T1110 Map  │ • Kill-Chain Phase │ • Firewall Rules   │ • PDF Incident Brief    │
│ • Blast Radius:High│ • T+0s to T+120s   │ • Pending Review   │ • Compliance Ready      │
└────────────────────┴────────────────────┴────────────────────┴─────────────────────────┘
```

### The Grounded AI Copilot Drawer:
1. Click the **"Open AI SOC Copilot"** button at the top of the incident page.
2. A slide-over AI Copilot drawer opens.
3. Click any quick query chip:
   - *"Explain Attack Narrative"*
   - *"What is the Blast Radius?"*
   - *"List Recommended Actions"*
4. **Zero-Hallucination Guarantee**: The Copilot executes deterministic SQL queries against PostgreSQL. It only answers using verified event records and cites the exact database IDs in an expandable **"Grounded Database Facts"** accordion.

---

# 13. Module 9: Human-in-the-Loop (HITL) Containment

Under **PRD Requirement FR-10**, autonomous AI is strictly prohibited from executing destructive remediation actions (such as blocking firewall ports or isolating servers) without human authorization.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              CONTAINMENT ACTIONS (HITL)                                │
├────────────────────────────────────────────────────────────────────────────────────────┤
│ [Pending Review] Block IP 198.51.100.45 on Edge Firewall (iptables command)            │
│ Analyst Justification Note: [ Confirmed external malicious brute force           ]     │
│                   [ Approve & Apply (Green) ]    [ Reject (Red) ]                      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

### How to Review and Authorize an Action:
1. Locate the **Containment Actions Card** on the incident page.
2. Proposed actions display a pulsating amber badge: `Pending Review`.
3. Review the proposed shell/firewall command:
   ```bash
   iptables -A INPUT -s 198.51.100.45 -j DROP
   ```
4. Optional: Enter an analyst justification note in the text input.
5. Click **"Approve & Apply"**:
   - Status transitions to `Approved (Executed: True)`.
   - The action is committed to the database with an immutable audit log timestamp.
6. Alternatively, click **"Reject"** to dismiss the proposal with an audit reason.

---

# 14. Module 10: Executive Incident Report Generation

### Purpose
Security incidents require formal documentation for executive leadership, legal teams, and regulatory compliance.

### How to Generate and Export Reports:
1. At the top of the Incident Details page, click the **"Executive Report"** button.
2. The **Executive Report Modal** opens, rendering a formatted GitHub-flavored Markdown document containing:
   - Executive Incident Summary
   - Incident Metadata & Classification
   - Deterministic 4-Factor Risk Breakdown
   - MITRE ATT&CK Matrix Mapping
   - Chronological Attack Timeline
   - Verified Indicators of Compromise (IOCs)
   - Containment & Remediation Audit Log
3. Click **"Download .md"** to save the report file directly to your computer.
4. Click **"Copy Markdown"** to copy the formatted text to your clipboard.

---

# 15. Module 11: Real-Time Stream Simulation & WebSocket Hub

### Purpose
To simulate live enterprise operations, Sentriq includes an asynchronous background streamer and bidirectional WebSocket hub at `/ws/soc-telemetry`.

### Using the Live Telemetry Control Bar:
Located at the bottom of the screen:
- **Play / Pause Button**: Starts or halts real-time background event generation.
- **Speed Multiplier**: Toggles between $1\times$ (normal speed), $2\times$, and $5\times$ (rapid simulation).
- **Inject Scenario Dropdown**: Injects an immediate burst of *Brute Force*, *DoS Flood*, or *Port Scan* traffic into the live stream.
- **Live Marquee Alert Ticker**: Scrolls real-time threat detection alerts across the screen as events are evaluated by the ML inference engine in flight.

---

# 16. System Verification & Troubleshooting

### 16.1 Automated Verification Commands
You can verify the entire platform anytime using the built-in terminal scripts:

1. **Run Full Automated Test Suite (27 Tests)**:
   ```powershell
   .venv\Scripts\python.exe -m pytest -v
   ```
   *Expected Result*: `27 passed in ~1.75s`

2. **Run End-to-End Demonstration Script (9 Stages)**:
   ```powershell
   .venv\Scripts\python.exe backend/scripts/demo_orchestrator.py
   ```
   *Expected Result*: `ALL 9 END-TO-END DEMONSTRATION STAGES VERIFIED SUCCESSFULLY!`

3. **Verify Frontend Production Build**:
   ```powershell
   cd frontend
   npm run build
   ```
   *Expected Result*: `built in ~6.0s (0 errors)`

---

### 16.2 Common Troubleshooting Scenarios

| Issue | Root Cause | Solution |
| :--- | :--- | :--- |
| **"Database Disconnected" badge in Navbar** | PostgreSQL container is stopped. | Run `docker compose up -d db` and verify Docker Desktop is running. |
| **Frontend displays network error when loading logs** | FastAPI backend server is not running. | Run `.venv\Scripts\uvicorn app.main:app --host 127.0.0.1 --port 8000` in the `backend/` directory. |
| **Port 5432 or 8000 already in use** | A dangling process is holding the port. | Check running processes via PowerShell: `Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess` and terminate if needed. |
| **CSV upload returns 400 Bad Request** | Uploaded file is empty or does not have a `.csv` extension. | Ensure file is a valid CSV with headers from UNSW-NB15, CIC-IDS2017, or standard security logs. |

