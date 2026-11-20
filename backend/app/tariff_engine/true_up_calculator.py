import datetime
from typing import Optional, Dict, Any

COMMENCEMENT_DATE = datetime.date(2026, 11, 1)

def is_true_up_active(bill_date_or_month: Any) -> bool:
    """
    Checks if True-Up recovery is active for the given bill date.
    Per TGERC Order dated 05.10.2026, recovery commences with CC bills issued in November 2026.
    """
    if isinstance(bill_date_or_month, datetime.date):
        return bill_date_or_month >= COMMENCEMENT_DATE
    elif isinstance(bill_date_or_month, str):
        try:
            parts = bill_date_or_month.strip().split("-")
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 1
            b_date = datetime.date(year, month, 1)
            return b_date >= COMMENCEMENT_DATE
        except Exception:
            return False
    return False

def get_true_up_rate(bill_date_or_month: Any) -> float:
    """
    Per Clause 12(d) of Order dated 05.10.2026:
    - First month (November 2026): Rs. 0.30 per unit
    - Thereafter (December 2026 onwards): Rs. 0.50 per unit
    """
    year = 2026
    month = 11
    if isinstance(bill_date_or_month, datetime.date):
        year, month = bill_date_or_month.year, bill_date_or_month.month
    elif isinstance(bill_date_or_month, str):
        try:
            parts = bill_date_or_month.strip().split("-")
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 1
        except Exception:
            pass
            
    if year == 2026 and month == 11:
        return 0.30
    return 0.50

def calculate_true_up_charge(
    bill_date_or_month: Any,
    utility_code: str = "TGSPDCL",
    monthly_quantum_units: Optional[float] = None,
    past_yearly_consumption: Optional[float] = None
) -> Dict[str, Any]:
    """
    Computes statutory True-Up recovery per TGERC Order dated 05.10.2026.
    """
    active = is_true_up_active(bill_date_or_month)
    if not active:
        return {
            "is_applicable": False,
            "rate": 0.0,
            "quantum": 0.0,
            "amount": 0.0,
            "notes": "True-Up recovery only applies to bills issued from November 2026 onwards."
        }

    rate = get_true_up_rate(bill_date_or_month)
    
    # Duration per utility: TGSPDCL: 29 months, TGNPDCL: 26 months
    duration_months = 29 if utility_code.upper() == "TGSPDCL" else 26
    
    quantum = 0.0
    if monthly_quantum_units is not None and monthly_quantum_units > 0:
        quantum = monthly_quantum_units
    elif past_yearly_consumption is not None and past_yearly_consumption > 0:
        quantum = round(past_yearly_consumption / 12.0, 2)
        
    amount = round(quantum * rate, 2)
    
    return {
        "is_applicable": True,
        "rate": rate,
        "quantum": quantum,
        "amount": amount,
        "duration_months": duration_months,
        "legal_reference": "TGERC Order in O.P. Nos. 56-59 of 2025, dated 05.10.2026, Clause 12",
        "notes": f"Recovery rate: Rs. {rate}/unit on 1/12th average past consumption for {duration_months} billing months."
    }
