import unittest
from datetime import date

from holiday_calendar import HolidayCalendar, TYPE_HOLIDAY, TYPE_REST, TYPE_WEEKDAY


class HolidayCalendarTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.calendar = HolidayCalendar()

    def test_2026_holiday(self):
        self.assertEqual(self.calendar.classify(date(2026, 10, 1))[0], TYPE_HOLIDAY)

    def test_2026_makeup_workday(self):
        self.assertEqual(self.calendar.classify(date(2026, 10, 10))[0], TYPE_WEEKDAY)

    def test_regular_weekend(self):
        self.assertEqual(self.calendar.classify(date(2026, 7, 18))[0], TYPE_REST)


if __name__ == "__main__":
    unittest.main()
