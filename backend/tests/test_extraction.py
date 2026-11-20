import pytest
from backend.app.extraction.parser import BillParser

def test_bill_parser_tgspdcl():
    sample_text = """
    SOUTHERN POWER DISTRIBUTION COMPANY OF TELANGANA LIMITED (TGSPDCL)
    ELECTRICITY BILL FOR DOMESTIC (LT-I) SUPPLY
    USC NO: 1004589211   Bill Month: Nov-2026
    Name: S. K. Narayana Rao
    Address: Plot 42, Jubilee Hills, Hyderabad
    Load: 2.0 KW   Category: LT-I Domestic
    Previous Reading: 12450   Current Reading: 12630
    Billed Units: 180
    Energy Charges: Rs. 689.00
    Customer Charges: Rs. 90.00
    Electricity Duty: Rs. 10.80
    Fixed Charges: Rs. 20.00
    True-Up Recovery: Rs. 54.00
    Net Payable: Rs. 863.80
    Due Date: 25-11-2026
    """
    pages_data = [{"page_number": 1, "text": sample_text}]
    extracted = BillParser.parse_text(pages_data)
    
    assert extracted["utility_code"]["value"] == "TGSPDCL"
    assert extracted["service_number"]["value"] == "1004589211"
    assert extracted["consumer_name"]["value"] == "S. K. Narayana Rao"
    assert extracted["billing_month"]["value"] == "2026-11"
    assert extracted["consumption_units"]["value"] == 180.0
    assert extracted["contracted_load_kw"]["value"] == 2.0
    assert extracted["printed_total"]["value"] == 863.80

def test_bill_parser_gruha_jyothi():
    sample_text = """
    TELANGANA STATE POWER DISTRIBUTION
    ELECTRICITY BILL - PRAJA PALANA / GRUHA JYOTHI BENEFICIARY
    SC NO: 99887766
    Consumer: M. Lakshmi
    Units Consumed: 120
    Current Bill Amount: Rs. 545.00
    Govt Subsidy: Rs. 545.00
    Net Amount Payable: Rs. 0.00
    """
    pages_data = [{"page_number": 1, "text": sample_text}]
    extracted = BillParser.parse_text(pages_data)
    
    assert extracted["consumption_units"]["value"] == 120.0
    assert extracted["is_gruha_jyothi"]["value"] == True
    assert extracted["printed_total"]["value"] == 0.0

def test_bill_parser_thermal_receipt_tsnpdcl_pww():
    sample_text = """
    TSNPDCL ELECTRICITY BILL-CUM NOTICE
    Ir Ver-0.96 BNo: 0002
    SBM ID:D7204I22
    ERO :3221 SEC:38
    GRP :M CYCLE:M1
    DT:03-02-2023 TIME:10:36
    USCNO: 13164173
    SCNO: 3801 02321
    NAME: G P WATER WORKS
    ADDR: W W MACHAREDDY
    CAT: 6B PWW
    LD: 5.00 PH:3
    PS: 18817352 03/02/2023 0
    PV: 2101 02/01/2023 01
    KWH UNITS: 18815252
    UNITS: 18815252 AVG: 18227
    ENERGYCHARGES: 112891504
    FIXED CHARGES: 160.00
    CUST CHARGES : 120.00
    ED : 1128915.1
    TOTAL AMOUNT : 114022208
    AFTER: 01-04-22: 141460.61
    NET AMOUNT : 114163672
    LAST PAID AMT: 3257.00
    www.tsnpdcl.in
    """
    pages_data = [{"page_number": 1, "text": sample_text}]
    extracted = BillParser.parse_text(pages_data)
    
    assert extracted["utility_code"]["value"] == "TGNPDCL"
    assert "13164173" in extracted["service_number"]["value"] or "3801" in extracted["service_number"]["value"]
    assert extracted["consumer_name"]["value"] == "G P WATER WORKS"
    assert extracted["consumer_category"]["value"] == "LT-VI(B) PWS Schemes (Panchayats)"
    assert extracted["billing_month"]["value"] == "2023-02"
    assert extracted["consumption_units"]["value"] == 18815252.0
    assert extracted["contracted_load_kw"]["value"] == 5.0
    assert extracted["printed_energy_charges"]["value"] == 112891504.0
    assert extracted["printed_fixed_charges"]["value"] == 160.0
    assert extracted["printed_customer_charges"]["value"] == 120.0
    assert extracted["printed_electricity_duty"]["value"] == 1128915.1
    assert extracted["printed_total"]["value"] == 114163672.0
    assert extracted["historical_average_units"]["value"] == 18227.0
    assert extracted["last_paid_amount"]["value"] == 3257.00

def test_image_ocr_end_to_end_on_user_thermal_receipt():
    import os
    from backend.app.extraction.image_ocr import ImageOCR
    img_path = "/Users/bhanuprasad/.gemini/antigravity/brain/5160f34c-53a3-4143-9054-658d8ee65044/.user_uploaded/media_1795002125597_c441b43b.jpg"
    if os.path.exists(img_path):
        res = ImageOCR.ocr_image_file(img_path)
        parsed = BillParser.parse_text([res])
        assert parsed["utility_code"]["value"] == "TGNPDCL"
        assert parsed["service_number"]["value"] == "13164173"
        assert parsed["consumer_name"]["value"] == "G P WATER WORKS"
        assert parsed["consumer_category"]["value"] == "LT-VI(B) PWS Schemes (Panchayats)"
        assert parsed["billing_month"]["value"] == "2023-02"
        assert parsed["consumption_units"]["value"] == 18815252.0
        assert parsed["contracted_load_kw"]["value"] == 5.0
        assert parsed["printed_total"]["value"] == 114163672.0


def test_parser_arrears_no_year_leakage():
    """Verify that dates like 01-04-2023 or 01-04-22 do not leak into arrears as 2023.00."""
    sample_text = """
    TGSPDCL ELECTRICITY BILL
    SCNO: 1002348911
    NAME: RAMA RAO
    CAT: LT-I(B)(i)
    MONTH: 2023-03
    UNITS: 180
    ENERGY CHARGES: 724.00
    FIXED CHARGES: 10.00
    CUST CHARGES: 90.00
    ED: 10.80
    AS ON: 01-04-2023: 0.00
    AFTER: 01-04-2023: 0.00
    NET AMOUNT: 734.00
    """
    res = BillParser.parse_text([{"page_number": 1, "text": sample_text}])
    # Arrears must NOT be 2023.00
    assert res["printed_arrears"]["value"] != 2023.00
    assert res["printed_arrears"]["value"] in [0.0, None]

def test_image_ocr_on_workspace_samplebill_jpeg():
    import os
    from backend.app.extraction.image_ocr import ImageOCR
    img_path = "/Users/bhanuprasad/AIBILL/samplebill.jpeg"
    if os.path.exists(img_path):
        res = ImageOCR.ocr_image_file(img_path)
        parsed = BillParser.parse_text([res])
        assert parsed["utility_code"]["value"] == "TGNPDCL"
        assert parsed["service_number"]["value"] == "13164173"
        assert parsed["consumer_name"]["value"] == "G P WATER WORKS"
        assert parsed["consumer_category"]["value"] == "LT-VI(B) PWS Schemes (Panchayats)"
        assert parsed["billing_month"]["value"] == "2023-02"
        assert parsed["consumption_units"]["value"] == 18815252.0
        assert parsed["contracted_load_kw"]["value"] == 5.0
        assert parsed["printed_total"]["value"] == 114163672.0


def test_parser_arrears_no_year_leakage():
    """Verify that dates like 01-04-2023 or 01-04-22 do not leak into arrears as 2023.00."""
    sample_text = """
    TGSPDCL ELECTRICITY BILL
    SCNO: 1002348911
    NAME: RAMA RAO
    CAT: LT-I(B)(i)
    MONTH: 2023-03
    UNITS: 180
    ENERGY CHARGES: 724.00
    FIXED CHARGES: 10.00
    CUST CHARGES: 90.00
    ED: 10.80
    AS ON: 01-04-2023: 0.00
    AFTER: 01-04-2023: 0.00
    NET AMOUNT: 734.00
    """
    res = BillParser.parse_text([{"page_number": 1, "text": sample_text}])
    # Arrears must NOT be 2023.00
    assert res["printed_arrears"]["value"] != 2023.00
    assert res["printed_arrears"]["value"] in [0.0, None]
