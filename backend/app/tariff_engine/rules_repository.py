import datetime
from typing import Dict, Any, Optional

TARIFF_SCHEDULES = {
    "FY 2022-23": {
        "title": "Abstract of Retail Supply Tariffs for FY 2022-23",
        "authority": "TSERC",
        "effective_from": datetime.date(2022, 4, 1),
        "effective_to": datetime.date(2023, 3, 31),
        "source_doc": "RST Order for FY 2022-23.pdf",
        "source_clause": "Page 1 Table LT-I, Table LT-VI & Conditions",
        "fixed_charge_rate_normal": 10.0,
        "fixed_charge_rate_high": 10.0,
        "duty_rate": 0.06,
        "slabs": {
            "LT-I(A)": [
                {"min": 0, "max": 50, "rate": 1.95, "label": "0-50 units"},
                {"min": 50, "max": 100, "rate": 3.10, "label": "51-100 units"}
            ],
            "LT-I(B)(i)": [
                {"min": 0, "max": 100, "rate": 3.40, "label": "0-100 units"},
                {"min": 100, "max": 200, "rate": 4.80, "label": "101-200 units"}
            ],
            "LT-I(B)(ii)": [
                {"min": 0, "max": 200, "rate": 5.10, "label": "0-200 units"},
                {"min": 200, "max": 300, "rate": 7.70, "label": "201-300 units"},
                {"min": 300, "max": 400, "rate": 9.00, "label": "301-400 units"},
                {"min": 400, "max": 800, "rate": 9.50, "label": "401-800 units"},
                {"min": 800, "max": 999999, "rate": 10.00, "label": "Above 800 units"}
            ]
        }
    },
    "FY 2023-24": {
        "title": "Abstract of Retail Supply Tariffs for FY 2023-24",
        "authority": "TSERC",
        "effective_from": datetime.date(2023, 4, 1),
        "effective_to": datetime.date(2024, 3, 31),
        "source_doc": "OFFICIAL_TARIFF_ORDERS/Tariff Schedule -RST FY 2023-24.pdf",
        "source_clause": "Page 1 Table LT-I & Page 7 Clause 8",
        "fixed_charge_rate_normal": 10.0,
        "fixed_charge_rate_high": 10.0, # All slabs were 10 in FY 23-24
        "duty_rate": 0.06,
        "slabs": {
            "LT-I(A)": [
                {"min": 0, "max": 50, "rate": 1.95, "label": "0-50 units"},
                {"min": 50, "max": 100, "rate": 3.10, "label": "51-100 units"}
            ],
            "LT-I(B)(i)": [
                {"min": 0, "max": 100, "rate": 3.40, "label": "0-100 units"},
                {"min": 100, "max": 200, "rate": 4.80, "label": "101-200 units"}
            ],
            "LT-I(B)(ii)": [
                {"min": 0, "max": 200, "rate": 5.10, "label": "0-200 units"},
                {"min": 200, "max": 300, "rate": 7.70, "label": "201-300 units"},
                {"min": 300, "max": 400, "rate": 9.00, "label": "301-400 units"},
                {"min": 400, "max": 800, "rate": 9.50, "label": "401-800 units"},
                {"min": 800, "max": 999999, "rate": 10.00, "label": "Above 800 units"}
            ]
        }
    },
    "FY 2024-25": {
        "title": "Abstract of Retail Supply Tariff for FY 2024-25 (Appendix-A)",
        "authority": "TGERC",
        "effective_from": datetime.date(2024, 11, 1),
        "effective_to": datetime.date(2025, 3, 31),
        "source_doc": "OFFICIAL_TARIFF_ORDERS/RST Schedule for FY 2024-25.pdf",
        "source_clause": "Page 1 Table LT-I & Page 6 Clause 7",
        "fixed_charge_rate_normal": 10.0,
        "fixed_charge_rate_high": 50.0, # >800 units increased to 50
        "duty_rate": 0.06,
        "slabs": {
            "LT-I(A)": [
                {"min": 0, "max": 50, "rate": 1.95, "label": "0-50 units"},
                {"min": 50, "max": 100, "rate": 3.10, "label": "51-100 units"}
            ],
            "LT-I(B)(i)": [
                {"min": 0, "max": 100, "rate": 3.40, "label": "0-100 units"},
                {"min": 100, "max": 200, "rate": 4.80, "label": "101-200 units"}
            ],
            "LT-I(B)(ii)": [
                {"min": 0, "max": 200, "rate": 5.10, "label": "0-200 units"},
                {"min": 200, "max": 300, "rate": 7.70, "label": "201-300 units"},
                {"min": 300, "max": 400, "rate": 9.00, "label": "301-400 units"},
                {"min": 400, "max": 800, "rate": 9.50, "label": "401-800 units"},
                {"min": 800, "max": 999999, "rate": 10.00, "label": "Above 800 units"}
            ]
        }
    },
    "FY 2025-26": {
        "title": "Abstract of Retail Supply Tariff for FY 2025-26 (Appendix A)",
        "authority": "TGERC",
        "effective_from": datetime.date(2025, 5, 1),
        "effective_to": datetime.date(2026, 3, 31),
        "source_doc": "OFFICIAL_TARIFF_ORDERS/RST Schedule for FY 2025-26.pdf",
        "source_clause": "Page 1 Appendix A & Page 6 Clause 7",
        "fixed_charge_rate_normal": 10.0,
        "fixed_charge_rate_high": 50.0,
        "duty_rate": 0.06,
        "slabs": {
            "LT-I(A)": [
                {"min": 0, "max": 50, "rate": 1.95, "label": "0-50 units"},
                {"min": 50, "max": 100, "rate": 3.10, "label": "51-100 units"}
            ],
            "LT-I(B)(i)": [
                {"min": 0, "max": 100, "rate": 3.40, "label": "0-100 units"},
                {"min": 100, "max": 200, "rate": 4.80, "label": "101-200 units"}
            ],
            "LT-I(B)(ii)": [
                {"min": 0, "max": 200, "rate": 5.10, "label": "0-200 units"},
                {"min": 200, "max": 300, "rate": 7.70, "label": "201-300 units"},
                {"min": 300, "max": 400, "rate": 9.00, "label": "301-400 units"},
                {"min": 400, "max": 800, "rate": 9.50, "label": "401-800 units"},
                {"min": 800, "max": 999999, "rate": 10.00, "label": "Above 800 units"}
            ]
        }
    },
    "FY 2026-27": {
        "title": "Abstract of Retail Supply Tariff for FY 2026-27 (Appendix A)",
        "authority": "TGERC",
        "effective_from": datetime.date(2026, 4, 1),
        "effective_to": datetime.date(2027, 3, 31),
        "source_doc": "Tariff Schedule 2026-27.pdf",
        "source_clause": "Page 1 Appendix A & Page 6 Clause 7",
        "fixed_charge_rate_normal": 10.0,
        "fixed_charge_rate_high": 50.0,
        "duty_rate": 0.06,
        "slabs": {
            "LT-I(A)": [
                {"min": 0, "max": 50, "rate": 1.95, "label": "0-50 units"},
                {"min": 50, "max": 100, "rate": 3.10, "label": "51-100 units"}
            ],
            "LT-I(B)(i)": [
                {"min": 0, "max": 100, "rate": 3.40, "label": "0-100 units"},
                {"min": 100, "max": 200, "rate": 4.80, "label": "101-200 units"}
            ],
            "LT-I(B)(ii)": [
                {"min": 0, "max": 200, "rate": 5.10, "label": "0-200 units"},
                {"min": 200, "max": 300, "rate": 7.70, "label": "201-300 units"},
                {"min": 300, "max": 400, "rate": 9.00, "label": "301-400 units"},
                {"min": 400, "max": 800, "rate": 9.50, "label": "401-800 units"},
                {"min": 800, "max": 999999, "rate": 10.00, "label": "Above 800 units"}
            ]
        }
    }
}

# TGERC LT-VI Tariff Schedule: Street Lighting & PWS Schemes
LT_VI_TARIFFS = {
    "LT-VI(A)": {
        "name": "Street Lighting",
        "Panchayats": {"energy_rate": 7.10, "fixed_rate": 32.0, "unit": "kW"},
        "Municipalities": {"energy_rate": 7.60, "fixed_rate": 32.0, "unit": "kW"},
        "Corporations": {"energy_rate": 8.10, "fixed_rate": 32.0, "unit": "kW"}
    },
    "LT-VI(B)": {
        "name": "PWS Schemes (Public Water Works)",
        "Panchayats": {"energy_rate": 6.00, "fixed_rate": 32.0, "min_fixed": 50.0, "unit": "HP"},
        "Municipalities": {"energy_rate": 7.00, "fixed_rate": 32.0, "min_fixed": 50.0, "unit": "HP"},
        "Corporations": {"energy_rate": 7.50, "fixed_rate": 32.0, "min_fixed": 50.0, "unit": "HP"}
    },
    "customer_charge": 120.0, # Rs. 120/month per TGERC Table
    "duty_rate": 0.06 # 6 paise/unit
}

CUSTOMER_CHARGES_SLABS = [
    (0, 50, 40.0),
    (50, 100, 70.0),
    (100, 200, 90.0),
    (200, 300, 100.0),
    (300, 400, 120.0),
    (400, 800, 140.0),
    (800, 999999, 160.0)
]

def get_customer_charge(units: float) -> float:
    for low, high, charge in CUSTOMER_CHARGES_SLABS:
        if low <= units <= high or (low < units <= high):
            return charge
    return 160.0

def resolve_tariff_schedule(bill_date_or_month: Any) -> tuple[str, Dict[str, Any]]:
    """
    Resolves the appropriate tariff schedule based on bill date or YYYY-MM string.
    """
    ref_date = None
    if isinstance(bill_date_or_month, datetime.date):
        ref_date = bill_date_or_month
    elif isinstance(bill_date_or_month, str):
        parts = bill_date_or_month.strip().split("-")
        try:
            year = int(parts[0])
            month = int(parts[1]) if len(parts) > 1 else 1
            day = int(parts[2]) if len(parts) > 2 else 15
            ref_date = datetime.date(year, month, day)
        except Exception:
            ref_date = datetime.date(2026, 11, 1)
    else:
        ref_date = datetime.date(2026, 11, 1)

    for fy, sched in sorted(TARIFF_SCHEDULES.items(), key=lambda x: x[1]["effective_from"], reverse=True):
        if sched["effective_from"] <= ref_date <= sched["effective_to"]:
            return fy, sched

    # Fallback by year boundary
    if ref_date >= datetime.date(2026, 4, 1):
        return "FY 2026-27", TARIFF_SCHEDULES["FY 2026-27"]
    elif ref_date >= datetime.date(2025, 4, 1):
        return "FY 2025-26", TARIFF_SCHEDULES["FY 2025-26"]
    elif ref_date >= datetime.date(2024, 4, 1):
        return "FY 2024-25", TARIFF_SCHEDULES["FY 2024-25"]
    elif ref_date >= datetime.date(2023, 4, 1):
        return "FY 2023-24", TARIFF_SCHEDULES["FY 2023-24"]
    else:
        return "FY 2022-23", TARIFF_SCHEDULES["FY 2022-23"]
