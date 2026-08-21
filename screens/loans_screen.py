# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.lang import Builder

import db
from utils.farsi_text import rtl
from utils.jalali import today_str, is_valid_date

Builder.load_string("""
<LoansScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("بازگشت")
                size_hint_x: None
                width: "90dp"
                background_color: 0.4, 0.4, 0.42, 1
                on_release: root.go_back()
            TitleLabel:
                text: root.tr("قرض‌ها")
                color: 1, 1, 1, 1

        BoxLayout:
            size_hint_y: None
            height: "56dp"
            padding: "8dp"
            RTLButton:
                text: root.tr("+ ثبت قرض جدید")
                on_release: root.open_add_popup()

        ScrollView:
            GridLayout:
                id: loan_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: "2dp"
""")


class LoansScreen(Screen):
    member_id = None  # اگر تنظیم شده باشد، فقط قرض‌های همین عضو

    def tr(self, text):
        return rtl(text)

    def go_back(self):
        if self.member_id:
            self.manager.current = "member_detail"
        else:
            self.manager.current = "dashboard"

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        container = self.ids.loan_list
        container.clear_widgets()
        loans = db.get_loans_for_member(self.member_id) if self.member_id else db.get_all_loans()
        if not loans:
            container.add_widget(Label(text=rtl("قرضی ثبت نشده"), font_name="PersianFont",
                                        size_hint_y=None, height="60dp", color=(0.4, 0.4, 0.4, 1)))
            return
        for loan in loans:
            container.add_widget(self._build_row(loan))

    def _build_row(self, loan):
        row = BoxLayout(size_hint_y=None, height="70dp", padding=[10, 6], spacing=8)
        balance = db.get_loan_balance(loan["id"])
        name = loan["member_name"] if "member_name" in loan.keys() else ""
        text = f"{name}   {loan['amount']:,.0f}   -   باقی‌مانده: {balance:,.0f}\\n{loan['date']}"
        info = Label(text=rtl(text), font_name="PersianFont", halign="right", valign="middle")
        info.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
        row.add_widget(info)
        open_btn = Button(text=rtl("جزئیات"), font_name="PersianFont",
                           size_hint_x=None, width="90dp",
                           background_normal="", background_color=(0.16, 0.45, 0.42, 1))
        open_btn.bind(on_release=lambda *_: self.open_loan(loan["id"]))
        row.add_widget(open_btn)
        return row

    def open_loan(self, loan_id):
        detail = self.manager.get_screen("loan_detail")
        detail.loan_id = loan_id
        self.manager.current = "loan_detail"

    def open_add_popup(self):
        content = BoxLayout(orientation="vertical", spacing="8dp", padding="12dp")

        member_name_display = None
        chosen_member_id = self.member_id

        if not self.member_id:
            content.add_widget(Label(text=rtl("نام عضو (دقیق یا بخشی از نام)"),
                                      font_name="PersianFont", size_hint_y=None, height="22dp"))
            search_field = _make_input()
            content.add_widget(search_field)
            result_label = Label(text=rtl("نتیجه‌ای انتخاب نشده"), font_name="PersianFont",
                                  size_hint_y=None, height="26dp", color=(0.4, 0.4, 0.4, 1))
            content.add_widget(result_label)
            results_box = BoxLayout(orientation="vertical", size_hint_y=None, height="90dp")
            content.add_widget(results_box)

            state = {"member_id": None}

            def do_search(*_):
                results_box.clear_widgets()
                q = search_field.text.strip()
                if not q:
                    return
                for m in db.search_members(q)[:4]:
                    b = Button(text=rtl(m["name"]), font_name="PersianFont", size_hint_y=None, height="30dp")

                    def pick(inst, mid=m["id"], mname=m["name"]):
                        state["member_id"] = mid
                        result_label.text = rtl(f"انتخاب شد: {mname}")

                    b.bind(on_release=pick)
                    results_box.add_widget(b)

            search_field.bind(text=do_search)
        else:
            state = {"member_id": self.member_id}

        content.add_widget(Label(text=rtl("مبلغ قرض"), font_name="PersianFont",
                                  size_hint_y=None, height="22dp"))
        amount_field = _make_input(input_type="number")
        content.add_widget(amount_field)

        content.add_widget(Label(text=rtl("تاریخ (سال-ماه-روز)"), font_name="PersianFont",
                                  size_hint_y=None, height="22dp"))
        date_field = _make_input()
        date_field.text = today_str()
        content.add_widget(date_field)

        content.add_widget(Label(text=rtl("یادداشت (اختیاری)"), font_name="PersianFont",
                                  size_hint_y=None, height="22dp"))
        note_field = _make_input()
        content.add_widget(note_field)

        error_label = Label(text="", font_name="PersianFont", size_hint_y=None, height="22dp",
                             color=(0.75, 0.2, 0.2, 1))
        content.add_widget(error_label)

        save_btn = Button(text=rtl("ثبت قرض"), font_name="PersianFont", size_hint_y=None, height="46dp",
                           background_normal="", background_color=(0.16, 0.45, 0.42, 1), color=(1, 1, 1, 1))
        content.add_widget(save_btn)

        popup = Popup(title=rtl("ثبت قرض جدید"), content=content,
                       size_hint=(0.9, 0.85), title_font="PersianFont")

        def save(*_):
            mid = state["member_id"]
            if not mid:
                error_label.text = rtl("لطفاً یک عضو انتخاب کنید")
                return
            try:
                amount = float(amount_field.text.strip())
            except ValueError:
                error_label.text = rtl("مبلغ نامعتبر است")
                return
            date_val = date_field.text.strip()
            if not is_valid_date(date_val):
                error_label.text = rtl("تاریخ نامعتبر است")
                return
            db.add_loan(mid, amount, date_val, note_field.text.strip())
            popup.dismiss()
            self.refresh()

        save_btn.bind(on_release=save)
        popup.open()


def _make_input(input_type="text"):
    from kivy.uix.textinput import TextInput
    ti = TextInput(font_name="PersianFont", halign="right", multiline=False,
                    input_type=input_type, size_hint_y=None, height="42dp")
    return ti
