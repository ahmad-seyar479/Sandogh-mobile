# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder

import db
from utils.farsi_text import rtl
from utils.jalali import is_valid_date, today_str

Builder.load_string("""
<MemberFormScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("انصراف")
                size_hint_x: None
                width: "90dp"
                background_color: 0.4, 0.4, 0.42, 1
                on_release: root.manager.current = "members"
            TitleLabel:
                id: form_title
                text: root.tr("عضو جدید")
                color: 1, 1, 1, 1

        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "10dp"
                size_hint_y: None
                height: self.minimum_height

                RTLLabel:
                    text: root.tr("نام کامل *")
                    size_hint_y: None
                    height: "22dp"
                RTLTextInput:
                    id: name_field
                    size_hint_y: None
                    height: "46dp"

                RTLLabel:
                    text: root.tr("نام پدر")
                    size_hint_y: None
                    height: "22dp"
                RTLTextInput:
                    id: father_field
                    size_hint_y: None
                    height: "46dp"

                RTLLabel:
                    text: root.tr("شماره تماس")
                    size_hint_y: None
                    height: "22dp"
                RTLTextInput:
                    id: phone_field
                    input_type: "number"
                    size_hint_y: None
                    height: "46dp"

                RTLLabel:
                    text: root.tr("آدرس")
                    size_hint_y: None
                    height: "22dp"
                RTLTextInput:
                    id: address_field
                    size_hint_y: None
                    height: "46dp"

                RTLLabel:
                    text: root.tr("تاریخ عضویت (سال-ماه-روز، مثلاً ۱۴۰۵-۰۱-۰۱)")
                    size_hint_y: None
                    height: "22dp"
                BoxLayout:
                    size_hint_y: None
                    height: "46dp"
                    spacing: "6dp"
                    RTLTextInput:
                        id: join_date_field
                    SecondaryButton:
                        text: root.tr("امروز")
                        size_hint_x: None
                        width: "80dp"
                        on_release: root.set_today()

                Widget:
                    size_hint_y: None
                    height: "10dp"

                RTLButton:
                    text: root.tr("ذخیره")
                    size_hint_y: None
                    height: "50dp"
                    on_release: root.save()
""")


class MemberFormScreen(Screen):
    member_id = None

    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        if self.member_id:
            self.ids.form_title.text = rtl("ویرایش عضو")
            m = db.get_member(self.member_id)
            self.ids.name_field.text = m["name"] or ""
            self.ids.father_field.text = m["father_name"] or ""
            self.ids.phone_field.text = m["phone"] or ""
            self.ids.address_field.text = m["address"] or ""
            self.ids.join_date_field.text = m["join_date"] or ""
        else:
            self.ids.form_title.text = rtl("عضو جدید")
            self.ids.name_field.text = ""
            self.ids.father_field.text = ""
            self.ids.phone_field.text = ""
            self.ids.address_field.text = ""
            self.ids.join_date_field.text = ""

    def set_today(self):
        self.ids.join_date_field.text = today_str()

    def save(self):
        name = self.ids.name_field.text.strip()
        if not name:
            self._error(rtl("نام عضو الزامی است"))
            return
        join_date = self.ids.join_date_field.text.strip()
        if join_date and not is_valid_date(join_date):
            self._error(rtl("فرمت تاریخ عضویت درست نیست (سال-ماه-روز)"))
            return

        father = self.ids.father_field.text.strip()
        phone = self.ids.phone_field.text.strip()
        address = self.ids.address_field.text.strip()

        if self.member_id:
            db.update_member(self.member_id, name, father, phone, address, join_date or None)
        else:
            db.add_member(name, father, phone, address, join_date or None)

        self.manager.current = "members"

    def _error(self, message):
        content = Label(text=message, font_name="PersianFont", halign="center")
        popup = Popup(title=rtl("خطا"), content=content,
                       size_hint=(0.8, 0.3), title_font="PersianFont")
        popup.open()
