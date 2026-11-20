import os
import hashlib
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.app.core.database import get_db
from backend.app.core.config import settings
from backend.app.models.models import Bill, BillExtraction, BillCharge, CalculationResult, AnomalyReport
from backend.app.schemas.schemas import (
    BillVerificationRequest, CalculationResultSchema, BillSummarySchema
)
from backend.app.extraction.pdf_extractor import PDFExtractor
from backend.app.extraction.image_ocr import ImageOCR
from backend.app.extraction.parser import BillParser
from backend.app.tariff_engine.engine import TariffEngine

router = APIRouter(prefix="/bills", tags=["Bills"])

def _execute_bill_calculation(bill: Bill, db: Session) -> CalculationResultSchema:
    """
    Executes deterministic tariff-based calculation engine for a bill,
    persists itemized charges and anomalies, and updates bill status.
    """
    extractions = {e.field_name: e.raw_value for e in bill.extractions}
    def flt(val, default=None):
        if val is None or val == "None" or val == "":
            return default
        try:
            return float(val)
        except (ValueError, TypeError):
            return default

    calc_input = {
        "consumption_units": bill.consumption_units,
        "billing_month": bill.billing_month,
        "utility_code": bill.utility_code or "TGSPDCL",
        "contracted_load_kw": bill.contracted_load_kw,
        "consumer_category": bill.consumer_category or "LT-I Domestic",
        "printed_total": bill.printed_total,
        "is_gruha_jyothi": bill.is_gruha_jyothi,
        "gruha_jyothi_eligible": bill.gruha_jyothi_eligible,
        "previous_reading": bill.previous_reading if bill.previous_reading is not None else flt(extractions.get("previous_reading")),
        "current_reading": bill.current_reading if bill.current_reading is not None else flt(extractions.get("current_reading")),
        "historical_average_units": flt(extractions.get("historical_average_units")),
        "last_paid_amount": flt(extractions.get("last_paid_amount")),
        "printed_energy_charges": flt(extractions.get("printed_energy_charges")),
        "printed_customer_charges": flt(extractions.get("printed_customer_charges")),
        "printed_fixed_charges": flt(extractions.get("printed_fixed_charges")),
        "printed_electricity_duty": flt(extractions.get("printed_electricity_duty")),
        "printed_fsa_charges": flt(extractions.get("printed_fsa_charges")),
        "printed_true_up_charges": flt(extractions.get("printed_true_up_charges")),
        "printed_arrears": flt(extractions.get("printed_arrears")),
        "printed_adjustments": flt(extractions.get("printed_adjustments")),
        "printed_subsidy": flt(extractions.get("printed_subsidy"))
    }
    
    result = TariffEngine.calculate(calc_input)
    
    if bill.calculation:
        db.delete(bill.calculation)
    db.query(BillCharge).filter(BillCharge.bill_id == bill.id).delete()
    db.query(AnomalyReport).filter(AnomalyReport.bill_id == bill.id).delete()
    db.flush()
    
    calc_record = CalculationResult(
        bill_id=bill.id,
        computed_units=result["consumption_units"],
        computed_energy_charge=result["energy_charges"],
        computed_customer_charge=result["customer_charges"],
        computed_fixed_charge=result["fixed_charges"],
        computed_duty=result["electricity_duty"],
        computed_fsa=result["fsa_charges"],
        computed_true_up=result["true_up_charges"],
        computed_subsidy=result["subsidies"],
        computed_total=result["computed_total"],
        printed_total=result["printed_total"],
        total_difference=result["total_difference"],
        status=result["status"],
        calculation_trace=result,
        explanation_en=result["explanation_en"],
        explanation_te=result["explanation_te"]
    )
    db.add(calc_record)
    
    for ch in result["itemized_charges"]:
        db.add(BillCharge(
            bill_id=bill.id,
            charge_type=ch["charge_type"],
            label=ch["label"],
            printed_amount=ch["printed_amount"],
            computed_amount=ch["computed_amount"],
            difference=ch["difference"],
            is_discrepant=ch["is_discrepant"],
            explanation=ch["explanation"]
        ))
        
    for an in result["anomalies"]:
        db.add(AnomalyReport(
            bill_id=bill.id,
            severity=an["severity"],
            issue_type=an["issue_type"],
            description=an["description"],
            legal_reference=an.get("legal_reference"),
            suggested_action=an.get("suggested_action")
        ))
        
    bill.status = "CALCULATED"
    db.commit()
    db.refresh(bill)
    
    return CalculationResultSchema(
        bill_id=bill.id,
        tariff_version=result["tariff_version"],
        effective_dates=result["effective_dates"],
        status=result["status"],
        consumption_units=result["consumption_units"],
        contracted_load_kw=result["contracted_load_kw"],
        category_determined=result["category_determined"],
        energy_charges=result["energy_charges"],
        energy_slabs=result["energy_slabs"],
        customer_charges=result["customer_charges"],
        fixed_charges=result["fixed_charges"],
        electricity_duty=result["electricity_duty"],
        fsa_charges=result["fsa_charges"],
        true_up_charges=result["true_up_charges"],
        subsidies=result["subsidies"],
        arrears=result["arrears"],
        adjustments=result["adjustments"],
        computed_total=result["computed_total"],
        printed_total=result["printed_total"],
        total_difference=result["total_difference"],
        itemized_charges=result["itemized_charges"],
        anomalies=result["anomalies"],
        explanation_en=result["explanation_en"],
        explanation_te=result["explanation_te"],
        source_citations=result["source_citations"]
    )

@router.post("/upload")
async def upload_bill(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Accepts PDF or Image electricity bill, runs secure validation,
    document text extraction / high-res multi-pass OCR, parses structured fields,
    and automatically calculates the bill immediately.
    """
    filename = file.filename or "uploaded_bill.pdf"
    content = await file.read()
    
    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")
    if len(content) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds maximum 15MB limit.")
        
    file_hash = hashlib.sha256(content).hexdigest()
    
    existing_bill = db.query(Bill).filter(Bill.file_hash == file_hash).first()
    
    if not existing_bill:
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        file_path = os.path.join(settings.UPLOAD_DIR, unique_name)
        with open(file_path, "wb") as f:
            f.write(content)
    else:
        file_path = existing_bill.file_path

    # Run extraction pipeline
    is_pdf = filename.lower().endswith(".pdf")
    pages_data = []
    
    if is_pdf:
        digital_pages = PDFExtractor.extract_text_by_pages(file_path)
        is_scanned = all(p["is_scanned"] for p in digital_pages)
        if is_scanned:
            pages_data = ImageOCR.ocr_pdf(file_path)
        else:
            pages_data = digital_pages
    else:
        img_res = ImageOCR.ocr_image_file(file_path)
        pages_data = [img_res]

    # Parse extracted text with multi-utility & thermal receipt intelligence
    parsed_fields = BillParser.parse_text(pages_data)
    
    if existing_bill:
        bill = existing_bill
        bill.utility_code = parsed_fields["utility_code"]["value"]
        bill.service_number = parsed_fields["service_number"]["value"] or bill.service_number
        bill.consumer_name = parsed_fields["consumer_name"]["value"] or bill.consumer_name
        bill.consumer_category = parsed_fields["consumer_category"]["value"]
        bill.billing_month = parsed_fields["billing_month"]["value"]
        bill.consumption_units = parsed_fields["consumption_units"]["value"]
        bill.contracted_load_kw = parsed_fields["contracted_load_kw"]["value"]
        bill.previous_reading = parsed_fields["previous_reading"]["value"]
        bill.current_reading = parsed_fields["current_reading"]["value"]
        bill.printed_total = parsed_fields["printed_total"]["value"]
        bill.is_gruha_jyothi = parsed_fields["is_gruha_jyothi"]["value"]
        bill.status = "EXTRACTED"
        
        db.query(BillExtraction).filter(BillExtraction.bill_id == bill.id).delete()
    else:
        bill = Bill(
            utility_code=parsed_fields["utility_code"]["value"],
            service_number=parsed_fields["service_number"]["value"],
            consumer_name=parsed_fields["consumer_name"]["value"],
            consumer_category=parsed_fields["consumer_category"]["value"],
            billing_month=parsed_fields["billing_month"]["value"],
            consumption_units=parsed_fields["consumption_units"]["value"],
            contracted_load_kw=parsed_fields["contracted_load_kw"]["value"],
            previous_reading=parsed_fields["previous_reading"]["value"],
            current_reading=parsed_fields["current_reading"]["value"],
            printed_total=parsed_fields["printed_total"]["value"],
            is_gruha_jyothi=parsed_fields["is_gruha_jyothi"]["value"],
            file_name=filename,
            file_path=file_path,
            file_hash=file_hash,
            mime_type=file.content_type or "application/pdf",
            status="EXTRACTED"
        )
        db.add(bill)
        
    db.flush()
    
    # Store extraction confidence logs
    for field_name, item in parsed_fields.items():
        val = str(item.get("value")) if item.get("value") is not None else None
        conf = float(item.get("confidence", 0.8))
        meth = str(item.get("method", "PARSER"))
        ext = BillExtraction(
            bill_id=bill.id,
            field_name=field_name,
            raw_value=val,
            confidence=conf,
            extraction_method=meth
        )
        db.add(ext)
        
    db.commit()
    db.refresh(bill)
    
    # AUTOMATICALLY EXECUTE TARIFF CALCULATION IMMEDIATELY!
    calc_result = _execute_bill_calculation(bill, db)
    
    # Structured response with dual-support (both .value objects and direct keys)
    extracted_data_formatted = {
        "utility_code": {"value": bill.utility_code, "confidence": 0.95},
        "service_number": {"value": bill.service_number, "confidence": 0.92},
        "consumer_name": {"value": bill.consumer_name, "confidence": 0.88},
        "consumer_category": {"value": bill.consumer_category, "confidence": 0.95},
        "billing_month": {"value": bill.billing_month, "confidence": 0.90},
        "consumption_units": {"value": bill.consumption_units, "confidence": 0.95},
        "contracted_load_kw": {"value": bill.contracted_load_kw, "confidence": 0.90},
        "previous_reading": {"value": bill.previous_reading, "confidence": 0.90},
        "current_reading": {"value": bill.current_reading, "confidence": 0.90},
        "printed_total": {"value": bill.printed_total, "confidence": 0.92},
        "printed_energy_charges": {"value": parsed_fields["printed_energy_charges"]["value"], "confidence": 0.88},
        "printed_customer_charges": {"value": parsed_fields["printed_customer_charges"]["value"], "confidence": 0.88},
        "printed_fixed_charges": {"value": parsed_fields["printed_fixed_charges"]["value"], "confidence": 0.88},
        "printed_electricity_duty": {"value": parsed_fields["printed_electricity_duty"]["value"], "confidence": 0.88},
        "printed_fsa_charges": {"value": parsed_fields["printed_fsa_charges"]["value"], "confidence": 0.85},
        "printed_true_up_charges": {"value": parsed_fields["printed_true_up_charges"]["value"], "confidence": 0.85},
        "printed_arrears": {"value": parsed_fields["printed_arrears"]["value"], "confidence": 0.88},
        "printed_adjustments": {"value": parsed_fields["printed_adjustments"]["value"], "confidence": 0.85},
        "printed_subsidy": {"value": parsed_fields["printed_subsidy"]["value"], "confidence": 0.85},
        "last_paid_amount": {"value": parsed_fields.get("last_paid_amount", {}).get("value"), "confidence": 0.88},
        "historical_average_units": {"value": parsed_fields.get("historical_average_units", {}).get("value"), "confidence": 0.85},
        "is_gruha_jyothi": {"value": bill.is_gruha_jyothi, "confidence": 0.90},
        "gruha_jyothi_eligible": {"value": bill.gruha_jyothi_eligible, "confidence": 0.90}
    }
    
    return {
        "bill_id": bill.id,
        "status": "CALCULATED",
        "message": "Bill successfully extracted and tariff calculation completed.",
        "extracted_data": extracted_data_formatted,
        "calculation": calc_result
    }

@router.get("", response_model=List[BillSummarySchema])
def list_bills(db: Session = Depends(get_db)):
    bills = db.query(Bill).order_by(Bill.billing_month.desc(), Bill.id.desc()).all()
    out = []
    for b in bills:
        has_disc = False
        if b.calculation and b.calculation.status in ["DISCREPANCY_DETECTED", "CRITICAL_ANOMALY_DETECTED"]:
            has_disc = True
        out.append(BillSummarySchema(
            id=b.id,
            utility_code=b.utility_code or "TGSPDCL",
            service_number=b.service_number,
            consumer_name=b.consumer_name,
            billing_month=b.billing_month,
            consumption_units=b.consumption_units,
            printed_total=b.printed_total,
            status=b.status,
            is_gruha_jyothi=b.is_gruha_jyothi,
            created_at=b.created_at,
            has_discrepancy=has_disc
        ))
    return out

@router.get("/{bill_id}")
def get_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    calc_data = None
    if bill.calculation:
        c = bill.calculation
        trace = c.calculation_trace or {}

        itemized = [
            {
                "charge_type": ch.charge_type,
                "label": ch.label,
                "printed_amount": ch.printed_amount,
                "computed_amount": ch.computed_amount,
                "difference": ch.difference,
                "is_discrepant": ch.is_discrepant,
                "explanation": ch.explanation
            }
            for ch in bill.charges
        ] if bill.charges else trace.get("itemized_charges", [])

        anomalies_list = [
            {
                "severity": a.severity,
                "issue_type": a.issue_type,
                "description": a.description,
                "legal_reference": a.legal_reference,
                "suggested_action": a.suggested_action
            }
            for a in bill.anomalies
        ] if bill.anomalies else trace.get("anomalies", [])

        calc_data = {
            "bill_id": bill.id,
            "tariff_version": trace.get("tariff_version", "FY 2026-27"),
            "effective_dates": trace.get("effective_dates", ""),
            "status": c.status,
            "consumption_units": c.computed_units,
            "contracted_load_kw": bill.contracted_load_kw or trace.get("contracted_load_kw", 1.0),
            "category_determined": trace.get("category_determined", bill.consumer_category or "LT-I Domestic"),
            "energy_charges": c.computed_energy_charge,
            "energy_slabs": trace.get("energy_slabs", []),
            "customer_charges": c.computed_customer_charge,
            "fixed_charges": c.computed_fixed_charge,
            "electricity_duty": c.computed_duty,
            "fsa_charges": c.computed_fsa,
            "true_up_charges": c.computed_true_up,
            "subsidies": c.computed_subsidy,
            "arrears": trace.get("arrears", 0.0),
            "adjustments": trace.get("adjustments", 0.0),
            "computed_total": c.computed_total,
            "printed_total": c.printed_total,
            "total_difference": c.total_difference,
            "explanation_en": c.explanation_en,
            "explanation_te": c.explanation_te,
            "itemized_charges": itemized,
            "anomalies": anomalies_list,
            "audit_steps": trace.get("audit_steps", []),
            "source_citations": trace.get("source_citations", [
                "TGERC Retail Supply Tariff Order",
                "Telangana State Electricity Duty Act, 1939",
                "TGERC Electricity Supply Code Regulations"
            ])
        }
        
    return {
        "bill": {
            "id": bill.id,
            "utility_code": bill.utility_code,
            "service_number": bill.service_number,
            "consumer_name": bill.consumer_name,
            "consumer_category": bill.consumer_category,
            "billing_month": bill.billing_month,
            "issue_date": str(bill.issue_date) if bill.issue_date else None,
            "due_date": str(bill.due_date) if bill.due_date else None,
            "previous_reading": bill.previous_reading,
            "current_reading": bill.current_reading,
            "consumption_units": bill.consumption_units,
            "contracted_load_kw": bill.contracted_load_kw,
            "printed_total": bill.printed_total,
            "is_gruha_jyothi": bill.is_gruha_jyothi,
            "gruha_jyothi_eligible": bill.gruha_jyothi_eligible,
            "status": bill.status,
            "file_name": bill.file_name
        },
        "calculation": calc_data
    }

@router.put("/{bill_id}/verify")
def verify_and_update_bill(
    bill_id: int,
    payload: BillVerificationRequest,
    db: Session = Depends(get_db)
):
    """
    Consumer Verification Screen: Saves consumer corrections to extracted values
    and re-runs deterministic tariff calculation.
    """
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    bill.utility_code = payload.utility_code
    bill.service_number = payload.service_number
    bill.consumer_name = payload.consumer_name
    bill.consumer_category = payload.consumer_category
    bill.billing_month = payload.billing_month
    bill.issue_date = payload.issue_date
    bill.due_date = payload.due_date
    bill.previous_reading = payload.previous_reading
    bill.current_reading = payload.current_reading
    bill.consumption_units = payload.consumption_units
    bill.contracted_load_kw = payload.contracted_load_kw
    bill.printed_total = payload.printed_total
    bill.is_gruha_jyothi = payload.is_gruha_jyothi
    bill.gruha_jyothi_eligible = payload.gruha_jyothi_eligible
    bill.ration_card_number = payload.ration_card_number
    bill.status = "VERIFIED"
    
    extractions_map = {e.field_name: e for e in bill.extractions}
    components = [
        ("printed_energy_charges", payload.printed_energy_charges),
        ("printed_customer_charges", payload.printed_customer_charges),
        ("printed_fixed_charges", payload.printed_fixed_charges),
        ("printed_electricity_duty", payload.printed_electricity_duty),
        ("printed_fsa_charges", payload.printed_fsa_charges),
        ("printed_true_up_charges", payload.printed_true_up_charges),
        ("printed_arrears", payload.printed_arrears),
        ("printed_adjustments", payload.printed_adjustments),
        ("printed_subsidy", payload.printed_subsidy),
    ]
    for key, val in components:
        if val is not None:
            if key in extractions_map:
                extractions_map[key].raw_value = str(val)
                extractions_map[key].user_override_value = str(val)
                extractions_map[key].is_verified = True
            else:
                db.add(BillExtraction(
                    bill_id=bill.id,
                    field_name=key,
                    raw_value=str(val),
                    user_override_value=str(val),
                    is_verified=True,
                    confidence=1.0,
                    extraction_method="USER_VERIFIED"
                ))

    db.commit()
    db.refresh(bill)
    
    # Automatically recalculate with verified numbers
    calc_res = _execute_bill_calculation(bill, db)
    
    return {
        "message": "Bill details successfully verified and updated.",
        "bill_id": bill.id,
        "calculation": calc_res
    }

@router.post("/{bill_id}/calculate", response_model=CalculationResultSchema)
def calculate_bill_analysis(
    bill_id: int,
    db: Session = Depends(get_db)
):
    """
    Executes deterministic tariff-based calculation engine for the bill.
    Compares printed vs calculated amounts, detects anomalies, and generates bilingual explanations.
    """
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    return _execute_bill_calculation(bill, db)

@router.delete("/{bill_id}")
def delete_bill(bill_id: int, db: Session = Depends(get_db)):
    bill = db.query(Bill).filter(Bill.id == bill_id).first()
    if not bill:
        raise HTTPException(status_code=404, detail="Bill not found")
        
    if bill.file_path and os.path.exists(bill.file_path):
        try:
            os.remove(bill.file_path)
        except Exception:
            pass
            
    db.delete(bill)
    db.commit()
    return {"message": "Bill successfully deleted."}
