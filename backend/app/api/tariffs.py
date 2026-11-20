from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from backend.app.tariff_engine.rules_repository import (
    TARIFF_SCHEDULES, CUSTOMER_CHARGES_SLABS
)

router = APIRouter(prefix="/tariffs", tags=["Tariffs"])

class SimulateBillRequest(BaseModel):
    units: float = Field(..., ge=0, description="Monthly units consumed")
    contracted_load_kw: float = Field(1.0, ge=0.5, description="Contracted load in kW")
    billing_month: str = Field("2026-11", description="Billing month in YYYY-MM format")
    utility_code: str = Field("TGSPDCL", description="TGSPDCL or TGNPDCL")
    gruha_jyothi_eligible: bool = Field(False, description="Whether consumer has White Ration Card & Praja Palana")

@router.post("/simulate")
def simulate_bill(req: SimulateBillRequest):
    """
    Simulates instantaneous deterministic bill calculation for citizens without requiring a file upload.
    Calculates exact slabs, customer charges, fixed charges, electricity duty, True-Up, and Gruha Jyothi benefit.
    """
    from backend.app.tariff_engine.engine import TariffEngine
    result = TariffEngine.calculate({
        "consumption_units": req.units,
        "billing_month": req.billing_month,
        "utility_code": req.utility_code,
        "contracted_load_kw": req.contracted_load_kw,
        "gruha_jyothi_eligible": req.gruha_jyothi_eligible,
        "is_gruha_jyothi": req.gruha_jyothi_eligible and req.units <= 200.0,
        "printed_total": 0.0
    })
    return result

@router.get("")
def list_tariffs():
    """
    Returns all officially approved and versioned tariff schedules
    for TGSPDCL & TGNPDCL domestic consumers (FY 2023-24 to FY 2026-27).
    """
    schedules = []
    for fy, s in TARIFF_SCHEDULES.items():
        schedules.append({
            "financial_year": fy,
            "title": s["title"],
            "authority": s["authority"],
            "effective_from": str(s["effective_from"]),
            "effective_to": str(s["effective_to"]),
            "source_document": s["source_doc"],
            "source_clause": s["source_clause"],
            "fixed_charge_rate_normal": s["fixed_charge_rate_normal"],
            "fixed_charge_rate_high": s["fixed_charge_rate_high"],
            "duty_rate": s["duty_rate"],
            "slabs": s["slabs"]
        })
    return {
        "schedules": schedules,
        "customer_charges_slabs": [
            {"min_units": low, "max_units": high if high != float("inf") else "Above 800", "charge": charge}
            for low, high, charge in CUSTOMER_CHARGES_SLABS
        ],
        "true_up_rules": {
            "authority": "TGERC Order dated 05.10.2026",
            "commencement": "November 2026 CC bills",
            "rates": "Month 1 (Nov 2026): Rs. 0.30/unit; Month 2 onwards: Rs. 0.50/unit",
            "duration": "29 billing months for TGSPDCL, 26 billing months for TGNPDCL",
            "quantum": "1/12th annual past consumption"
        },
        "gruha_jyothi_rules": {
            "authority": "GoTS G.O.Ms.No.7 & TSERC Order dated 16.03.2024",
            "effective": "March 2024 onwards",
            "eligibility": "Domestic connection <= 200 units, White Ration Card linked with Aadhaar, Praja Palana registered",
            "benefit": "100% Zero Bill"
        }
    }

@router.get("/{version}")
def get_tariff_version(version: str):
    if version not in TARIFF_SCHEDULES:
        raise HTTPException(status_code=404, detail="Tariff version not found")
    s = TARIFF_SCHEDULES[version]
    return {
        "financial_year": version,
        "title": s["title"],
        "authority": s["authority"],
        "effective_from": str(s["effective_from"]),
        "effective_to": str(s["effective_to"]),
        "source_document": s["source_doc"],
        "source_clause": s["source_clause"],
        "slabs": s["slabs"],
        "customer_charges": CUSTOMER_CHARGES_SLABS
    }
