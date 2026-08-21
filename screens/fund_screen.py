# -*- coding: utf-8 -*-
import os
import csv
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.lang import Builder

import db
from utils.farsi_text import rtl

Builder.load_string("""
<FundScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("بازگشت")
                size_hint_x: None
                width: "90dp"
                background_color: 0.4, 0.4, 0.42, 1
                on_release: root.manager.current = "dashboard"
            TitleLabel:
                text: root.tr("صندوق و گزارش‌ها")
                color: 1, 1, 1, 1

        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "10dp"
                size_hint_y: None
                height: self.minimum_height

                RTLLabel:
                    id: summary_label
                    text: ""
                    size_hint_y: None
                    height: "220dp"
                    font_size: "17sp"

                RTLButton:
                    text: root.tr("خروجی CSV از تراکنش‌ها")
                    size_hint_y: None
                    height: "50dp"
                    on_release: root.export_csv()

                RTLLabel:
                    text: root.tr("آخرین تراکنش‌ها")
                    size_hint_y: None
                    height: "30dp"
                    bold: True

                GridLayout:
                    id: ledger_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: "2dp"
""")


class FundScreen(Screen):
    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        balance = db.get_fund_balance()
        dues_total = db.total_dues_collected()
        aid_in = db.total_aid_received()
        aid_out = db.total_aid_given()
        loans_out = db.total_loans_given()
        loan_repay = db.total_loan_repayments()
        loans_outstanding = db.total_loans_outstanding()

        lines = [
            f"موجودی فعلی صندوق: {balance:,.0f}",
            "",
            f"مجموع حق عضویت دریافتی: {dues_total:,.0f}",
            f"مجموع کمک دریافتی: {aid_in:,.0f}",
            f"مجموع اقساط بازپرداختی: {loan_repay:,.0f}",
            f"مجموع کمک اهدائی: {aid_out:,.0f}",
            f"مجموع قرض‌های پرداختی: {loans_out:,.0f}",
            f"مانده قرض‌های در جریان: {loans_outstanding:,.0f}",
        ]
        self.ids.summary_label.text = rtl("\\n".join(lines))

        container = self.ids.ledger_list
        container.clear_widgets()
        ledger = db.get_transactions_ledger()
        recent = ledger[-25:][::-1]
        if not recent:
            container.add_widget(Label(text=rtl("تراکنشی ثبت نشده"), font_name="PersianFont",
                                        size_hint_y=None, height="50dp", color=(0.4, 0.4, 0.4, 1)))
            return
        for t in recent:
            sign = "+" if t["in"] else "-"
            amount = t["in"] or t["out"]
            text = f"{t['type']}   {sign}{amount:,.0f}\\n{t['desc']}   -   {t['date']}"
            lbl = Label(text=rtl(text), font_name="PersianFont", halign="right", valign="middle",
                        size_hint_y=None, height="54dp")
            lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
            container.add_widget(lbl)

    def export_csv(self):
        ledger = db.get_transactions_ledger()
        app = App.get_running_app()
        out_dir = app.user_data_dir
        out_path = os.path.join(out_dir, "sandogh_transactions.csv")
        try:
            with open(out_path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f)
                writer.writerow(["تاریخ", "نوع", "شرح", "دریافتی", "پرداختی"])
                for t in ledger:
                    writer.writerow([t["date"], t["type"], t["desc"], t["in"] or "", t["out"] or ""])
            self._info(rtl(f"فایل ذخیره شد در:\\n{out_path}"))
        except Exception as e:
            self._info(rtl(f"خطا در ذخیره فایل: {e}"))

    def _info(self, message):
        content = Label(text=message, font_name="PersianFont", halign="center")
        popup = Popup(title=rtl("خروجی گزارش"), content=content,
                       size_hint=(0.9, 0.4), title_font="PersianFont")
        popup.open()
