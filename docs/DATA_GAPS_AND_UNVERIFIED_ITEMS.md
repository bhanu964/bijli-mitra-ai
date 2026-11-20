# BIJLI MITRA AI — DATA GAPS AND UNVERIFIED ITEMS
## Transparency, Data Completeness, and Pending Verification Register

**Document Version:** 1.0.0  
**Status:** Monitored and Maintained  
**Guiding Principle:** In accordance with project instructions, missing or unverified rules are never assumed or fabricated; they are explicitly flagged as `PENDING_VERIFICATION`.

---

### 1. Specific Data Gaps and Engineering Resolutions

| # | Item Description | Why it cannot be universally hardcoded | Engineering / System Resolution | Verification Status |
|---|---|---|---|---|
| **1** | **Monthly Variable FCA/FSA Rate** | The Multi-Year Tariff Regulation sets the formula and a statutory ceiling of Rs. 0.30/unit, but individual monthly rates vary based on DISCOM spot fuel costs and are gazetted monthly in local newspapers. | The system extracts the printed FSA/FCA directly from the uploaded bill. It runs a safety ceiling validation ($ \le \text{Rs. 0.30/unit} $). If missing or anomalous, it flags `PENDING_VERIFICATION` instead of guessing a rate. | `PENDING_VERIFICATION` (Per-bill variable) |
| **2** | **Consumer-Specific True-Up Quantum ($Q_{monthly}$)** | The TGERC Order dated 05.10.2026 establishes recovery based on $1/12\text{th}$ of the consumer's actual annual consumption in FY 2022-23 and FY 2023-24. | If the bill prints both the True-Up rate (Rs. 0.30 or 0.50) and quantum, the system validates the arithmetic ($Q \times \text{Rate}$). If only the total charge is printed, the engine checks whether it falls within reasonable bounds and prompts the user to verify their historical consumption base. | `PENDING_VERIFICATION` (Consumer-specific past history) |
| **3** | **Gruha Jyothi Government Database Status** | White Ration Card / Praja Palana backend database is an internal State Government portal requiring authenticated citizen consent and SSO. | The system inspects the bill's printed subsidy line item, zero-bill flag, or "Gruha Jyothi" markings. It allows the user to declare their eligibility status during the editable review step without fabricating external API links. | `VERIFIED` via Bill Indicator & User Confirmation |
| **4** | **Unscheduled Local Surcharges / Cess** | Certain legacy municipalities or local authorities may attempt ad-hoc surcharges not listed in the TGERC Retail Supply Tariff Schedule. | Any charge row that cannot be mapped to the canonical TGERC categories (Energy, Customer, Fixed, ED, FSA, True-Up, Arrears, DPS) is classified as `OTHER_UNSCHEDULED_CHARGE` and flagged for consumer review. | `PENDING_VERIFICATION` |
| **5** | **Pre-FY 2023 Tariff Schedules** | The attached project repository includes official tariff schedules from FY 2023-24 through FY 2026-27. Orders prior to April 2023 are not part of the active challenge repository. | For bills dated prior to 01.04.2023, the calculation engine flags `TARIFF_VERSION_OUT_OF_BOUNDS` and alerts the user rather than retrofitting current rates. | `PENDING_VERIFICATION` (Out-of-Scope Historical) |

---

### 2. Discrepancy Severity Classifications

To ensure honest, objective reporting to the consumer without making false accusations against utilities:

1. **CONFIRMED_ARITHMETIC_ERROR:**
   - The printed sum on the bill does not match the arithmetic sum of its constituent printed line items ($|\sum \text{items} - \text{Total}| > \text{Rs. 1.00}$).
2. **REGULATORY_RATE_MISMATCH:**
   - The rate charged per slab, fixed charge, or customer charge deviates from the officially gazetted TGERC schedule for that utility, category, and effective billing month.
3. **UNUSUAL_VARIATION (Anomaly):**
   - Monthly consumption jumped $>50\%$ or dropped $>50\%$ compared to previous historical average, or unusually large unexplained adjustments are present.
4. **NORMAL_VARIATION:**
   - Fluctuation within seasonal expectations (e.g., summer cooling load changes).
