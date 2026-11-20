# BIJLI MITRA AI — BILLING RULES REPORT
## Operational Billing Rules, Regulatory Mandates, and Calculation Mechanics

**Version:** 1.0.0  
**Scope:** TGSPDCL and TGNPDCL Domestic (LT-I) Electricity Billing  
**Authoritative Sources:** TGERC / TSERC Regulations & Orders

---

### 1. Master Formula for Monthly Electricity Bill Calculation

For any given billing cycle, the total bill payable is computed through strict component separation:

$$\text{Total Bill} = \text{EC} + \text{FC} + \text{CC} + \text{ED} + \text{FSA/FCA} + \text{True-Up} + \text{Arrears} + \text{Adjustments} + \text{DPS} - \text{Subsidy}$$

Where:
- **$\text{EC}$ (Energy Charges):** Tier-based telescopic calculation on total metered kWh consumption.
- **$\text{FC}$ (Fixed Charges):** Contracted load (in kW) $\times$ applicable fixed rate per kW.
- **$\text{CC}$ (Customer Charges):** Slab-based flat charge depending on total consumption bracket.
- **$\text{ED}$ (Electricity Duty):** Total units consumed $\times$ Rs. 0.06 / kWh.
- **$\text{FSA/FCA}$ (Fuel Cost Adjustment):** Permitted fuel surcharge adjustment $\times$ units consumed (capped at Rs. 0.30/unit unless explicitly approved otherwise).
- **$\text{True-Up}$ (Regulatory True-Up Recovery):** Commencing November 2026 bills, $Q_{monthly} \times \text{Rate}$ (Rs. 0.30 for Month 1, Rs. 0.50 thereafter) for 29 months (TGSPDCL) / 26 months (TGNPDCL).
- **$\text{Arrears}$:** Unpaid previous balances.
- **$\text{Adjustments}$:** Regulatory credits, court-ordered refunds, or prior billing dispute corrections.
- **$\text{DPS}$ (Delayed Payment Surcharge):** Levied only if past payment due date (Flat Rs. 10 for LT-I(A), Rs. 25 for LT-I(B)).
- **$\text{Subsidy}$:** Government subsidy (e.g., 100% bill waiver under Gruha Jyothi for eligible beneficiaries up to 200 units).

---

### 2. Tier Selection and Slab Calculation Logic

The engine must implement deterministic bracket selection prior to slab evaluation:

```python
def calculate_energy_charges(units: float) -> tuple[str, float, list[dict]]:
    """
    Computes energy charges according to TGERC approved domestic tariff schedules.
    Returns: (category, total_charge, itemized_slabs)
    """
    breakdown = []
    total = 0.0

    if units <= 100:
        category = "LT-I(A)"
        # Slab 1: 0 - 50 units @ Rs. 1.95
        u1 = min(units, 50.0)
        c1 = u1 * 1.95
        breakdown.append({"slab": "0-50 units", "units": u1, "rate": 1.95, "amount": c1})
        total += c1
        
        # Slab 2: 51 - 100 units @ Rs. 3.10
        if units > 50:
            u2 = units - 50.0
            c2 = u2 * 3.10
            breakdown.append({"slab": "51-100 units", "units": u2, "rate": 3.10, "amount": c2})
            total += c2

    elif units <= 200:
        category = "LT-I(B)(i)"
        # Slab 1: 0 - 100 units @ Rs. 3.40
        u1 = min(units, 100.0)
        c1 = u1 * 3.40
        breakdown.append({"slab": "0-100 units", "units": u1, "rate": 3.40, "amount": c1})
        total += c1
        
        # Slab 2: 101 - 200 units @ Rs. 4.80
        if units > 100:
            u2 = units - 100.0
            c2 = u2 * 4.80
            breakdown.append({"slab": "101-200 units", "units": u2, "rate": 4.80, "amount": c2})
            total += c2

    else:
        category = "LT-I(B)(ii)"
        slabs = [
            (200.0, 5.10, "0-200 units"),
            (100.0, 7.70, "201-300 units"),
            (100.0, 9.00, "301-400 units"),
            (400.0, 9.50, "401-800 units"),
            (float("inf"), 10.00, "Above 800 units")
        ]
        remaining = units
        for limit, rate, label in slabs:
            if remaining <= 0:
                break
            chunk = min(remaining, limit)
            amt = chunk * rate
            breakdown.append({"slab": label, "units": chunk, "rate": rate, "amount": amt})
            total += amt
            remaining -= chunk

    return category, round(total, 2), breakdown
```

---

### 3. Gruha Jyothi Scheme Billing Mechanics

Under G.O.Ms.No.7 and TSERC Order dated 16.03.2024 (O.P. No. 6 of 2024):
1. **Eligibility Evaluation Matrix:**
   - Domestic connection (LT-I).
   - Valid Food Security Card (White Ration Card).
   - Aadhaar number authenticated.
   - Domestic service connection registered on Praja Palana portal.
2. **Monthly Consumption Rule:**
   - If `units <= 200` AND `is_eligible == True`:
     - Net Current Bill = `Rs. 0.00`.
     - GoTS releases 100% subsidy amount directly to TGSPDCL / TGNPDCL in advance under Section 65 of EA 2003.
     - Note: Previous unpaid arrears (if any prior to March 2024) are not covered by Gruha Jyothi and remain payable.
3. **Over-200 Disqualification Rule:**
   - If `units > 200` (e.g. 201 units):
     - The consumer is **ineligible for that billing cycle**.
     - Energy charges are calculated at full LT-I(B)(ii) rates: 200 units @ 5.10 + 1 unit @ 7.70 = Rs. 1,027.70 + Customer Charges (Rs. 100) + Fixed Charges + Duty = **Rs. 1,150+**.
     - The consumer pays the entire bill; no partial 200-unit discount is allowed under the official government order.

---

### 4. Legal Protections Against Erroneous Billing (TGERC Reg 04 of 2026)

Under the Electricity Supply Code Third Amendment (Regulation No. 04 of 2026, dated 27.05.2026):
1. **Mandatory Due Date Extension:** When an erroneous bill complaint is admitted, the utility must issue a revised bill with a due date fixed **not earlier than 7 days** from delivery.
2. **Refund via Adjustment:** Excess amounts paid by the consumer must be credited immediately by adjustment in subsequent monthly bills.
3. **Mandatory 18% p.a. Interest Penalty on Utility:**
   $$\text{Interest Payable by Utility} = \text{Excess Overbilled Amount} \times 18\% \times \frac{\text{Days Outstanding}}{365}$$
   This statutory right must be prominently highlighted to consumers by BIJLI MITRA AI whenever a billing discrepancy or error is detected.

---

### 5. kVArh Lead Billing Relief & Refunds (Procds No. 07/Tariff/TGERC)

1. Unblocking leading kVArh for LT consumers was deferred to 31.03.2026.
2. DISCOMs were ordered to revise all excess bills raised on LT consumers and refund the excess charges via adjustment across 3 monthly bills starting in April 2026.
3. If a consumer's bill between April and June 2026 reflects negative adjustments or credits, BIJLI MITRA AI identifies and explains this as the TGERC-mandated kVArh refund.
