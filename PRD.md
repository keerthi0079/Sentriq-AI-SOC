Product Requirements Document (PRD)

Autonomous AI Security Operations Center (AI-SOC)

Document Type: Product Requirements Document
Project Type: Final-Year Academic Major Project
Primary Domain: Artificial Intelligence, Data Security, Data Engineering
Current Implementation Status: Phases 1–3 completed; Phase 4 onward planned incrementally

1. Product Overview

1.1 Product Name

Autonomous AI Security Operations Center (AI-SOC)

1.2 Product Vision

AI-SOC is an intelligent security monitoring and incident-management platform designed to help security analysts understand large volumes of security events without manually reviewing every event. The platform takes security data, prepares it into a common format, applies machine-learning-based threat detection, presents alerts in a centralized dashboard, and progressively adds risk scoring, event correlation, explainability, and AI-assisted investigation.

The academic prototype is designed to demonstrate the complete journey from security data to actionable incident information while keeping human approval in the response process.

1.3 Product Goal

Build a practical and explainable security platform that can:

Collect and normalize security-event data.

Detect suspicious and malicious activity using machine learning.

Classify supported attack categories.

Prioritize events using a transparent risk score.

Correlate related security events into meaningful incidents.

Explain why an event was detected.

Assist analysts with investigation and response recommendations.

Present security activity through a professional SOC dashboard.

1.4 Target Users

SOC Analyst
Reviews alerts, investigates incidents, checks evidence, and decides on response actions.

Security Engineer
Monitors detection performance, data sources, and system behavior.

IT Administrator
Uses incident information to understand affected systems and coordinate remediation.

Project Faculty / Reviewer
Evaluates system architecture, implementation, technical depth, usability, and measured results.

2. Problem Statement

Organizations generate large volumes of security events from network traffic, servers, applications, databases, firewalls, cloud platforms, and user systems. Manual analysis becomes difficult as the number of events increases. Traditional monitoring approaches may generate many alerts without providing enough context about how those alerts are related. Analysts then have to identify important alerts, determine whether they belong to the same incident, understand the likely severity, and prepare a response. This creates alert fatigue and delays investigation.

AI-SOC addresses this problem by combining data processing, machine learning, incident correlation, risk assessment, and analyst-oriented visualization into one platform.

3. Product Objectives

Standardize security data from multiple sources into a common event structure.

Detect security threats using supervised machine-learning models and selected anomaly-detection approaches as the project grows.

Classify attack categories supported by the selected datasets.

Prioritize incidents using transparent risk scoring based on measurable factors.

Correlate related events so analysts can understand an attack as a timeline rather than isolated alerts.

Improve interpretability by providing understandable reasons for detections and risk levels.

Support investigation through structured incident views and, in later phases, specialized AI agents.

Evaluate the system using detection quality, false-positive behavior, and operational response metrics.

4. Product Scope

4.1 In Scope

Security-event ingestion from public benchmark datasets and simulated events.

Data cleaning, normalization, validation, and feature preparation.

Machine-learning-based binary threat detection.

Multi-class attack classification for supported categories.

Alert and incident management.

Risk scoring.

Event correlation.

Explainable detection output.

Real-time or near-real-time dashboard behavior as the project progresses.

AI-assisted investigation and response recommendations in later implementation phases.

Incident and security reports.

4.2 Out of Scope

Direct connection to live enterprise production infrastructure.

Unrestricted autonomous remediation of real systems.

Physical security monitoring.

Guaranteed detection of every possible cyberattack.

Claims of zero-day detection without appropriate data and validation.

Automatic blocking or isolation of real users/devices without human approval.

The current project plan explicitly uses public benchmark datasets and simulated streams and keeps response actions human-approved.

5. Current Product Capabilities

The current implementation has completed the following capabilities:

5.1 Application Foundation

React-based web application.

TypeScript frontend.

Vite development/build environment.

Tailwind CSS styling.

React Router navigation.

Recharts-based visualization.

Axios-based API communication.

FastAPI backend.

SQLAlchemy data layer.

Pydantic validation.

PostgreSQL 16 running in Docker Desktop (via Docker Compose) as the primary database with SQLAlchemy ORM and connection pooling (SQLite retained as an optional fallback for isolated unit testing).

5.2 Security Event Data Layer

Security-event database structure.

Source, event type, attack type, severity, message, label, and timestamp fields.

Public benchmark data preparation workflow.

Simulated authentication/security events.

Cleaning and duplicate removal.

Normalization into a common event structure.

Log filtering by severity, attack type, and source.

5.3 Machine Learning Layer

Reproducible preprocessing pipeline.

Categorical feature encoding for selected security-event fields.

Random Forest binary classification for Normal vs Attack.

Random Forest multi-class classification for supported attack categories.

Saved model and preprocessing artifacts.

Model evaluation using accuracy, precision, recall, F1 score, and confusion matrices.

Prediction API integrated with the application.

Human-readable rule-based prediction reasons in the current prototype.

5.4 Current Demonstration Data

The prototype currently uses a small simulated dataset for end-to-end testing. The current evaluation must be treated as a demonstration check rather than a benchmark result from the full UNSW-NB15 or CIC-IDS2017 datasets.

6. Supported Security Data

6.1 Primary Benchmark Sources

UNSW-NB15
Used for intrusion-detection research and attack classification. The project plan identifies network traffic features and several attack categories.

CIC-IDS2017
Used for evaluating network-attack detection across benign traffic and several common attack categories.

6.2 Simulated Data

The prototype generates safe simulated events to demonstrate:

Normal login activity.

Repeated failed logins.

Successful authentication after repeated failures.

Brute-force-style suspicious activity.

Other structured security events used to test the system flow.

Simulated data must always be visibly identified as SIMULATED DEMO DATA in documentation and demonstrations.

6.3 Data Preparation Requirements

The data layer should support:

Validation of required fields.

Missing-value handling.

Duplicate removal.

Categorical encoding.

Numerical feature preparation.

Label preservation.

Training/validation/test partitioning.

Class-imbalance handling when full benchmark datasets are used.

Both a binary label and the original attack category should be preserved wherever available.

7. Core Security Event Model

Each normalized security event should conceptually represent:

Unique event identifier.

Event timestamp.

Data source.

Event type.

Attack category.

Severity.

Event message or summary.

Binary attack/anomaly label where available.

Original model-relevant features where required for ML processing.

Creation timestamp.

The event model is the common language shared by the ingestion, ML, risk, correlation, and dashboard layers.

8. User Roles and Permissions

Analyst

View alerts and incidents.

Filter logs.

Analyze selected events.

Review model output.

View risk score and explanation.

Review incident timelines.

Approve or reject proposed response actions.

Administrator

Manage users and application configuration.

Review system health.

Manage data-source settings.

Review model versions and operational statistics as these capabilities are implemented.

The first release can keep authorization simple and expand role-based access later.

9. Functional Requirements

FR-01: Dashboard

The system shall provide a centralized SOC dashboard showing security activity and incident status.

The dashboard should display:

Total security events processed.

Active incidents.

Critical incidents.

High-risk incidents.

Threat trend over time.

Attack category distribution.

Risk-level distribution.

Recent alerts.

Recent incidents.

FR-02: Security Logs

The system shall display normalized security events in a searchable, filterable view.

The logs view should support filtering by:

Severity.

Attack type.

Source.

Time period when implemented.

FR-03: Alert Analysis

For a selected security event, the system shall display:

Prediction.

Attack category.

Confidence.

Severity.

Source.

Detection reason.

Model version.

FR-04: Machine-Learning Detection

The system shall accept a normalized security event and return a machine-learning prediction for supported detection tasks.

The current implementation supports:

Binary detection: Normal vs Attack.

Multi-class classification for supported categories.

FR-05: Risk Assessment

The system shall calculate a transparent risk score from 0 to 100 using configurable factors.

The planned initial factors are:

Severity.

ML confidence.

Asset importance.

Attack impact.

The final risk score shall be mapped to a clear risk level:

Low.

Medium.

High.

Critical.

FR-06: Event Correlation

The system shall group related security events into a single incident when they meet the defined correlation conditions.

Correlation may consider:

Time relationship.

Common source.

Common user or context.

Compatible attack category.

Related security activity.

FR-07: Incident Management

The system shall create and maintain incidents containing:

Incident identifier.

Incident title.

Attack category.

Severity.

Risk score.

Risk level.

Confidence.

Status.

Summary.

Related events.

Timeline.

Creation time.

Suggested incident states:

Open.

Investigating.

Resolved.

Closed.

FR-08: Explainable Detection

The system shall present a human-readable explanation for a detection.

The explanation should identify understandable evidence, such as repeated authentication failures or unusually high traffic characteristics, where those signals are supported by the model and input data.

The system shall not claim that an explanation comes from SHAP or another XAI technique unless that technique has actually been implemented.

FR-09: Investigation Assistance

In later phases, specialized AI agents shall help with:

Event analysis.

Incident context gathering.

Correlation review.

Investigation summary.

Response recommendations.

Report generation.

FR-10: Response Recommendation

The system may recommend actions such as reviewing an account, isolating an affected device, or blocking a suspicious source in a controlled demonstration.

The system shall keep a human analyst in the approval loop for response actions.

FR-11: Reporting

The system shall generate an incident summary containing:

Incident overview.

Detection details.

Risk.

Timeline.

Evidence.

Investigation summary.

Recommended response.

10. Main Attack Detection Scope

The initial detection focus should remain aligned with the benchmark data actually used.

Primary Attack Categories

Brute Force
Repeated attempts to gain access by trying many credentials or authentication attempts.

DoS / DDoS
Abnormally large or disruptive traffic patterns intended to overwhelm a service.

Port Scanning / Reconnaissance
Repeated attempts to inspect many services or ports in order to discover possible entry points.

Web Attacks
Suspicious activity targeting web applications, limited to attack patterns represented by the selected dataset.

Exploitation
Suspicious activity associated with attempts to exploit a system or service weakness, limited to supported dataset patterns.

Extended Scope

Additional categories such as botnet activity, privilege escalation, lateral movement, data exfiltration, insider threat, phishing, malware, ransomware, SQL injection, and XSS should only be added when appropriate data and detection logic are available.

The project should never claim universal attack detection.

11. End-to-End User Journey

A representative user journey is:

Security events enter the platform.

Data is cleaned and normalized.

Relevant features are prepared.

The ML engine evaluates the event.

The system identifies Normal or Attack and predicts a supported attack category.

Confidence and severity are displayed.

Risk scoring determines priority.

Related events are correlated.

A meaningful incident is created.

The analyst reviews the timeline and explanation.

Investigation support provides additional context.

A response recommendation is shown.

The analyst approves or rejects the action.

A report is generated for the incident.

12. Brute Force Demonstration Scenario

The primary demonstration scenario should be a safe simulated account-compromise sequence.

Scenario

A simulated user account receives repeated failed login attempts followed by a successful login.

Expected AI-SOC behavior

Step 1 — Event Generation
Authentication events are generated as simulated data.

Step 2 — Detection
The ML layer identifies the suspicious pattern as an attack and predicts the supported category.

Step 3 — Confidence
The system shows the model confidence.

Step 4 — Risk
The system calculates a risk score based on configured factors.

Step 5 — Correlation
The related login events are grouped into one incident.

Step 6 — Incident View
The analyst sees a clear event timeline and explanation.

Step 7 — Recommendation
The system provides a controlled response recommendation for analyst approval.

This scenario demonstrates the complete platform without performing any real attack.

13. Risk Scoring Requirements

13.1 Purpose

Risk scoring determines which incidents deserve attention first.

13.2 Initial Model

The first implementation uses a transparent weighted model rather than allowing an LLM to invent a score.

Proposed weights:

Severity: 30%.

ML confidence: 30%.

Asset importance: 20%.

Attack impact: 20%.

13.3 Severity Scale

Low.

Medium.

High.

Critical.

13.4 Risk Levels

0–29: Low.

30–59: Medium.

60–79: High.

80–100: Critical.

13.5 Explanation Requirement

Every risk score should be accompanied by a short explanation describing the major contributing factors.

13.6 Future Improvement

Weights may later be calibrated using historical incident data and validated against analyst feedback. Any revised scoring method must remain measurable and documented.

14. Event Correlation Requirements

The purpose of correlation is to turn isolated events into a security story.

Example

A sequence such as repeated login failures followed by a successful login and suspicious privilege use should be treated as a possible account-compromise incident rather than several unrelated alerts.

Correlation Rules

The first implementation should remain deterministic and explainable. It should use:

A configurable time window.

Common source or user context where available.

Compatible event types.

Related attack categories.

The system should prevent the same group of events from creating duplicate incidents.

15. Incident Management Requirements

Incident Creation

An incident may be created when one or more correlated events meet the project's incident criteria.

Incident Details

The incident page should display:

Incident title.

Severity.

Risk score.

Risk level.

Confidence.

Summary.

Related alerts/events.

Event timeline.

Investigation notes as supported.

Recommended response.

Status.

Incident Lifecycle

Open → Investigating → Resolved → Closed

Status transitions should be visible to the analyst and recorded for auditability.

16. Dashboard Requirements

Visual Hierarchy

The dashboard should make the most important security information visible first.

Priority order:

Critical incidents.

High-risk incidents.

Active alerts.

Threat trends.

Detailed logs.

Dashboard Components

KPI cards.

Threat trend chart.

Attack-category chart.

Risk distribution chart.

Recent alerts table.

Active incidents table.

Incident status summary.

Interaction

Users should be able to move from:

Dashboard → Alert → Incident → Timeline → Recommended Response → Report

without losing context.

17. UI/UX and Visual Design System

The design should feel like a professional enterprise security application, not a generic AI product.

17.1 Design Principles

Calm.

Professional.

High readability.

Data-first.

Serious enterprise tone.

Clear hierarchy.

Minimal decorative effects.

Strong use of spacing and alignment.

Motion only when it helps explain system state.

17.2 Explicitly Avoid

Purple gradients.

Pink-to-purple AI gradients.

Neon green/cyan cyberpunk visuals.

Glowing borders everywhere.

Excessive glassmorphism.

Excessive shadows.

Futuristic decorative graphics that reduce readability.

Random gradient backgrounds.

Generic “AI chatbot” styling.

17.3 Recommended Color Palette

Use a restrained enterprise palette:

Purpose

Color Direction

Main background

Deep navy-charcoal

Secondary panels

Dark slate

Primary accent

Steel blue / muted blue

Secondary accent

Desaturated teal

Main text

Soft white

Secondary text

Cool gray

Border

Slate gray

Success

Muted green

Warning

Warm amber

High severity

Burnt orange / amber-red

Critical severity

Deep red

Suggested design feel:

Deep Navy + Slate + Steel Blue + Muted Teal + Amber/Red for Status

This gives the product a security-oriented appearance without looking neon or stereotypically “AI”.

17.4 Severity Colors

Severity colors should be reserved for status information:

Low → muted green/gray.

Medium → muted amber.

High → orange/amber-red.

Critical → deep red.

17.5 Typography

Use a clean modern sans-serif family with strong readability. Avoid decorative fonts.

Recommended hierarchy:

Page title: bold.

Section title: semibold.

Metric: bold and large.

Body text: regular.

Metadata: smaller and muted.

18. Accessibility Requirements

Maintain readable contrast between background and text.

Never communicate severity using color alone.

Provide labels or text alongside status indicators.

Use clear focus states for interactive controls.

Keep tables readable at normal browser zoom.

Avoid flashing or rapidly animated content.

19. Technology Requirements

Current Core Stack

Frontend

React.

TypeScript.

Vite.

Tailwind CSS.

React Router.

Recharts.

Axios.

Backend

Python.

FastAPI.

Uvicorn.

SQLAlchemy.

Pydantic.

Pydantic Settings.

Database

PostgreSQL 16 deployed locally using Docker Desktop (via `docker-compose.yml` with persistent Docker volume, mapped to port 5432, connection pooling via SQLAlchemy and psycopg2/asyncpg).

SQLite retained as an optional secondary lightweight driver strictly for isolated automated unit tests.

Machine Learning

scikit-learn.

Random Forest.

Joblib for model artifacts.

Planned Extensions

Kafka or another message broker for streaming ingestion.

Spark or another stream-processing framework for larger-scale processing.

Elasticsearch or another document/search store for high-volume log search.

SHAP or a comparable XAI technique for model-based feature explanation.

LLM-based agent orchestration for investigation and reporting.

Optional graph storage such as Neo4j if attack-relationship requirements justify it.

Docker Desktop & Docker Compose for containerized infrastructure (PostgreSQL 16, pgAdmin web interface, and multi-service deployment).

Technology Selection Principle

A technology should be added only when it solves a clear project requirement. The system should prefer a stable and understandable implementation over technology complexity for its own sake.

20. Non-Functional Requirements

Performance

Dashboard interactions should feel responsive during prototype use.

API operations should not block unnecessarily.

ML inference should be efficient enough for the intended prototype workload.

Future streaming components should support near-real-time processing.

Reliability

Failed API requests should return meaningful error responses.

Database failures should not silently corrupt data.

Model loading failures should be reported clearly.

Duplicate incidents should be prevented where correlation rules require it.

Security

No hardcoded credentials.

Use environment variables for sensitive configuration.

Validate API inputs.

Restrict sensitive actions to authorized users.

Keep response actions human-approved.

Maintainability

Modular frontend components.

Separated backend routes, schemas, models, and services.

Separate ML training and inference logic.

Clear documentation for every major module.

Scalability

The architecture should make it possible to replace the prototype batch ingestion layer with streaming components later without redesigning the entire product.

21. Data and ML Quality Requirements

The project shall distinguish between prototype demonstration results and benchmark evaluation results.

Required ML Measures

Accuracy.

Precision.

Recall.

F1 score.

Confusion matrix.

False-positive rate where applicable.

Dataset Requirements

When full benchmark datasets are used, the evaluation must:

Use train/validation/test separation.

Avoid target leakage.

Preserve class labels.

Address class imbalance.

Report the evaluated dataset and class distribution.

Avoid unsupported claims based on small simulated samples.

The current project draft explicitly notes that its small simulated sample is not a full UNSW-NB15/CIC-IDS2017 evaluation.

22. Development Phases

Phase 1 — Core Application Foundation ✅

Project structure.

React frontend.

FastAPI backend.

Database setup (PostgreSQL 16 via Docker Desktop, Docker Compose configuration, volume persistence, and SQLAlchemy models).

Dashboard foundation.

Incident APIs.

Basic incident views.

Phase 2 — Data Ingestion and Normalization ✅

Security-event model.

Data directories.

Preprocessing utilities.

Normalization.

Simulated event generator.

Database loading.

Logs API.

Logs dashboard.

Phase 3 — Machine Learning Detection ✅

ML preprocessing.

Random Forest binary model.

Random Forest multi-class model.

Model evaluation.

Prediction API.

Frontend event analysis.

Phase 4 — Risk Scoring and Event Correlation

Transparent risk calculation.

Risk levels.

Risk explanation.

Event correlation.

Incident creation/update.

Incident timeline.

Phase 5 — Near-Real-Time Processing

Simulated event streaming first.

WebSocket dashboard updates.

Later evaluation of Kafka/Spark based on workload and project needs.

Phase 6 — Explainable AI

Model feature contribution analysis.

Better detection explanations.

Analyst-friendly evidence presentation.

Phase 7 — AI-Assisted Investigation

Investigation agent.

Correlation/context agent.

Response recommendation agent.

Reporting agent.

Phase 8 — Final Evaluation and Deployment

Full benchmark evaluation.

False-positive analysis.

Response-time analysis.

UI refinement.

Docker deployment (Docker Desktop multi-container orchestration with frontend, backend, PostgreSQL 16, and worker services).

Documentation.

23. Success Metrics

The final system should be evaluated using measurable outcomes.

ML Metrics

Precision.

Recall.

F1 score.

Attack-class recognition performance.

False-positive rate.

System Metrics

Event processing latency.

Prediction latency.

Incident creation time.

Dashboard response time.

SOC Workflow Metrics

Reduction in duplicate/related alerts after correlation.

Time required to understand an incident before and after correlation.

Percentage of incidents with an understandable explanation.

Percentage of incidents with complete timelines.

No metric should be presented as a result until it is measured in the actual implementation.

24. Reporting Requirements

An incident report should be understandable to both technical and non-technical stakeholders.

Report Sections

Incident Summary.

Detection Details.

Attack Category.

Severity and Risk.

Evidence.

Event Timeline.

Investigation Findings.

Recommended Response.

Incident Status.

Generated Timestamp.

25. Error and Empty-State Requirements

No Data

Show a clear message such as:

“No security events match the selected filters.”

API Failure

Show:

“Unable to load security data. Check the backend connection and try again.”

ML Failure

Show:

“Threat analysis is temporarily unavailable. The event remains available for manual review.”

Model Unavailable

The dashboard must not display a fabricated prediction.

26. Auditability

The platform should preserve enough information to understand how an incident was created.

For each detection or incident, retain where applicable:

Event identifier.

Detection timestamp.

Model version.

Prediction.

Confidence.

Risk score.

Correlation context.

Incident status changes.

Analyst-approved actions.

27. Demo Requirements for Faculty Review

The preferred demonstration sequence is:

1. Dashboard
   Show overall security activity.

2. Security Logs
   Show normalized events from the current data layer.

3. Analyze Event
   Select a simulated suspicious event and run ML detection.

4. Detection Result
   Show attack type, confidence, and reason.

5. Risk Assessment
   Show the calculated risk and contributing factors.

6. Incident View
   Show related events grouped into one incident.

7. Timeline
   Explain how separate events form a meaningful attack story.

8. Planned AI Investigation
   Explain the next layer that will automate context gathering and recommendations.

This approach shows real implementation while clearly separating completed work from planned functionality.

28. Faculty-Friendly Product Explanation

One-Sentence Explanation

AI-SOC is a security monitoring platform that converts large volumes of security events into prioritized and explainable incidents using data processing and machine learning.

Simple Workflow

Security Data → Preprocessing → ML Detection → Risk → Correlation → Incident → Investigation → Response Recommendation → Report

Key Innovation

The project is not limited to detecting whether an event is malicious. It aims to connect detection, prioritization, incident context, explainability, and analyst-assisted response into one workflow.

29. Known Limitations

Current ML training uses a small simulated dataset and should not be treated as a benchmark result.

Current explanations are rule-based rather than model-feature attribution from SHAP/LIME.

Current ingestion is batch-oriented.

Full-scale streaming is not yet implemented.

Advanced agent orchestration is planned rather than complete.

The prototype does not connect to live enterprise networks.

Detection coverage depends on the available datasets and features.

30. Future Product Direction

The platform may later support:

Continuous streaming ingestion.

Additional cloud and container security logs.

Threat-intelligence enrichment.

More advanced anomaly detection.

Better attack-path correlation.

Model monitoring and retraining.

Analyst feedback loops.

Role-based access control.

Controlled response playbooks.

Larger-scale deployment.

31. Product Principles

Evidence before claims — only display results that the system actually measured.

Human oversight — AI supports analysts; high-impact response actions remain controlled.

Explainability — important decisions should have understandable supporting evidence.

Modular growth — each future phase must build on the current stable foundation.

Data realism — simulated data must be identified clearly and never presented as real enterprise data.

Professional security UX — prioritize clarity and trust over decorative AI visual effects.

Technology with purpose — use Kafka, Spark, Elasticsearch, agents, and similar tools only when they solve a demonstrated project requirement.

32. Requirements Traceability to Current Project Plan

The project requirements align with the existing project plan's flow from raw security data through ingestion and normalization, ML detection, event correlation, risk scoring, explainability, investigation, and dashboard output. The current plan identifies UNSW-NB15 and CIC-IDS2017 as primary benchmark datasets, and it keeps live production integration and unrestricted autonomous remediation outside the project boundary.
