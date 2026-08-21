# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.button import Button
from kivy.lang import Builder

import db
from utils.farsi_text import rtl
from utils.jalali import DARI_MONTHS, today_str, today_ymd

Builder.load_string("""
<DuesScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("بازگشت")
                size_hint_x: None
                width: "90dp"
                background_color: 0.4, 0.4, 0.42, 1
                on_release: root.manager.current = "member_detail"
            TitleLabel:
                text: root.tr("حق عضویت")
                color: 1, 1, 1, 1

        BoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "8dp"
            spacing: "8dp"
            SecondaryButton:
                text: "-"
                size_hint_x: None
                width: "44dp"
                on_release: root.change_year(-1)
            RTLLabel:
                id: year_label
                text: ""
                halign: "center"
            SecondaryButton:
                text: "+"
                size_hint_x: None
                width: "44dp"
                on_release: root.change_year(1)

        ScrollView:
            GridLayout:
                id: month_grid
                cols: 3
                spacing: "8dp"
                padding: "12dp"
                size_hint_y: None
                height: self.minimum_height
                row_default_height: "70dp"
                row_force_default: True
""")


class DuesScreen(Screen):
    member_id = None

    def __init__(self, **kw):
        super().__init__(**kw)
        self.year = today_ymd()[0]

    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        self.year = today_ymd()[0]
        self.refresh()

    def change_year(self, delta):
        self.year += delta
        self.refresh()

    def refresh(self):
        self.ids.year_label.text = rtl(f"سال {self.year}")
        grid = self.ids.month_grid
        grid.clear_widgets()

        dues = db.get_dues_for_member_year(self.member_id, self.year)
        applicable = set(db.get_applicable_months(self.member_id, self.year))

        for month in range(1, 13):
            label = f"{DARI_MONTHS[month - 1]}"
            paid = dues[month]["paid"]
            is_applicable = month in applicable

            btn = Button(text=rtl(label), font_name="PersianFont",
                         background_normal="")
            if not is_applicable:
                btn.background_color = (0.85, 0.85, 0.85, 1)
                btn.color = (0.6, 0.6, 0.6, 1)
                btn.disabled = True
            elif paid:
                btn.background_color = (0.25, 0.6, 0.35, 1)
                btn.color = (1, 1, 1, 1)
            else:
                btn.background_color = (0.85, 0.4, 0.35, 1)
                btn.color = (1, 1, 1, 1)

            btn.bind(on_release=lambda inst, mo=month, is_paid=paid: self.toggle(mo, is_paid))
            grid.add_widget(btn)

    def toggle(self, month, currently_paid):
        new_state = not currently_paid
        paid_date = today_str() if new_state else None
        db.set_due_paid(self.member_id, self.year, month, new_state, paid_date)
        self.refresh()
