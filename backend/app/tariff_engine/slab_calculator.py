from typing import Dict, Any, List, Tuple
from backend.app.tariff_engine.rules_repository import get_customer_charge

def calculate_domestic_energy(units: float, schedule: Dict[str, Any]) -> Tuple[str, float, List[Dict[str, Any]]]:
    """
    Deterministically computes energy charges for Telangana LT-I Domestic consumers.
    Returns: (category, total_charge, itemized_slabs)
    """
    slabs_config = schedule["slabs"]
    breakdown = []
    total = 0.0

    if units <= 100.0:
        category = "LT-I(A)"
        active_slabs = slabs_config["LT-I(A)"]
    elif units <= 200.0:
        category = "LT-I(B)(i)"
        active_slabs = slabs_config["LT-I(B)(i)"]
    else:
        category = "LT-I(B)(ii)"
        active_slabs = slabs_config["LT-I(B)(ii)"]

    remaining_units = units
    previous_max = 0.0

    for slab in active_slabs:
        if remaining_units <= 0:
            break
        s_min = slab["min"]
        s_max = slab["max"]
        rate = slab["rate"]
        label = slab["label"]
        
        slab_span = s_max - s_min
        units_in_slab = min(remaining_units, slab_span)
        amount = round(units_in_slab * rate, 2)
        
        breakdown.append({
            "slab": label,
            "units": round(units_in_slab, 2),
            "rate": rate,
            "amount": amount
        })
        
        total += amount
        remaining_units -= units_in_slab

    return category, round(total, 2), breakdown

def calculate_fixed_charges(units: float, contracted_load_kw: float, schedule: Dict[str, Any]) -> float:
    """
    Calculates Fixed Charges.
    For LT-I Domestic:
    - In FY 2024-25, 2025-26, 2026-27: If units > 800, rate is Rs. 50/kW. Otherwise Rs. 10/kW.
    - Load minimum billing is 1 kW if unrecorded.
    """
    load = max(1.0, contracted_load_kw)
    if units > 800.0:
        rate = schedule.get("fixed_charge_rate_high", 50.0)
    else:
        rate = schedule.get("fixed_charge_rate_normal", 10.0)
    return round(load * rate, 2)

def calculate_electricity_duty(units: float, schedule: Dict[str, Any]) -> float:
    """
    Calculates Electricity Duty under Telangana State Electricity Duty Act, 1939.
    Rate: 6 paise per unit (Rs. 0.06 / kWh).
    """
    rate = schedule.get("duty_rate", 0.06)
    return round(units * rate, 2)

def calculate_dps(category: str, arrears: float = 0.0, days_delayed: int = 30) -> float:
    """
    Delayed Payment Surcharge (DPS) under TSERC/TGERC Retail Supply Tariff Orders:
    - LT-I(A): Flat Rs. 10.00 per month (if arrears > 0)
    - LT-I(B)(i), LT-I(B)(ii), LT-II(A/D), LT-IV, LT-V(B): Flat Rs. 25.00 per month (if arrears > 0)
    - LT-VI (PWS Schemes & Street Lights): 5 paise per Rs. 100 per day (0.05% per day, ~18.25% p.a.) on unpaid arrears.
    """
    if arrears <= 0.0:
        # If arrears is 0, DPS is 0. If arrears parameter was omitted (default 0), check if category lookup was requested
        return 0.0

    cat_upper = category.upper()
    if "LT-I(A)" in cat_upper:
        return 10.0
    elif "LT-I(B)" in cat_upper or "LT-II" in cat_upper or "LT-IV" in cat_upper or "LT-V" in cat_upper:
        return 25.0
    elif "LT-VI" in cat_upper or "PWS" in cat_upper or "PWW" in cat_upper or "STREET" in cat_upper:
        # 5 paise per Rs. 100 per day = (0.05 / 100) * arrears * days
        daily_rate = 0.05 / 100.0
        return round(arrears * daily_rate * days_delayed, 2)
    return 25.0
