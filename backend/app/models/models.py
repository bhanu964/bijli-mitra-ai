import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Date, DateTime,
    ForeignKey, Text, JSON
)
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Utility(Base):
    __tablename__ = "utilities"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, index=True, nullable=False) # TGSPDCL, TGNPDCL
    name = Column(String(255), nullable=False)
    state = Column(String(50), default="Telangana")
    headquarters = Column(String(100), default="Hyderabad")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    tariff_schedules = relationship("TariffSchedule", back_populates="utility")
    bills = relationship("Bill", back_populates="utility")

class TariffSchedule(Base):
    __tablename__ = "tariff_schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    utility_id = Column(Integer, ForeignKey("utilities.id"), nullable=False)
    financial_year = Column(String(20), index=True, nullable=False) # e.g. "FY 2024-25"
    title = Column(String(255), nullable=False)
    effective_from = Column(Date, nullable=False)
    effective_to = Column(Date, nullable=False)
    source_document = Column(String(255), nullable=False)
    source_clause = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    utility = relationship("Utility", back_populates="tariff_schedules")
    energy_slabs = relationship("TariffSlab", back_populates="schedule")
    customer_slabs = relationship("CustomerChargeSlab", back_populates="schedule")

class TariffSlab(Base):
    __tablename__ = "tariff_slabs"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("tariff_schedules.id"), nullable=False)
    category = Column(String(50), default="LT-I")
    subcategory = Column(String(50), nullable=False) # LT-I(A), LT-I(B)(i), LT-I(B)(ii)
    slab_min = Column(Float, nullable=False)
    slab_max = Column(Float, nullable=False) # float('inf') for above 800
    energy_rate = Column(Float, nullable=False) # Rs / kWh
    fixed_rate = Column(Float, default=10.0) # Rs / kW / month
    fixed_unit = Column(String(20), default="kW")
    rate_unit = Column(String(20), default="kWh")
    
    schedule = relationship("TariffSchedule", back_populates="energy_slabs")

class CustomerChargeSlab(Base):
    __tablename__ = "customer_charge_slabs"
    
    id = Column(Integer, primary_key=True, index=True)
    schedule_id = Column(Integer, ForeignKey("tariff_schedules.id"), nullable=False)
    min_units = Column(Float, nullable=False)
    max_units = Column(Float, nullable=False)
    charge_amount = Column(Float, nullable=False) # Rs / month
    
    schedule = relationship("TariffSchedule", back_populates="customer_slabs")

class Bill(Base):
    __tablename__ = "bills"
    
    id = Column(Integer, primary_key=True, index=True)
    utility_id = Column(Integer, ForeignKey("utilities.id"), nullable=True)
    utility_code = Column(String(50), default="TGSPDCL", index=True)
    service_number = Column(String(100), index=True, nullable=True)
    consumer_name = Column(String(255), nullable=True)
    consumer_category = Column(String(50), default="LT-I Domestic")
    address = Column(Text, nullable=True)
    
    billing_month = Column(String(20), index=True, nullable=False) # YYYY-MM
    issue_date = Column(Date, nullable=True)
    due_date = Column(Date, nullable=True)
    billing_days = Column(Integer, default=30)
    
    previous_reading = Column(Float, nullable=True)
    current_reading = Column(Float, nullable=True)
    consumption_units = Column(Float, nullable=False, default=0.0)
    contracted_load_kw = Column(Float, default=1.0) # In kW
    recorded_demand_kw = Column(Float, nullable=True)
    
    printed_total = Column(Float, nullable=False, default=0.0)
    
    # Gruha Jyothi indicators
    is_gruha_jyothi = Column(Boolean, default=False)
    gruha_jyothi_eligible = Column(Boolean, default=False)
    ration_card_number = Column(String(100), nullable=True)
    
    # Document storage metadata
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), index=True, nullable=False)
    mime_type = Column(String(50), default="application/pdf")
    status = Column(String(50), default="UPLOADED") # UPLOADED, EXTRACTED, VERIFIED, CALCULATED
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    utility = relationship("Utility", back_populates="bills")
    extractions = relationship("BillExtraction", back_populates="bill", cascade="all, delete-orphan")
    charges = relationship("BillCharge", back_populates="bill", cascade="all, delete-orphan")
    calculation = relationship("CalculationResult", back_populates="bill", uselist=False, cascade="all, delete-orphan")
    anomalies = relationship("AnomalyReport", back_populates="bill", cascade="all, delete-orphan")

class BillExtraction(Base):
    __tablename__ = "bill_extractions"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    field_name = Column(String(100), nullable=False)
    raw_value = Column(String(255), nullable=True)
    confidence = Column(Float, default=1.0)
    page_number = Column(Integer, default=1)
    extraction_method = Column(String(50), default="DIGITAL_PDF") # DIGITAL_PDF, OCR, REGEX
    is_verified = Column(Boolean, default=False)
    user_override_value = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    bill = relationship("Bill", back_populates="extractions")

class BillCharge(Base):
    __tablename__ = "bill_charges"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    charge_type = Column(String(50), nullable=False) # ENERGY, CUSTOMER, FIXED, DUTY, FSA, TRUE_UP, ARREARS, ADJUSTMENTS, DPS, SUBSIDY, OTHER
    label = Column(String(100), nullable=False)
    printed_amount = Column(Float, default=0.0)
    computed_amount = Column(Float, nullable=True)
    difference = Column(Float, default=0.0)
    is_discrepant = Column(Boolean, default=False)
    explanation = Column(Text, nullable=True)
    
    bill = relationship("Bill", back_populates="charges")

class CalculationResult(Base):
    __tablename__ = "calculation_results"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    tariff_schedule_id = Column(Integer, ForeignKey("tariff_schedules.id"), nullable=True)
    
    computed_units = Column(Float, nullable=False)
    computed_energy_charge = Column(Float, default=0.0)
    computed_customer_charge = Column(Float, default=0.0)
    computed_fixed_charge = Column(Float, default=0.0)
    computed_duty = Column(Float, default=0.0)
    computed_fsa = Column(Float, default=0.0)
    computed_true_up = Column(Float, default=0.0)
    computed_subsidy = Column(Float, default=0.0)
    computed_total = Column(Float, default=0.0)
    printed_total = Column(Float, default=0.0)
    total_difference = Column(Float, default=0.0)
    
    status = Column(String(50), default="VERIFIED_MATCH") # VERIFIED_MATCH, DISCREPANCY_DETECTED, PENDING_VERIFICATION
    calculation_trace = Column(JSON, nullable=True)
    explanation_en = Column(Text, nullable=True)
    explanation_te = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    bill = relationship("Bill", back_populates="calculation")

class AnomalyReport(Base):
    __tablename__ = "anomaly_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=False)
    severity = Column(String(20), default="MEDIUM") # LOW, MEDIUM, HIGH, CRITICAL
    issue_type = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    legal_reference = Column(String(255), nullable=True)
    suggested_action = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    bill = relationship("Bill", back_populates="anomalies")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), index=True, nullable=False)
    bill_id = Column(Integer, ForeignKey("bills.id"), nullable=True)
    role = Column(String(20), nullable=False) # user, assistant
    content_en = Column(Text, nullable=False)
    content_te = Column(Text, nullable=True)
    grounded_context = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
