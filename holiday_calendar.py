"""Offline Chinese holiday/workday classification.

The bundled JSON is based on the annual State Council holiday notices. Dates not
listed explicitly fall back to their weekday: Monday-Friday are workdays and
Saturday-Sunday are rest days.
"""

import json
from datetime import date
from pathlib import Path


TYPE_WEEKDAY = "平日 1.5 倍"
TYPE_REST = "休息日 2 倍"
TYPE_HOLIDAY = "节假日 3 倍"


class HolidayCalendar:
    def __init__(self, data_file=None):
        path = Path(data_file) if data_file else Path(__file__).with_name("holidays.json")
        self.holidays = set()
        self.workdays = set()
        self.years = set()
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            for year, values in data.get("years", {}).items():
                self.years.add(int(year))
                self.holidays.update(values.get("holidays", []))
                self.workdays.update(values.get("workdays", []))
        except (OSError, ValueError, TypeError):
            # The app remains usable even if its optional data file is damaged.
            pass

    def classify(self, day):
        """Return (overtime_type, explanation) for a datetime.date."""
        key = day.isoformat()
        if key in self.workdays:
            return TYPE_WEEKDAY, "法定调休上班日"
        if key in self.holidays:
            return TYPE_HOLIDAY, "法定节假日"
        if day.weekday() >= 5:
            return TYPE_REST, "周末休息日"
        note = "普通工作日"
        if self.years and day.year not in self.years:
            note = "未内置该年度安排，已按星期判断"
        return TYPE_WEEKDAY, note

