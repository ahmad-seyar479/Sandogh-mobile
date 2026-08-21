# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.lang import Builder

import db
from utils.farsi_text import rtl

Builder.load_string("""
<DashboardScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("خروج")
                size_hint_x: None
                width: "90dp"
                background_color: 0.75, 0.22, 0.22, 1
                on_release: root.logout()
            TitleLabel:
                text: root.tr("صندوق اتحادیه")
                color: 1, 1, 1, 1

        RTLLabel:
            id: balance_label
            text: root.tr("موجودی صندوق: ...")
            size_hint_y: None
            height: "60dp"
            font_size: "20sp"
            bold: True
            halign: "center"
            color: 0.12, 0.35, 0.32, 1

        ScrollView:
            GridLayout:
                cols: 2
                spacing: "14dp"
                padding: "16dp"
                size_hint_y: None
                height: self.minimum_height
                row_default_height: "110dp"
                row_force_default: True

                RTLButton:
                    text: root.tr("اعضا")
                    on_release: root.goto("members")
                RTLButton:
                    text: root.tr("قرض‌ها")
                    on_release: root.goto("loans")
                RTLButton:
                    text: root.tr("کمک‌ها")
                    on_release: root.goto("aid")
                RTLButton:
                    text: root.tr("صندوق و گزارش‌ها")
                    on_release: root.goto("fund")
                RTLButton:
                    text: root.tr("تنظیمات")
                    on_release: root.goto("settings")
                RTLButton:
                    text: root.tr("بکاپ و بازیابی")
                    on_release: root.goto("backup")
""")


class DashboardScreen(Screen):
    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        balance = db.get_fund_balance()
        self.ids.balance_label.text = rtl(f"موجودی صندوق: {balance:,.0f}")

    def goto(self, screen_name):
        self.manager.current = screen_name

    def logout(self):
        self.manager.current = "login"
