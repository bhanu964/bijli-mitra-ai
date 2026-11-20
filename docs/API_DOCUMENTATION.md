# BIJLI MITRA AI — API DOCUMENTATION
## REST API Specification for Telangana Personalized Billing Assistance

**Base URL:** `http://localhost:8000/api`  
**Interactive Swagger UI:** `http://localhost:8000/docs`  
**Interactive ReDoc:** `http://localhost:8000/redoc`

---

### Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/health` | System health check, version, and supported utilities |
| `POST` | `/api/bills/upload` | Upload bill (PDF/JPG/PNG), run duplicate check, extract fields via OCR |
| `GET` | `/api/bills` | List all bills with summaries, status, and discrepancy flags |
| `GET` | `/api/bills/{bill_id}` | Retrieve complete details, extractions, itemized charges, and calculations |
| `PUT` | `/api/bills/{bill_id}/verify` | Consumer verification endpoint to review and update extracted values |
| `POST` | `/api/bills/{bill_id}/calculate` | Run deterministic tariff calculation engine and anomaly detection |
| `DELETE`| `/api/bills/{bill_id}` | Delete bill record and associated stored documents |
| `GET` | `/api/tariffs` | List all versioned tariff schedules (FY 23-24 to 26-27) with official sources |
| `GET` | `/api/tariffs/{version}` | Retrieve specific financial year tariff slabs and customer charge rules |
| `GET` | `/api/analytics/summary` | Retrieve consumption history, spend metrics, and trend charts |
| `GET` | `/api/analytics/savings/{bill_id}` | Retrieve personalized energy savings and Gruha Jyothi cliff guidance |
| `POST` | `/api/chat` | Bilingual conversational assistant grounded in TGERC regulatory documents |

---

### Detailed Endpoint Specifications

#### 1. System Health Check
- **Endpoint:** `GET /api/health`
- **Response (200 OK):**
```json
{
  "status": "HEALTHY",
  "service": "BIJLI MITRA AI Backend",
  "version": "1.0.0",
  "jurisdiction": "Telangana Electricity Regulatory Commission (TGERC)",
  "utilities_supported": ["TGSPDCL", "TGNPDCL"]
}
```

#### 2. Bill Document Upload & OCR Extraction
- **Endpoint:** `POST /api/bills/upload`
- **Content-Type:** `multipart/form-data`
- **Body:** `file: Binary (PDF, JPG, PNG)`
- **Response (200 OK):**
```json
{
  "bill_id": 1,
  "status": "EXTRACTED",
  "message": "Bill successfully read. Please review the extracted information.",
  "extracted_data": {
    "utility_code": "TGSPDCL",
    "service_number": "1004589211",
    "consumer_name": "S. K. Narayana Rao",
    "consumer_category": "LT-I Domestic",
    "billing_month": "2026-11",
    "consumption_units": 180.0,
    "contracted_load_kw": 2.0,
    "previous_reading": 12450.0,
    "current_reading": 12630.0,
    "printed_total": 863.80,
    "is_gruha_jyothi": false
  }
}
```

#### 3. Consumer Verification & Update (Module 4)
- **Endpoint:** `PUT /api/bills/{bill_id}/verify`
- **Content-Type:** `application/json`
- **Payload:**
```json
{
  "utility_code": "TGSPDCL",
  "service_number": "1004589211",
  "consumer_name": "S. K. Narayana Rao",
  "consumer_category": "LT-I Domestic",
  "billing_month": "2026-11",
  "consumption_units": 180.0,
  "contracted_load_kw": 2.0,
  "printed_total": 863.80,
  "is_gruha_jyothi": false,
  "gruha_jyothi_eligible": false
}
```

#### 4. Deterministic Bill Calculation (Module 5)
- **Endpoint:** `POST /api/bills/{bill_id}/calculate`
- **Response (200 OK):**
```json
{
  "bill_id": 1,
  "tariff_version": "FY 2026-27",
  "effective_dates": "2026-04-01 to 2027-03-31",
  "status": "VERIFIED_MATCH",
  "consumption_units": 180.0,
  "contracted_load_kw": 2.0,
  "category_determined": "LT-I(B)(i)",
  "energy_charges": 724.0,
  "energy_slabs": [
    {"slab": "0-100 units", "units": 100.0, "rate": 3.40, "amount": 340.0},
    {"slab": "101-200 units", "units": 80.0, "rate": 4.80, "amount": 384.0}
  ],
  "customer_charges": 90.0,
  "fixed_charges": 20.0,
  "electricity_duty": 10.80,
  "true_up_charges": 54.0,
  "computed_total": 863.80,
  "printed_total": 863.80,
  "total_difference": 0.0,
  "anomalies": [],
  "explanation_en": "Your monthly electricity bill for 180 units has been evaluated under the LT-I(B)(i) domestic tariff...",
  "explanation_te": "మీ నెలవారీ విద్యుత్ వినియోగం 180 యూనిట్లకు LT-I(B)(i) గృహ కేటగిరీ కింద లెక్కించబడింది..."
}
```

#### 5. Bilingual AI Chat Assistant (Module 12)
- **Endpoint:** `POST /api/chat`
- **Payload:**
```json
{
  "message": "Why is there a True-Up charge on my bill?",
  "bill_id": 1,
  "language": "en"
}
```
- **Response (200 OK):**
```json
{
  "session_id": "default_session",
  "reply_en": "The True-Up charge on your bill reflects regulatory recovery of power purchase adjustments mandated by TGERC Order dated 05.10.2026...",
  "reply_te": "మీ బిల్లులోని 'ట్రూ-అప్' ఛార్జీ అనేది విద్యుత్ కొనుగోలు సర్దుబాటు రికవరీ (TGERC ఉత్తర్వు 05.10.2026)...",
  "grounded_facts": ["TGERC Order dated 05.10.2026, Clause 12"],
  "suggested_questions": [
    "How does the Gruha Jyothi 200-unit limit work?",
    "What should I do if my bill is erroneous or overcharged?"
  ]
}
```
