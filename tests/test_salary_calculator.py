import unittest

from salary_calculator import monthly_salary_summary


class MonthlySalarySummaryTest(unittest.TestCase):
    def test_current_month_gross_salary(self):
        state = {
            "monthly_salary": 6000,
            "records": [
                {"date": "2026-07-01", "hours": 2, "pay": 100},
                {"date": "2026-07-02", "hours": 3.5, "pay": 200.25},
                {"date": "2026-06-30", "hours": 8, "pay": 999},
            ],
        }
        result = monthly_salary_summary(state, "2026-07")
        self.assertEqual(result["base_salary"], 6000)
        self.assertEqual(result["overtime_pay"], 300.25)
        self.assertEqual(result["gross_salary"], 6300.25)
        self.assertEqual(result["overtime_hours"], 5.5)
        self.assertEqual(result["record_count"], 2)


if __name__ == "__main__":
    unittest.main()
