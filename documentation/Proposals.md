# Proposal 1

## Project Title
TradSync: Intelligent Job Management and Regulatory Compliance API for Trade Services

## Introduction
Small-to-medium trade enterprises (plumbing, electrical, and carpentry businesses) in New Zealand face heavy administrative burdens complying with strict Health & Safety regulations and Building Code standards while managing daily workflows. The problem addressed is the high operational friction and legal risk associated with manual job tracking, onsite hazard assessments, and regulatory compliance logging. The objective of this project is to develop a centralized job management API that structures field notes, manages client service records, and automatically flags compliance/safety risks against statutory checklists before a job is signed off. The expected benefit is a significant reduction in administrative overhead for tradies, improved onsite safety tracking, and automated, legally sound documentation for council auditing.

## Technologies and Tools Used
The project will be built using the FastAPI full-stack template:
* **Backend:** Python and FastAPI to build asynchronous endpoints handling incoming job telemetry, materials logging, and automated compliance-checking algorithms.
* **Frontend:** React to build a responsive, scannable field-technician dashboard and an administrative command center for tracking active work sites.
* **Database:** PostgreSQL to map complex relational data models, including many-to-many relationships between jobs, field technicians, materials, hazard reports, and statutory compliance clauses.
* **Validation & Security:** Pydantic and SQLModel for rigid input sanitization (ensuring onsite safety data is complete), combined with OAuth2/JWT for role-based access control (separating Apprentices, Certified Tradesmen, and Auditors).

## Final Outcome
The final deliverable will be a deployed full-stack job management prototype tailored for trade industries. Field workers can log job details, track billable hours, and complete interactive, rule-based site safe/compliance checklists. The system features an automated report exporter that compiles immutable job histories and compliance logs into structured summaries. This serves as a highly relevant portfolio piece for the booming construction-technology (ConTech) and regulatory-technology (RegTech) sectors.

---

# Proposal 2

## Project Title
FinLaw: Automated Financial Compliance Workflow and Regulatory Audit System

## Introduction
The financial sector requires rigorous adherence to volatile anti-money laundering (AML) laws and legal compliance frameworks, which currently involves highly inefficient, manual reviews of extensive documentation. This project addresses the operational bottleneck and high human-error risks associated with manual legal compliance checks. The objective is to engineer an automated, state-machine driven document workflow system that tracks, flags, and audits financial documents against predefined compliance rules. The expected impact is a drastic reduction in administrative overhead, institutional legal risks, and a bulletproof, software-driven auditing trail for financial institutions.

## Technologies and Tools Used
This project will be built upon the provided FastAPI full-stack template:
* **Backend:** Python and FastAPI leveraging asynchronous endpoints to simulate concurrent document ingestion and high-performance parsing.
* **Frontend:** React to build an interactive administrative dashboard featuring an interactive Kanban workflow and compliance risk matrices.
* **Database:** PostgreSQL utilizing transactional isolation levels to guarantee the integrity of document metadata and immutable compliance logs, replacing lightweight solutions like SQLite3 for production-grade reliability.
* **ORM & Data Validation:** SQLModel/SQLAlchemy and Pydantic for rigid data-typing, schema enforcement, and input sanitization against legal data fields.
* **Containerization:** Docker and Docker Compose for consistent deployment pipelines and isolated environment management.

## Final Outcome
The final deliverable will be a deployed full-stack compliance web application. The system will allow compliance officers to upload financial document records, transition them through a strict, rule-based Kanban workflow, and automatically generate structured, tamper-proof compliance audit reports. This system bridges the gap between legal rigor and software engineering, making it a highly relevant prototype for modern RegTech (Regulatory Technology) ecosystems.

---

# Proposal 3

## Project Title
ForeXchange: High-Availability Real-Time Remittance and Compliance Telemetry Dashboard

## Introduction
While basic currency applications handle simple static conversions, commercial cross-border remittance demands highly scalable architectures, real-time telemetry (rate tracking), and rigid compliance checks to prevent financial crime. This project addresses the lack of transparent, secure, and production-ready architectures for monitoring international money exchanges. The objective is to engineer a robust, database-driven foreign exchange platform that seamlessly handles concurrent user sessions, live rate simulations, automated fee compliance calculations, and immutable transaction histories. 

## Technologies and Tools Used
The solution will leverage the modern Python web ecosystem via the FastAPI template:
* **Core Backend:** Python 3 and FastAPI utilizing background tasks to process algorithmic currency conversion and transactional compliance checking.
* **Frontend:** React for a responsive, state-managed single-page application (SPA) tracking live market fluctuations.
* **Database Management:** PostgreSQL with strict relational constraints to secure ledger data, migrating local SQLite3 prototypes to an enterprise client-server model.
* **Authentication & Security:** OAuth2 with Password Flow and JWT tokens integrated natively into the FastAPI pipeline to enforce secure, role-based user sessions (e.g., Customer vs. Compliance Auditor).
* **Deployment:** Dockerized microservices orchestrated with Traefik for automated reverse proxy, SSL termination, and load balancing.

## Final Outcome
The expected outcome is a fully functional, containerized prototype of an enterprise money exchange platform. It will feature a secure multi-tier login system, an interactive dashboard visualizing live simulated currency trends, and an immutable ledger module that records and flags simulated cross-border remittance transactions. The architecture demonstrates modern software principles required in both FinTech and telemetry-driven industrial software engineering.