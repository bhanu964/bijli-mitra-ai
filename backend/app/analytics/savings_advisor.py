from typing import List, Dict, Any

class SavingsAdvisor:
    @staticmethod
    def generate_recommendations(
        units: float,
        is_gruha_jyothi: bool = False,
        current_bill_amount: float = 0.0
    ) -> List[Dict[str, Any]]:
        recs = []

        # 1. Gruha Jyothi Optimization Scenario
        if is_gruha_jyothi:
            if 200.0 < units <= 230.0:
                units_to_cut = round(units - 200.0, 1)
                recs.append({
                    "id": "gj_cliff_restore",
                    "title": "Restore 100% Free Electricity (Gruha Jyothi)",
                    "category": "CRITICAL_GOVERNMENT_SCHEME",
                    "estimated_monthly_savings": round(current_bill_amount, 2),
                    "difficulty": "Easy",
                    "impact": "High",
                    "description": (
                        f"You consumed {units:.0f} units this month, which is just {units_to_cut} units above the 200-unit Gruha Jyothi zero-bill threshold. "
                        f"By reducing usage by {units_to_cut} units next month, your entire current electricity bill (~Rs. {current_bill_amount:.2f}) will become Rs. 0.00!"
                    ),
                    "action_steps": [
                        "Set AC temperature to 25°C instead of 20°C (saves 15-20 units/month).",
                        "Turn off water geysers immediately after heating.",
                        "Track meter reading on day 25 of the billing cycle to ensure units stay <= 200."
                    ]
                })
            elif 185.0 <= units <= 200.0:
                recs.append({
                    "id": "gj_cliff_caution",
                    "title": "Protect Your Zero-Bill Status",
                    "category": "CAUTION_GOVERNMENT_SCHEME",
                    "estimated_monthly_savings": round(current_bill_amount, 2) if current_bill_amount > 0 else 900.0,
                    "difficulty": "Easy",
                    "impact": "High",
                    "description": (
                        f"You are currently at {units:.0f} units, very close to the 200-unit ceiling. "
                        "If you use even 2-3 extra units, you will lose the zero-bill subsidy and be billed for the entire 201+ units (~Rs. 1,150+)."
                    ),
                    "action_steps": [
                        "Keep ceiling fans on medium speed.",
                        "Unplug standby TV, set-top box, and microwave chargers when not in use."
                    ]
                })

        # 2. Slab Cliff Optimization for General Domestic (LT-I)
        if not is_gruha_jyothi:
            if 100.0 < units <= 115.0:
                units_over = round(units - 100.0, 1)
                recs.append({
                    "id": "slab_bracket_drop_100",
                    "title": "Drop into the Lowest Domestic Bracket (LT-I(A))",
                    "category": "TARIFF_SLAB_OPTIMIZATION",
                    "estimated_monthly_savings": 140.0,
                    "difficulty": "Medium",
                    "impact": "Medium",
                    "description": (
                        f"You are currently in LT-I(B)(i) ({units:.0f} units). If you lower usage by {units_over} units to $\\le 100$ units, "
                        "your base rate drops from Rs. 3.40/unit to Rs. 1.95 (for 0-50 units) and customer charges decrease from Rs. 90 to Rs. 70."
                    ),
                    "action_steps": [
                        "Switch old tube lights to 9W LED bulbs.",
                        "Run washing machines only with full loads."
                    ]
                })

        # 3. High Consumption Tier (>800 units)
        if units > 800.0:
            recs.append({
                "id": "tier_800_reduction",
                "title": "Avoid High Demand Charge Tier (>800 units)",
                "category": "FIXED_CHARGE_REDUCTION",
                "estimated_monthly_savings": 250.0,
                "difficulty": "Medium",
                "impact": "High",
                "description": (
                    f"Consuming {units:.0f} units places you above 800 units, which triggers a Rs. 50/kW monthly fixed charge (versus Rs. 10/kW) "
                    "plus the highest energy slab of Rs. 10.00/unit."
                ),
                "action_steps": [
                    "Perform energy audit on high-tonnage ACs and refrigeration equipment.",
                    "Explore Telangana Solar Rooftop scheme with net-metering to offset high-tier consumption."
                ]
            })

        # 4. Standard Energy Efficiency Practices
        recs.append({
            "id": "appliance_efficiency",
            "title": "Air Conditioner & Refrigeration Optimization",
            "category": "GENERAL_EFFICIENCY",
            "estimated_monthly_savings": 350.0,
            "difficulty": "Easy",
            "impact": "Medium",
            "description": (
                "Setting your air conditioner thermostat at 24°C to 26°C uses 20% to 30% less electricity than running at 18°C. "
                "Ensuring refrigerator door seals are tight prevents continuous compressor cycling."
            ),
            "action_steps": [
                "Set AC timer to switch off after 4-5 hours of night sleep.",
                "Clean AC filters every 2 weeks to maintain optimal airflow."
            ]
        })

        return recs
