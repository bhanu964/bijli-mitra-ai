import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import settings
from backend.app.core.database import engine, Base, SessionLocal
from backend.app.models.models import Utility, Bill, CalculationResult
from backend.app.api import bills, tariffs, analytics, chat
from backend.app.tariff_engine.engine import TariffEngine

# Create all database tables
Base.metadata.create_all(bind=engine)

def seed_initial_demo_data():
    """
    Seeds initial realistic demonstration bills for Telangana consumers
    (e.g., historical progression from Summer to Winter, Gruha Jyothi Zero Bill,
    and a November 2026 bill reflecting TGERC True-Up recovery).
    """
    db = SessionLocal()
    try:
        # Seed Utilities
        u_spdcl = db.query(Utility).filter(Utility.code == "TGSPDCL").first()
        if not u_spdcl:
            u_spdcl = Utility(
                code="TGSPDCL",
                name="Southern Power Distribution Company of Telangana Limited",
                state="Telangana",
                headquarters="Hyderabad"
            )
            db.add(u_spdcl)
            
        u_npdcl = db.query(Utility).filter(Utility.code == "TGNPDCL").first()
        if not u_npdcl:
            u_npdcl = Utility(
                code="TGNPDCL",
                name="Northern Power Distribution Company of Telangana Limited",
                state="Telangana",
                headquarters="Warangal"
            )
            db.add(u_npdcl)
        db.commit()

        # Seed initial bills if none exist
        bill_count = db.query(Bill).count()
        if bill_count == 0:
            demo_bills = [
                {
                    "utility_code": "TGSPDCL",
                    "service_number": "1002348911",
                    "consumer_name": "K. Venkata Raman",
                    "billing_month": "2026-07",
                    "units": 240.0,
                    "load": 2.0,
                    "is_gj": False,
                    "file_name": "TGSPDCL_July_2026.pdf"
                },
                {
                    "utility_code": "TGSPDCL",
                    "service_number": "1002348911",
                    "consumer_name": "K. Venkata Raman",
                    "billing_month": "2026-08",
                    "units": 210.0,
                    "load": 2.0,
                    "is_gj": False,
                    "file_name": "TGSPDCL_Aug_2026.pdf"
                },
                {
                    "utility_code": "TGSPDCL",
                    "service_number": "1002348911",
                    "consumer_name": "K. Venkata Raman",
                    "billing_month": "2026-09",
                    "units": 180.0,
                    "load": 2.0,
                    "is_gj": True, # Gruha Jyothi zero bill
                    "file_name": "TGSPDCL_Sep_2026_GruhaJyothi.pdf"
                },
                {
                    "utility_code": "TGSPDCL",
                    "service_number": "1002348911",
                    "consumer_name": "K. Venkata Raman",
                    "billing_month": "2026-10",
                    "units": 140.0,
                    "load": 2.0,
                    "is_gj": True, # Gruha Jyothi zero bill
                    "file_name": "TGSPDCL_Oct_2026_GruhaJyothi.pdf"
                },
                {
                    "utility_code": "TGSPDCL",
                    "service_number": "1002348911",
                    "consumer_name": "K. Venkata Raman",
                    "billing_month": "2026-11",
                    "units": 160.0,
                    "load": 2.0,
                    "is_gj": False, # Non-GJ with True-Up
                    "file_name": "TGSPDCL_Nov_2026_TrueUp.pdf"
                }
            ]
            
            for b_spec in demo_bills:
                # Calculate correct amounts using TariffEngine
                calc_res = TariffEngine.calculate({
                    "consumption_units": b_spec["units"],
                    "billing_month": b_spec["billing_month"],
                    "utility_code": b_spec["utility_code"],
                    "contracted_load_kw": b_spec["load"],
                    "gruha_jyothi_eligible": b_spec["is_gj"],
                    "printed_total": 0.0
                })
                
                dummy_hash = f"demo_hash_{b_spec['billing_month']}"
                b_rec = Bill(
                    utility_code=b_spec["utility_code"],
                    service_number=b_spec["service_number"],
                    consumer_name=b_spec["consumer_name"],
                    consumer_category="LT-I Domestic",
                    billing_month=b_spec["billing_month"],
                    consumption_units=b_spec["units"],
                    contracted_load_kw=b_spec["load"],
                    printed_total=calc_res["computed_total"],
                    is_gruha_jyothi=b_spec["is_gj"],
                    gruha_jyothi_eligible=b_spec["is_gj"],
                    file_name=b_spec["file_name"],
                    file_path=os.path.join(settings.UPLOAD_DIR, b_spec["file_name"]),
                    file_hash=dummy_hash,
                    status="CALCULATED"
                )
                db.add(b_rec)
                db.flush()
                
                # Attach calculation result
                c_rec = CalculationResult(
                    bill_id=b_rec.id,
                    computed_units=calc_res["consumption_units"],
                    computed_energy_charge=calc_res["energy_charges"],
                    computed_customer_charge=calc_res["customer_charges"],
                    computed_fixed_charge=calc_res["fixed_charges"],
                    computed_duty=calc_res["electricity_duty"],
                    computed_fsa=calc_res["fsa_charges"],
                    computed_true_up=calc_res["true_up_charges"],
                    computed_subsidy=calc_res["subsidies"],
                    computed_total=calc_res["computed_total"],
                    printed_total=calc_res["computed_total"],
                    total_difference=0.0,
                    status=calc_res["status"],
                    calculation_trace=calc_res,
                    explanation_en=calc_res["explanation_en"],
                    explanation_te=calc_res["explanation_te"]
                )
                db.add(c_rec)
            db.commit()
    finally:
        db.close()

# Also run seed now so DB is immediately ready
seed_initial_demo_data()

@asynccontextmanager
async def lifespan(app: FastAPI):
    seed_initial_demo_data()
    yield

app = FastAPI(
    title="BIJLI MITRA AI — Telangana Personalized Billing Assistance API",
    description="Official API for Telangana Government Challenge 13: Deterministic electricity tariff calculation, bill OCR, bilingual explanations, and anomaly detection.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(bills.router, prefix=settings.API_V1_STR)
app.include_router(tariffs.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(chat.router, prefix=settings.API_V1_STR)

# Health Check
@app.get("/api/health", tags=["System"])
def health_check():
    return {
        "status": "HEALTHY",
        "service": "BIJLI MITRA AI Backend",
        "version": "1.0.0",
        "jurisdiction": "Telangana Electricity Regulatory Commission (TGERC)",
        "utilities_supported": ["TGSPDCL", "TGNPDCL"]
    }

