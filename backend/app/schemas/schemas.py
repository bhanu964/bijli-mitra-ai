from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime

class BillExtractionSchema(BaseModel):
    field_name: str
    raw_value: Optional[str] = None
    confidence: float = 1.0
    page_number: int = 1
    extraction_method: str = "DIGITAL_PDF"
    is_verified: bool = False
    user_override_value: Optional[str] = None

class BillVerificationRequest(BaseModel):
    utility_code: str = "TGSPDCL"
    service_number: Optional[str] = None
    consumer_name: Optional[str] = None
    consumer_category: str = "LT-I Domestic"
    billing_month: str # YYYY-MM
    issue_date: Optional[date] = None
    due_date: Optional[date] = None
    previous_reading: Optional[float] = None
    current_reading: Optional[float] = None
    consumption_units: float
    contracted_load_kw: float = 1.0
    printed_total: float
    
    # Printed component values for comparison
    printed_energy_charges: Optional[float] = None
    printed_customer_charges: Optional[float] = None
    printed_fixed_charges: Optional[float] = None
    printed_electricity_duty: Optional[float] = None
    printed_fsa_charges: Optional[float] = None
    printed_true_up_charges: Optional[float] = None
    printed_arrears: Optional[float] = None
    printed_adjustments: Optional[float] = None
    printed_subsidy: Optional[float] = None
    
    is_gruha_jyothi: bool = False
    gruha_jyothi_eligible: bool = False
    ration_card_number: Optional[str] = None

class SlabBreakdownItem(BaseModel):
    slab: str
    units: float
    rate: float
    amount: float

class ChargeBreakdownItem(BaseModel):
    charge_type: str
    label: str
    printed_amount: float
    computed_amount: Optional[float] = None
    difference: float = 0.0
    is_discrepant: bool = False
    legal_source: Optional[str] = None
    explanation: Optional[str] = None

class AnomalyItem(BaseModel):
    severity: str # LOW, MEDIUM, HIGH, CRITICAL
    issue_type: str
    description: str
    legal_reference: Optional[str] = None
    suggested_action: Optional[str] = None

class CalculationResultSchema(BaseModel):
    bill_id: int
    tariff_version: str
    effective_dates: str
    status: str
    
    consumption_units: float
    contracted_load_kw: float
    category_determined: str
    
    energy_charges: float
    energy_slabs: List[SlabBreakdownItem]
    customer_charges: float
    fixed_charges: float
    electricity_duty: float
    fsa_charges: float
    true_up_charges: float
    subsidies: float
    arrears: float
    adjustments: float
    
    computed_total: float
    printed_total: float
    total_difference: float
    
    itemized_charges: List[ChargeBreakdownItem]
    anomalies: List[AnomalyItem]
    explanation_en: str
    explanation_te: str
    source_citations: List[str]

class BillSummarySchema(BaseModel):
    id: int
    utility_code: str
    service_number: Optional[str] = None
    consumer_name: Optional[str] = None
    billing_month: str
    consumption_units: float
    printed_total: float
    status: str
    is_gruha_jyothi: bool
    created_at: datetime
    has_discrepancy: bool = False

class ChatRequestSchema(BaseModel):
    bill_id: Optional[int] = None
    session_id: str = "default_session"
    message: str
    language: str = "en" # "en" or "te"

class ChatResponseSchema(BaseModel):
    session_id: str
    reply_en: str
    reply_te: str
    grounded_facts: List[str]
    suggested_questions: List[str]

class AnalyticsSummarySchema(BaseModel):
    total_bills_analyzed: int
    latest_bill_amount: float
    latest_units: float
    previous_month_units: Optional[float] = None
    consumption_change_pct: Optional[float] = None
    average_monthly_spend: float
    average_monthly_units: float
    highest_month: Optional[str] = None
    lowest_month: Optional[str] = None
    monthly_trend: List[Dict[str, Any]]
    discrepancies_detected_count: int
