from typing import List, Dict, Any, Optional

class ConsumptionTracker:
    @staticmethod
    def calculate_summary(bills_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyzes consumer bill history to compute monthly trends, averages, and changes.
        """
        if not bills_data:
            return {
                "total_bills_analyzed": 0,
                "latest_bill_amount": 0.0,
                "latest_units": 0.0,
                "previous_month_units": None,
                "consumption_change_pct": None,
                "average_monthly_spend": 0.0,
                "average_monthly_units": 0.0,
                "highest_month": None,
                "lowest_month": None,
                "monthly_trend": [],
                "discrepancies_detected_count": 0
            }

        # Sort by billing month ascending
        sorted_bills = sorted(bills_data, key=lambda b: b.get("billing_month", ""))
        latest = sorted_bills[-1]
        previous = sorted_bills[-2] if len(sorted_bills) > 1 else None
        
        total_units = sum(b.get("consumption_units", 0.0) for b in sorted_bills)
        total_spend = sum(b.get("printed_total", 0.0) for b in sorted_bills)
        n = len(sorted_bills)
        
        avg_units = round(total_units / n, 1)
        avg_spend = round(total_spend / n, 2)
        
        highest_bill = max(sorted_bills, key=lambda b: b.get("consumption_units", 0.0))
        lowest_bill = min(sorted_bills, key=lambda b: b.get("consumption_units", 0.0))
        
        change_pct = None
        if previous and previous.get("consumption_units", 0) > 0:
            diff = latest.get("consumption_units", 0) - previous.get("consumption_units", 0)
            change_pct = round((diff / previous.get("consumption_units", 0)) * 100.0, 1)

        monthly_trend = []
        discrepancies = 0
        for b in sorted_bills:
            if b.get("status") == "DISCREPANCY_DETECTED" or b.get("has_discrepancy"):
                discrepancies += 1
            monthly_trend.append({
                "month": b.get("billing_month"),
                "units": b.get("consumption_units", 0.0),
                "amount": b.get("printed_total", 0.0),
                "computed_total": b.get("computed_total", b.get("printed_total", 0.0)),
                "is_gruha_jyothi": b.get("is_gruha_jyothi", False)
            })

        return {
            "total_bills_analyzed": n,
            "latest_bill_amount": latest.get("printed_total", 0.0),
            "latest_units": latest.get("consumption_units", 0.0),
            "previous_month_units": previous.get("consumption_units") if previous else None,
            "consumption_change_pct": change_pct,
            "average_monthly_spend": avg_spend,
            "average_monthly_units": avg_units,
            "highest_month": f"{highest_bill.get('billing_month')} ({highest_bill.get('consumption_units')} units)",
            "lowest_month": f"{lowest_bill.get('billing_month')} ({lowest_bill.get('consumption_units')} units)",
            "monthly_trend": monthly_trend,
            "discrepancies_detected_count": discrepancies
        }
