import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "HEALTHY"
    assert "TGSPDCL" in data["utilities_supported"]

def test_get_tariffs():
    res = client.get("/api/tariffs")
    assert res.status_code == 200
    data = res.json()
    assert "schedules" in data
    assert len(data["schedules"]) >= 4

def test_simulate_bill():
    payload = {
        "units": 180.0,
        "contracted_load_kw": 2.0,
        "billing_month": "2026-11",
        "utility_code": "TGSPDCL",
        "gruha_jyothi_eligible": True
    }
    res = client.post("/api/tariffs/simulate", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["consumption_units"] == 180.0
    assert data["subsidies"] > 0
    assert data["computed_total"] == 0.0 # Zero bill under Gruha Jyothi!
    assert len(data["energy_slabs"]) > 0
    assert "customer_charges" in data

def test_list_bills():
    res = client.get("/api/bills")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) >= 1

def test_analytics_summary():
    res = client.get("/api/analytics/summary")
    assert res.status_code == 200
    data = res.json()
    assert "total_bills_analyzed" in data
    assert data["total_bills_analyzed"] >= 1
    assert "monthly_trend" in data

def test_chat_assistant():
    payload = {
        "message": "Why is there a True-Up charge on my bill?",
        "language": "en"
    }
    res = client.post("/api/chat", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "05.10.2026" in data["reply_en"]
    assert "reply_te" in data
    assert len(data["grounded_facts"]) > 0

def test_bill_calculation_lifecycle():
    # 1. Get first bill
    bills = client.get("/api/bills").json()
    assert len(bills) > 0
    bill_id = bills[0]["id"]
    
    # 2. Get bill details
    b_detail = client.get(f"/api/bills/{bill_id}")
    assert b_detail.status_code == 200
    
    # 3. Verify / update bill
    verify_payload = {
        "utility_code": "TGSPDCL",
        "service_number": "1002348911",
        "consumer_name": "K. Venkata Raman",
        "consumer_category": "LT-I Domestic",
        "billing_month": "2026-11",
        "consumption_units": 150.0,
        "contracted_load_kw": 1.0,
        "printed_total": 689.0,
        "is_gruha_jyothi": False,
        "gruha_jyothi_eligible": False
    }
    v_res = client.put(f"/api/bills/{bill_id}/verify", json=verify_payload)
    assert v_res.status_code == 200
    
    # 4. Calculate
    calc_res = client.post(f"/api/bills/{bill_id}/calculate")
    assert calc_res.status_code == 200
    c_data = calc_res.json()
    assert c_data["category_determined"] == "LT-I(B)(i)"
    assert c_data["energy_charges"] == 580.0
    assert c_data["customer_charges"] == 90.0
    assert c_data["status"] == "VERIFIED_MATCH"
