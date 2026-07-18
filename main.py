"""加班薪资记录仪：完全离线、无需读取日历权限。"""

import calendar
import json
from datetime import date, datetime
from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from holiday_calendar import HolidayCalendar


BG = (0.08, 0.09, 0.10, 1)
PANEL = (0.13, 0.14, 0.16, 1)
GREEN = (0.0, 0.92, 0.62, 1)
TEXT = (0.90, 0.94, 0.92, 1)
MUTED = (0.55, 0.62, 0.59, 1)
RED = (0.95, 0.30, 0.30, 1)
TYPE_MULTIPLIERS = {"平日 1.5 倍": 1.5, "休息日 2 倍": 2.0, "节假日 3 倍": 3.0}


def paint(widget, color):
    with widget.canvas.before:
        widget._color = Color(*color)
        widget._rect = Rectangle(pos=widget.pos, size=widget.size)
    widget.bind(pos=lambda obj, value: setattr(obj._rect, "pos", value))
    widget.bind(size=lambda obj, value: setattr(obj._rect, "size", value))


def label(text="", color=TEXT, **kwargs):
    item = Label(text=text, color=color, **kwargs)
    item.bind(size=lambda obj, _value: setattr(obj, "text_size", obj.size))
    return item


def button(text, callback=None, danger=False, **kwargs):
    item = Button(text=text, color=TEXT if danger else BG, background_normal="",
                  background_color=RED if danger else GREEN, **kwargs)
    if callback:
        item.bind(on_release=callback)
    return item


class DatePickerPopup(Popup):
    """Local calendar picker backed by the phone's system date."""

    def __init__(self, selected, callback, **kwargs):
        super().__init__(title="选择日期", size_hint=(0.94, 0.74), **kwargs)
        self.year, self.month = selected.year, selected.month
        self.callback = callback
        root = BoxLayout(orientation="vertical", padding=dp(8), spacing=dp(6))
        paint(root, PANEL)
        nav = BoxLayout(size_hint_y=None, height=dp(44), spacing=dp(6))
        nav.add_widget(button("‹", self.previous, size_hint_x=.24))
        self.title_label = label(halign="center")
        nav.add_widget(self.title_label)
        nav.add_widget(button("›", self.next, size_hint_x=.24))
        root.add_widget(nav)
        self.days = GridLayout(cols=7, spacing=dp(3))
        root.add_widget(self.days)
        self.content = root
        self.render()

    def previous(self, _):
        self.month -= 1
        if self.month == 0:
            self.year, self.month = self.year - 1, 12
        self.render()

    def next(self, _):
        self.month += 1
        if self.month == 13:
            self.year, self.month = self.year + 1, 1
        self.render()

    def render(self):
        self.title_label.text = f"{self.year} 年 {self.month} 月"
        self.days.clear_widgets()
        for name in "一二三四五六日":
            self.days.add_widget(label(name, GREEN, halign="center"))
        for week in calendar.monthcalendar(self.year, self.month):
            for number in week:
                if not number:
                    self.days.add_widget(Label())
                    continue
                day_button = Button(text=str(number), color=TEXT, background_normal="",
                                    background_color=(.20, .22, .24, 1))
                day_button.bind(on_release=lambda _btn, value=number: self.choose(value))
                self.days.add_widget(day_button)

    def choose(self, number):
        self.callback(date(self.year, self.month, number))
        self.dismiss()


class OvertimeRoot(BoxLayout):
    def __init__(self, data_path, holiday_path, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(7), padding=dp(10), **kwargs)
        paint(self, BG)
        self.data_path = Path(data_path)
        self.holidays = HolidayCalendar(holiday_path)
        self.selected_date = date.today()
        self.state = {"monthly_salary": 0.0, "records": []}
        self.selected_record_id = None
        self.load()

        self.add_widget(label("加班薪资记录仪", GREEN, size_hint_y=None, height=dp(42),
                              font_size="22sp", halign="center"))
        salary = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(6))
        self.salary_input = TextInput(text=str(self.state["monthly_salary"] or ""),
                                     hint_text="月基本工资（元）", multiline=False,
                                     input_filter="float", foreground_color=TEXT,
                                     hint_text_color=MUTED, background_normal="",
                                     background_color=PANEL)
        salary.add_widget(self.salary_input)
        salary.add_widget(button("保存底薪", self.save_salary, size_hint_x=.30))
        self.hourly = label(size_hint_x=.43, font_size="12sp", halign="center")
        salary.add_widget(self.hourly)
        self.add_widget(salary)

        form = GridLayout(cols=2, size_hint_y=None, height=dp(150), spacing=dp(6))
        form.add_widget(label("日期（读取手机系统日期）", halign="left"))
        self.date_button = button(self.selected_date.isoformat(), self.open_picker)
        form.add_widget(self.date_button)
        form.add_widget(label("加班时长（小时）", halign="left"))
        self.hours_input = TextInput(hint_text="例如 2.5", multiline=False,
                                    input_filter="float", foreground_color=TEXT,
                                    hint_text_color=MUTED, background_normal="",
                                    background_color=PANEL)
        form.add_widget(self.hours_input)
        form.add_widget(label("加班类型（可以手动修改）", halign="left"))
        self.type_spinner = Spinner(values=tuple(TYPE_MULTIPLIERS), color=TEXT,
                                    background_normal="", background_color=PANEL)
        form.add_widget(self.type_spinner)
        self.add_widget(form)
        self.add_widget(button("添加记录", self.add_record, size_hint_y=None, height=dp(44)))

        totals = BoxLayout(size_hint_y=None, height=dp(54))
        self.total_hours = label(halign="center")
        self.total_pay = label(color=GREEN, halign="center")
        totals.add_widget(self.total_hours)
        totals.add_widget(self.total_pay)
        self.add_widget(totals)

        header = BoxLayout(size_hint_y=None, height=dp(30))
        for text, width in zip(("日期", "时长", "类型", "加班费"), (.28, .16, .31, .25)):
            header.add_widget(label(text, GREEN, size_hint_x=width, halign="center"))
        self.add_widget(header)
        scroll = ScrollView()
        self.rows = GridLayout(cols=1, spacing=dp(2), size_hint_y=None)
        self.rows.bind(minimum_height=self.rows.setter("height"))
        scroll.add_widget(self.rows)
        self.add_widget(scroll)
        self.add_widget(button("删除选中记录", self.confirm_delete, danger=True,
                               size_hint_y=None, height=dp(42)))
        self.status = label("", MUTED, size_hint_y=None, height=dp(25),
                            font_size="11sp", halign="center")
        self.add_widget(self.status)
        self.update_hourly()
        self.apply_date_type(self.selected_date)
        self.refresh()

    def load(self):
        try:
            if self.data_path.exists():
                data = json.loads(self.data_path.read_text(encoding="utf-8"))
                if isinstance(data, dict):
                    self.state.update(data)
        except (OSError, ValueError, TypeError):
            pass

    def persist(self):
        try:
            self.data_path.parent.mkdir(parents=True, exist_ok=True)
            temp = self.data_path.with_suffix(".tmp")
            temp.write_text(json.dumps(self.state, ensure_ascii=False, indent=2), encoding="utf-8")
            temp.replace(self.data_path)
        except OSError as exc:
            self.message(f"保存失败：{exc}", True)

    def message(self, text, error=False):
        self.status.text = text
        self.status.color = RED if error else MUTED

    def hourly_rate(self):
        return float(self.state.get("monthly_salary", 0) or 0) / 21.75 / 8

    def update_hourly(self):
        self.hourly.text = f"当前时薪：{self.hourly_rate():.2f} 元/小时"

    def save_salary(self, _):
        try:
            value = float(self.salary_input.text)
            if value <= 0:
                raise ValueError
        except ValueError:
            self.message("请输入有效的月基本工资", True)
            return
        self.state["monthly_salary"] = value
        self.persist()
        self.update_hourly()
        self.message("底薪已保存")

    def open_picker(self, _):
        DatePickerPopup(self.selected_date, self.date_selected).open()

    def date_selected(self, chosen):
        self.selected_date = chosen
        self.date_button.text = chosen.isoformat()
        self.apply_date_type(chosen)

    def apply_date_type(self, chosen):
        day_type, reason = self.holidays.classify(chosen)
        self.type_spinner.text = day_type
        self.message(f"离线识别：{reason}；如单位安排不同可手动修改")

    def add_record(self, _):
        if self.hourly_rate() <= 0:
            self.message("请先保存月基本工资", True)
            return
        try:
            hours = float(self.hours_input.text)
            if not 0 < hours <= 24:
                raise ValueError
        except ValueError:
            self.message("请输入 0 到 24 之间的有效时长", True)
            return
        kind = self.type_spinner.text
        multiplier = TYPE_MULTIPLIERS.get(kind, 1.5)
        self.state.setdefault("records", []).append({
            "id": datetime.now().strftime("%Y%m%d%H%M%S%f"),
            "date": self.selected_date.isoformat(), "hours": round(hours, 2),
            "type": kind, "multiplier": multiplier,
            "pay": round(self.hourly_rate() * hours * multiplier, 2),
        })
        self.state["records"].sort(key=lambda row: (row["date"], row["id"]), reverse=True)
        self.persist()
        self.hours_input.text = ""
        self.selected_record_id = None
        self.refresh()
        self.message("记录已添加")

    def refresh(self):
        self.rows.clear_widgets()
        for record in self.state.get("records", []):
            row = Button(size_hint_y=None, height=dp(42), background_normal="",
                         background_color=PANEL, color=TEXT)
            row.record_id = record["id"]
            row.text = (f'{record["date"]}     {float(record["hours"]):g}h     '
                        f'{record["type"].replace(" ", "")}     ¥{float(record["pay"]):.2f}')
            row.bind(on_release=self.select_row)
            self.rows.add_widget(row)
        month = date.today().strftime("%Y-%m")
        current = [r for r in self.state.get("records", []) if r.get("date", "").startswith(month)]
        self.total_hours.text = f'本月累计\n{sum(float(r["hours"]) for r in current):.2f} 小时'
        self.total_pay.text = f'本月加班费\n¥{sum(float(r["pay"]) for r in current):.2f}'

    def select_row(self, selected):
        self.selected_record_id = selected.record_id
        for row in self.rows.children:
            row.background_color = (0.05, .35, .27, 1) if row.record_id == selected.record_id else PANEL
        self.message("已选择一条记录")

    def confirm_delete(self, _):
        if not self.selected_record_id:
            self.message("请先选择一条记录", True)
            return
        content = BoxLayout(orientation="vertical", padding=dp(12), spacing=dp(10))
        content.add_widget(label("确定删除选中的加班记录吗？", halign="center"))
        actions = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(8))
        popup = Popup(title="删除确认", content=content, size_hint=(.82, .34))
        actions.add_widget(button("取消", lambda _btn: popup.dismiss()))
        actions.add_widget(button("确认删除", lambda _btn: self.delete(popup), danger=True))
        content.add_widget(actions)
        popup.open()

    def delete(self, popup):
        self.state["records"] = [r for r in self.state.get("records", [])
                                 if r.get("id") != self.selected_record_id]
        self.selected_record_id = None
        self.persist()
        self.refresh()
        popup.dismiss()
        self.message("记录已删除")


class OvertimeRecorderApp(App):
    title = "加班薪资记录仪"

    def build(self):
        Window.clearcolor = BG
        project_dir = Path(__file__).resolve().parent
        return OvertimeRoot(Path(self.user_data_dir) / "overtime_data.json",
                            project_dir / "holidays.json")


if __name__ == "__main__":
    OvertimeRecorderApp().run()
