# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.lang import Builder

import db
from utils.farsi_text import rtl

Builder.load_string("""
<SettingsScreen>:
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
                text: root.tr("تنظیمات")
                color: 1, 1, 1, 1

        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "14dp"
                size_hint_y: None
                height: self.minimum_height

                RTLLabel:
                    text: root.tr("مبلغ حق عضویت ماهانه")
                    size_hint_y: None
                    height: "24dp"
                BoxLayout:
                    size_hint_y: None
                    height: "46dp"
                    spacing: "6dp"
                    RTLTextInput:
                        id: fee_field
                        input_type: "number"
                    RTLButton:
                        text: root.tr("ذخیره")
                        size_hint_x: None
                        width: "90dp"
                        on_release: root.save_fee()

                Widget:
                    size_hint_y: None
                    height: "10dp"

                RTLLabel:
                    text: root.tr("تغییر رمز عبور")
                    size_hint_y: None
                    height: "24dp"
                RTLTextInput:
                    id: new_pass_field
                    password: True
                    hint_text: root.tr("رمز عبور جدید")
                RTLTextInput:
                    id: confirm_pass_field
                    password: True
                    hint_text: root.tr("تکرار رمز عبور جدید")
                RTLButton:
                    text: root.tr("تغییر رمز عبور")
                    size_hint_y: None
                    height: "46dp"
                    on_release: root.change_password()

                Widget:
                    size_hint_y: None
                    height: "20dp"

                DangerButton:
                    text: root.tr("پاک کردن همه اطلاعات (بازنشانی)")
                    size_hint_y: None
                    height: "46dp"
                    on_release: root.confirm_reset()
""")


class SettingsScreen(Screen):
    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        self.ids.fee_field.text = str(db.get_monthly_fee())
        self.ids.new_pass_field.text = ""
        self.ids.confirm_pass_field.text = ""

    def save_fee(self):
        try:
            amount = float(self.ids.fee_field.text.strip())
        except ValueError:
            self._info(rtl("مبلغ نامعتبر است"))
            return
        db.set_monthly_fee(amount)
        self._info(rtl("مبلغ حق عضویت ذخیره شد"))

    def change_password(self):
        p1 = self.ids.new_pass_field.text
        p2 = self.ids.confirm_pass_field.text
        if not p1 or len(p1) < 4:
            self._info(rtl("رمز عبور باید حداقل ۴ کاراکتر باشد"))
            return
        if p1 != p2:
            self._info(rtl("رمز عبور و تکرار آن یکسان نیستند"))
            return
        db.change_password(p1)
        self.ids.new_pass_field.text = ""
        self.ids.confirm_pass_field.text = ""
        self._info(rtl("رمز عبور با موفقیت تغییر کرد"))

    def confirm_reset(self):
        content = BoxLayout(orientation="vertical", spacing="10dp", padding="10dp")
        content.add_widget(Label(
            text=rtl("تمام اعضا، حق عضویت‌ها، قرض‌ها و کمک‌ها برای همیشه حذف می‌شوند. این عمل "
                     "قابل بازگشت نیست. مطمئن هستید؟"),
            font_name="PersianFont", halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height="44dp", spacing="8dp")
        yes_btn = Button(text=rtl("بله، پاک کن"), font_name="PersianFont",
                          background_normal="", background_color=(0.75, 0.22, 0.22, 1))
        no_btn = Button(text=rtl("انصراف"), font_name="PersianFont",
                         background_normal="", background_color=(0.55, 0.55, 0.58, 1))
        btn_row.add_widget(yes_btn)
        btn_row.add_widget(no_btn)
        content.add_widget(btn_row)

        popup = Popup(title=rtl("تایید بازنشانی"), content=content,
                       size_hint=(0.9, 0.4), title_font="PersianFont")
        no_btn.bind(on_release=popup.dismiss)

        def do_reset(*_):
            db.reset_database()
            popup.dismiss()
            self._info(rtl("اطلاعات پاک شد"))

        yes_btn.bind(on_release=do_reset)
        popup.open()

    def _info(self, message):
        content = Label(text=message, font_name="PersianFont", halign="center")
        popup = Popup(title=rtl("پیام"), content=content,
                       size_hint=(0.85, 0.35), title_font="PersianFont")
        popup.open()
