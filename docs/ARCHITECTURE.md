# BIJLI MITRA AI — SYSTEM ARCHITECTURE
## Telangana Government Challenge 13: Personalized Billing Assistance

### 1. High-Level Architecture Overview

**BIJLI MITRA AI** is engineered as a robust, modular monolith combining high-accuracy document processing, deterministic tariff calculations, and grounded bilingual natural language advisory.

```mermaid
flowchart TD
    subgraph UI ["Frontend (Next.js 16 + React 19 + Tailwind CSS)"]
        DASH["Dashboard & Executive Metrics"]
        UPLOAD_UI["Drag-and-Drop Bill Upload"]
        REVIEW_UI["Editable Verification Screen"]
        BREAKDOWN_UI["Itemized Tariff Breakdown"]
        ANALYTICS_UI["Recharts Consumption Trends"]
        CHAT_UI["Bilingual AI Assistant (EN / TE)"]
    end

    subgraph API ["Backend API Layer (FastAPI)"]
        ROUTER["REST API Routers (/bills, /tariffs, /analytics, /chat)"]
    end

    subgraph PROCESSING ["Document Intelligence Pipeline"]
        PYMUPDF["PyMuPDF Digital Text Extractor"]
        OPENCV["OpenCV Adaptive Preprocessing"]
        TESSERACT["Tesseract 5.5 OCR Engine"]
        PARSER["Heuristic & Regex Parser"]
    end

    subgraph ENGINE ["Deterministic Tariff Calculation Engine"]
        REPO["Versioned Tariff Repository (FY 2023-24 to 2026-27)"]
        SLAB_CALC["Tier Selection & Telescopic Slab Evaluator"]
        TRUEUP_CALC["TGERC True-Up Engine (05.10.2026 Order)"]
        GJ_CALC["Gruha Jyothi Zero-Bill Eligibility Evaluator"]
        ANOMALY["Rule-Based Anomaly & Variance Detector"]
    end

    subgraph ADVISORY ["Personalized Bilingual AI Advisor"]
        EXPLAINER["Grounded Natural Language Explainer"]
        SAVINGS["Targeted Savings & Cliff Optimizer"]
        ASSISTANT["Bijli Mitra Chat Assistant (EN & TE)"]
    end

    subgraph STORAGE ["Persistence & Database Layer"]
        DB[("PostgreSQL / SQLite Storage")]
        FILES[("Secure Document Storage (SHA-256)")]
    end

    UPLOAD_UI -->|Upload Document| ROUTER
    ROUTER --> PROCESSING
    PROCESSING -->|Extracted Fields & Confidence| DB
    DB --> REVIEW_UI
    REVIEW_UI -->|User Confirmed Values| ROUTER
    ROUTER --> ENGINE
    ENGINE --> REPO
    ENGINE -->|Itemized Computed Charges & Anomalies| DB
    ENGINE --> ADVISORY
    ADVISORY --> CHAT_UI
    ADVISORY --> BREAKDOWN_UI
    DB --> DASH
    DB --> ANALYTICS_UI
```

---

### 2. Core Architectural Tenets

1. **Deterministic Calculation Integrity:**
   - LLMs are strictly prohibited from calculating electricity bills.
   - All rate lookups, bracket shifts, fixed charges, customer charges, electricity duties, and True-Up recoveries are executed deterministically by Python algorithms validated against official gazetted orders.

2. **Strict Tariff Versioning by Effective Dates:**
   - Tariff schedules are versioned by exact effective dates (e.g. FY 2023-24 from 01.04.2023 to 31.03.2024; FY 2024-25 from 01.11.2024 to 31.03.2025; FY 2026-27 from 01.04.2026 to 31.03.2027).
   - Historical bills are never calculated using current rates.

3. **Explicit Charge Separation:**
   - Every bill component (Energy Charges, Customer Charges, Fixed Charges, Electricity Duty, FSA/FCA, True-Up Recovery, Arrears, Adjustments, Subsidies) is itemized separately.
   - In accordance with TGERC directives, True-Up charges and FSA charges are never bundled into energy charges.

4. **Consumer Verification Workflow (Module 4):**
   - The platform never silently overwrites consumer inputs or accepts low-confidence OCR blindly.
   - Consumers review and confirm extracted values prior to calculation.

5. **Citizen Privacy & Security:**
   - File uploads are validated, size-limited, and fingerprinted using SHA-256 for duplicate detection.
   - Personally Identifiable Information (PII) is kept isolated from public regulatory data.
   - Citizen data is never transmitted to external third-party model providers.

---

### 3. Database Entity Relationship Diagram

```mermaid
erDiagram
    UTILITIES ||--o{ TARIFF_SCHEDULES : provides
    UTILITIES ||--o{ BILLS : issues
    TARIFF_SCHEDULES ||--o{ TARIFF_SLABS : contains
    TARIFF_SCHEDULES ||--o{ CUSTOMER_CHARGE_SLABS : contains
    BILLS ||--o{ BILL_EXTRACTIONS : has
    BILLS ||--o{ BILL_CHARGES : details
    BILLS ||--o| CALCULATION_RESULTS : generates
    BILLS ||--o{ ANOMALY_REPORTS : triggers
    BILLS ||--o{ CHAT_MESSAGES : contextualizes

    UTILITIES {
        int id PK
        string code
        string name
        string state
    }

    TARIFF_SCHEDULES {
        int id PK
        int utility_id FK
        string financial_year
        date effective_from
        date effective_to
        string source_document
    }

    BILLS {
        int id PK
        int utility_id FK
        string service_number
        string billing_month
        float consumption_units
        float contracted_load_kw
        float printed_total
        boolean is_gruha_jyothi
        string file_hash
        string status
    }

    CALCULATION_RESULTS {
        int id PK
        int bill_id FK
        float computed_total
        float total_difference
        string status
        text explanation_en
        text explanation_te
    }
```
