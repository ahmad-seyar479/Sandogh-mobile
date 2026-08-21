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
<AidScreen>:
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
                text: root.tr("کمک‌ها")
                color: 1, 1, 1, 1

        BoxLayout:
            size_hint_y: None
            height: "48dp"
            padding: "6dp"
            spacing: "6dp"
            RTLButton:
                id: tab_received
                text: root.tr("کمک دریافتی")
                on_release: root.switch_tab("received")
            RTLButton:
                id: tab_given
                text: root.tr("کمک اهدائی")
                on_release: root.switch_tab("given")

        BoxLayout:
            size_hint_y: None
            height: "50dp"
            padding: "8dp"
            RTLButton:
                text: root.tr("+ ثبت جدید")
                on_release: root.open_add_popup()

        ScrollView:
            GridLayout:
                id: aid_list
                cols: 1
                size_hint_y: None
                height: self.minimum_height
                spacing: "2dp"
""")


class AidScreen(Screen):
    tab = "received"

    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        self.switch_tab(self.tab)

    def switch_tab(self, tab):
        self.tab = tab
        active = (0.16, 0.45, 0.42, 1)
        inactive = (0.6, 0.6, 0.62, 1)
        self.ids.tab_received.background_color = active if tab == "received" else inactive
        self.ids.tab_given.background_color = active if tab == "given" else inactive
        self.refresh()

    def refresh(self):
        container = self.ids.aid_list
        container.clear_widgets()
        if self.tab == "received":
            rows = db.get_all_aid_received()
            empty_text = "کمک دریافتی ثبت نشده"
        else:
            rows = db.get_all_aid_given()
            empty_text = "کمک اهدائی ثبت نشده"

        if not rows:
            container.add_widget(Label(text=rtl(empty_text), font_name="PersianFont",
                                        size_hint_y=None, height="60dp", color=(0.4, 0.4, 0.4, 1)))
            return

        for r in rows:
            if self.tab == "received":
                text = f"{r['donor_name'] or '-'}   {r['amount']:,.0f}\\n{r['date']}"
            else:
                text = f"{r['member_name']}   {r['amount']:,.0f}\\n{r['date']}"
            lbl = Label(text=rtl(text), font_name="PersianFont", halign="right", valign="middle",
                        size_hint_y=None, height="56dp")
            lbl.bind(size=lambda w, *_: setattr(w, "text_size", w.size))
            container.add_widget(lbl)

    def open_add_popup(self):
        if self.tab == "received":
            self._popup_received()
        else:
            self._popup_given()

    def _popup_received(self):
        content = BoxLayout(orientation="vertical", spacing="8dp", padding="12dp")
        content.add_widget(Label(text=rtl("نام اهداکننده"), font_name="PersianFont",
                                  size_hint_y=None, height="22dp"))
        donor_field = TextInput(font_name="PersianFont", halign="right", multiline=False,
                                 size_hint_y=None, height="42dp")
        content.add_widget(donor_field)

        content.add_widget(Label(text=rtl("مبلغ"), font_name="PersianFont",
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

        popup = Popup(title=rtl("ثبت کمک دریافتی"), content=content,
                       size_hint=(0.9, 0.7), title_font="PersianFont")

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
            db.add_aid_received(amount, date_val, donor_field.text.strip())
            popup.dismiss()
            self.refresh()

        save_btn.bind(on_release=save)
        popup.open()

    def _popup_given(self):
        content = BoxLayout(orientation="vertical", spacing="8dp", padding="12dp")
        content.add_widget(Label(text=rtl("نام عضو (بخشی از نام کافی است)"), font_name="PersianFont",
                                  size_hint_y=None, height="22dp"))
        search_field = TextInput(font_name="PersianFont", halign="right", multiline=False,
                                  size_hint_y=None, height="42dp")
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

        content.add_widget(Label(text=rtl("مبلغ"), font_name="PersianFont",
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

        popup = Popup(title=rtl("ثبت کمک اهدائی"), content=content,
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
            try:
                db.add_aid_given(mid, amount, date_val)
            except ValueError as e:
                error_label.text = rtl(str(e))
                return
            popup.dismiss()
            self.refresh()

        save_btn.bind(on_release=save)
        popup.open()
