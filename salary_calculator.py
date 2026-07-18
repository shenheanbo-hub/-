"""Pure salary summary calculations shared by the UI and tests."""


def monthly_salary_summary(state, month):
    records = [
        record for record in state.get("records", [])
        if str(record.get("date", "")).startswith(month)
    ]
    base_salary = float(state.get("monthly_salary", 0) or 0)
    overtime_pay = sum(float(record.get("pay", 0) or 0) for record in records)
    overtime_hours = sum(float(record.get("hours", 0) or 0) for record in records)
    return {
        "base_salary": round(base_salary, 2),
        "overtime_pay": round(overtime_pay, 2),
        "gross_salary": round(base_salary + overtime_pay, 2),
        "overtime_hours": round(overtime_hours, 2),
        "record_count": len(records),
    }
