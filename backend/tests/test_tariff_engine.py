import pytest
from backend.app.tariff_engine.engine import TariffEngine
from backend.app.tariff_engine.slab_calculator import calculate_domestic_energy
from backend.app.tariff_engine.rules_repository import resolve_tariff_schedule, get_customer_charge
from backend.app.tariff_engine.true_up_calculator import is_true_up_active, get_true_up_rate

def test_lt_1a_energy_calculation():
    _, sched = resolve_tariff_schedule("2026-11")
    cat, total, slabs = calculate_domestic_energy(75.0, sched)
    assert cat == "LT-I(A)"
    assert total == 175.0 # (50 * 1.95 = 97.50) + (25 * 3.10 = 77.50)
    assert len(slabs) == 2

def test_lt_1b1_energy_calculation():
    _, sched = resolve_tariff_schedule("2026-11")
    cat, total, slabs = calculate_domestic_energy(150.0, sched)
    assert cat == "LT-I(B)(i)"
    assert total == 580.0 # (100 * 3.40 = 340) + (50 * 4.80 = 240)
    assert len(slabs) == 2

def test_lt_1b2_energy_calculation():
    _, sched = resolve_tariff_schedule("2026-11")
    cat, total, slabs = calculate_domestic_energy(250.0, sched)
    assert cat == "LT-I(B)(ii)"
    assert total == 1405.0 # (200 * 5.10 = 1020) + (50 * 7.70 = 385)
    assert len(slabs) == 2

def test_customer_charges():
    assert get_customer_charge(45.0) == 40.0
    assert get_customer_charge(80.0) == 70.0
    assert get_customer_charge(150.0) == 90.0
    assert get_customer_charge(250.0) == 100.0
    assert get_customer_charge(350.0) == 120.0
    assert get_customer_charge(600.0) == 140.0
    assert get_customer_charge(900.0) == 160.0

def test_gruha_jyothi_zero_bill():
    bill_data = {
        "consumption_units": 150.0,
        "billing_month": "2024-05",
        "contracted_load_kw": 1.0,
        "gruha_jyothi_eligible": True,
        "printed_total": 0.0
    }
    result = TariffEngine.calculate(bill_data)
    # Energy: 580, CC: 90, FC: 10, ED: 9. Total = 689. Subsidy = 689. Net = 0.
    assert result["subsidies"] == 689.0
    assert result["computed_total"] == 0.0
    assert "జీరో బిల్లు" in result["explanation_te"]

def test_gruha_jyothi_cliff_overconsumption():
    bill_data = {
        "consumption_units": 205.0,
        "billing_month": "2024-05",
        "contracted_load_kw": 1.0,
        "gruha_jyothi_eligible": True,
        "printed_total": 1180.8
    }
    result = TariffEngine.calculate(bill_data)
    # Exceeding 200 units disqualifies for Gruha Jyothi zero bill
    assert result["subsidies"] == 0.0
    assert result["computed_total"] > 1000.0
    # Must contain anomaly alert
    anomaly_types = [a["issue_type"] for a in result["anomalies"]]
    assert "GRUHA_JYOTHI_CLIFF_EXCEEDED" in anomaly_types

def test_true_up_recovery_rates():
    assert is_true_up_active("2026-10") == False
    assert is_true_up_active("2026-11") == True
    assert get_true_up_rate("2026-11") == 0.30
    assert get_true_up_rate("2026-12") == 0.50

def test_discrepancy_detection():
    bill_data = {
        "consumption_units": 100.0,
        "billing_month": "2026-11",
        "contracted_load_kw": 1.0,
        "printed_total": 500.0 # Intentionally wrong printed total
    }
    result = TariffEngine.calculate(bill_data)
    assert result["status"] == "DISCREPANCY_DETECTED"
    assert len(result["anomalies"]) > 0
    assert result["anomalies"][0]["issue_type"] in ["ARITHMETIC_TOTAL_MISMATCH", "OVERCHARGE_DISCREPANCY"]


def test_lt_6b_pws_and_defective_meter_anomaly():
    bill_data = {
        "consumption_units": 18815252.0,
        "billing_month": "2023-02",
        "contracted_load_kw": 5.0,
        "consumer_category": "LT-VI(B) PWS Schemes (Panchayats)",
        "printed_total": 114163672.0,
        "previous_reading": 2101.0,
        "current_reading": 18817352.0,
        "historical_average_units": 18227.0,
        "last_paid_amount": 3257.0,
        "printed_arrears": 141460.61,
        "printed_adjustments": 1509.40
    }
    result = TariffEngine.calculate(bill_data)
    
    assert result["status"] == "CRITICAL_ANOMALY_DETECTED"
    assert result["tariff_version"] == "FY 2022-23"
    assert result["category_determined"] == "LT-VI(B) PWS Schemes (Panchayats)"
    # Energy: 18815252 * 6.00 = 112891512.0
    assert result["energy_charges"] == 112891512.0
    # Fixed charge: 5 HP * 32.0 = 160.0
    assert result["fixed_charges"] == 160.0
    # Customer charge: 120.0
    assert result["customer_charges"] == 120.0
    # Electricity duty: 18815252 * 0.06 = 1128915.12
    assert result["electricity_duty"] == 1128915.12
    # Check anomaly
    anomaly_types = [a["issue_type"] for a in result["anomalies"]]
    assert "DEFECTIVE_METER_OR_ROLLOVER_ANOMALY" in anomaly_types
    # Check revised bill based on 3-month average (18227 units)
    assert result["rectified_bill_estimate"] == 110735.62
    # Check overcharge amount strictly computed on current charges (114,020,707.12 - 110,735.62 = 113,909,971.50)
    assert result["overcharge_amount"] == 113909971.50
    # Check bilingual legal citations
    assert "TGERC Regulation 04 of 2026" in result["explanation_en"]
    assert "18%" in result["explanation_en"]
    assert "18%" in result["explanation_te"]


def test_gruha_jyothi_historical_2023_no_subsidy():
    """Bill 1 Audit Point: Gruha Jyothi launched 26.02.2024; pre-March 2024 bills get 0 subsidy."""
    bill_data = {
        "consumption_units": 180.0,
        "contracted_load_kw": 1.0,
        "billing_month": "2023-03",
        "consumer_category": "LT-I Domestic",
        "printed_total": 734.0,
        "gruha_jyothi_eligible": True
    }
    result = TariffEngine.calculate(bill_data)
    assert result["subsidies"] == 0.0
    assert result["current_charges_subtotal"] == 834.80
    assert result["computed_total"] == 834.80
    # Printed 734 vs computed 834.80 => underbilled by 100.80, NOT overcharged!
    assert result["status"] == "UNDERBILLED_DETECTED"
    assert "UNDERBILLED_OR_UNBILLED_COMPONENTS" in [a["issue_type"] for a in result["anomalies"]]
    assert "OVERCHARGE_DISCREPANCY" not in [a["issue_type"] for a in result["anomalies"]]


def test_gruha_jyothi_post_march_2024_zero_bill():
    """Gruha Jyothi on 2024-04 bill <= 200 units grants 100% subsidy on current charges."""
    bill_data = {
        "consumption_units": 180.0,
        "contracted_load_kw": 1.0,
        "billing_month": "2024-04",
        "consumer_category": "LT-I Domestic",
        "printed_total": 0.0,
        "gruha_jyothi_eligible": True
    }
    result = TariffEngine.calculate(bill_data)
    assert result["subsidies"] == 834.80
    assert result["computed_total"] == 0.0
    assert "Zero Bill" in result["explanation_en"]


def test_gruha_jyothi_does_not_subsidize_prior_arrears():
    """Audit Point: Prior arrears must remain payable; subsidy covers only current month charges."""
    bill_data = {
        "consumption_units": 180.0,
        "contracted_load_kw": 1.0,
        "billing_month": "2024-04",
        "consumer_category": "LT-I Domestic",
        "printed_arrears": 2023.00,
        "gruha_jyothi_eligible": True
    }
    result = TariffEngine.calculate(bill_data)
    # Current charges = 834.80 subsidized
    assert result["subsidies"] == 834.80
    # Net payable = 2023.00 (arrears are NOT waived)
    assert result["computed_total"] == 2023.00
    assert "2023.00" in result["explanation_en"]


def test_domestic_fixed_charges_above_800_units():
    """Audit Point: Domestic fixed charges jump from Rs 10/kW to Rs 50/kW when units > 800."""
    from backend.app.tariff_engine.rules_repository import resolve_tariff_schedule
    from backend.app.tariff_engine.slab_calculator import calculate_fixed_charges
    _, sched = resolve_tariff_schedule("2026-11")
    fc_800 = calculate_fixed_charges(800.0, 2.0, sched)
    fc_801 = calculate_fixed_charges(801.0, 2.0, sched)
    assert fc_800 == 20.0 # 2 kW * 10
    assert fc_801 == 100.0 # 2 kW * 50
