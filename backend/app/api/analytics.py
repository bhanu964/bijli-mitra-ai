from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db
from backend.app.models.models import Bill
from backend.app.schemas.schemas import AnalyticsSummarySchema
from backend.app.analytics.consumption_tracker import ConsumptionTracker
from backend.app.analytics.savings_advisor import SavingsAdvisor

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/summary", response_model=AnalyticsSummarySchema)
def get_analytics_summary(db: Session = Depends(get_db)):
    bills = db.query(Bill).all()
    bills_data = []
    for b in bills:
        calc_status = b.calculation.status if b.calculation else "PENDING"
        bills_data.append({
            "billing_month": b.billing_month,
            "consumption_units": b.consumption_units,
            "printed_total": b.printed_total,
            "computed_total": b.calculation.computed_total if b.calculation else b.printed_total,
            "is_gruha_jyothi": b.is_gruha_jyothi,
            "status": calc_status,
            "has_discrepancy": calc_status == "DISCREPANCY_DETECTED"
        })
    summary = ConsumptionTracker.calculate_summary(bills_data)
    return AnalyticsSummarySchema(**summary)

@router.get("/savings/{bill_id}")
def get_bill_savings(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    recs = SavingsAdvisor.generate_recommendations(
        units=bill.consumption_units,
        is_gruha_jyothi=bill.is_gruha_jyothi or bill.gruha_jyothi_eligible,
        current_bill_amount=bill.printed_total
    )
    return {
        "bill_id": bill.id,
        "units": bill.consumption_units,
        "is_gruha_jyothi": bill.is_gruha_jyothi or bill.gruha_jyothi_eligible,
        "recommendations": recs
    }
