# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.lang import Builder

import db
from utils.farsi_text import rtl
from utils.jalali import today_str, is_valid_date

Builder.load_string("""
<LoanDetailScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("بازگشت")
                size_hint_x: None
                width: "90dp"
                background_color: 0.4, 0.4, 0.42, 1
                on_release: root.manager.current = "loans"
            TitleLabel:
                text: root.tr("جزئیات قرض")
                color: 1, 1, 1, 1

        RTLLabel:
            id: summary_label
            text: ""
            size_hint_y: None
            height: "90dp"

        BoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "8dp"
            RTLButton:
                text: root.tr("+ ثبت قسط بازپرداخت")
                on_release: root.open_payment_popup()

        ScrollView:
            GridLayout:
                id: payments_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: "2dp"
""")


class LoanDetailScreen(Screen):
    loan_id = None

    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        loan = db.get_loan(self.loan_id)
        if not loan:
            self.manager.current = "loans"
            return
        balance = db.get_loan_balance(self.loan_id)
        lines = [
            f"عضو: {loan['member_name']}",
            f"مبلغ قرض: {loan['amount']:,.0f}   -   تاریخ: {loan['date']}",
            f"باقی‌مانده: {balance:,.0f}",
        ]
        self.ids.summary_label.text = rtl("\\n".join(lines))

        container = self.ids.payments_list
        container.clear_widgets()
        payments = db.get_loan_payments(self.loan_id)
        if not payments:
            container.add_widget(Label(text=rtl("هنوز قسطی پرداخت نشده"), font_name="PersianFont",
                                        size_hint_y=None, height="50dp", color=(0.4, 0.4, 0.4, 1)))
            return
        for p in payments:
            row = Label(text=rtl(f"{p['amount']:,.0f}   -   {p['date']}"), font_name="PersianFont",
                        halign="right", valign="middle", size_hint_y=None, height="40dp")
            row.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
            container.add_widget(row)

    def open_payment_popup(self):
        content = BoxLayout(orientation="vertical", spacing="8dp", padding="12dp")
        content.add_widget(Label(text=rtl("مبلغ قسط"), font_name="PersianFont",
                                  size_hint_y=None, height="22dp"))
        amount_field = TextInput(font_name="PersianFont", halign="right", multiline=False,
                                  input_type="number", size_hint_y=None, height="42dp")
        content.add_widget(amount_field)

        content.add_widget(Label(text=rtl("تاریخ (سال-ماه-روز)"), font_name="PersianFont",
                                  size_hint_y=None, height="22dp"))
        date_field = TextInput(font_name="PersianFont", halign="right", multiline=False,
                                size_hint_y=None, height="42dp", text=today_str())
        content.add_widget(date_field)

        error_label = Label(text="", font_name="PersianFont", size_hint_y=None, height="22dp",
                             color=(0.75, 0.2, 0.2, 1))
        content.add_widget(error_label)

        save_btn = Button(text=rtl("ثبت"), font_name="PersianFont", size_hint_y=None, height="46dp",
                           background_normal="", background_color=(0.16, 0.45, 0.42, 1), color=(1, 1, 1, 1))
        content.add_widget(save_btn)

        popup = Popup(title=rtl("ثبت قسط بازپرداخت"), content=content,
                       size_hint=(0.85, 0.6), title_font="PersianFont")

        def save(*_):
            try:
                amount = float(amount_field.text.strip())
            except ValueError:
                error_label.text = rtl("مبلغ نامعتبر است")
                return
            date_val = date_field.text.strip()
            if not is_valid_date(date_val):
                error_label.text = rtl("تاریخ نامعتبر است")
                return
            db.add_loan_payment(self.loan_id, amount, date_val)
            popup.dismiss()
            self.refresh()

        save_btn.bind(on_release=save)
        popup.open()
