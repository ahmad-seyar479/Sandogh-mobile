# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.popup import Popup
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder

import db
from utils.farsi_text import rtl

Builder.load_string("""
<MemberDetailScreen>:
    BoxLayout:
        orientation: "vertical"

        TopBar:
            RTLButton:
                text: root.tr("بازگشت")
                size_hint_x: None
                width: "90dp"
                background_color: 0.4, 0.4, 0.42, 1
                on_release: root.manager.current = "members"
            TitleLabel:
                id: name_label
                text: ""
                color: 1, 1, 1, 1

        ScrollView:
            BoxLayout:
                orientation: "vertical"
                padding: "16dp"
                spacing: "10dp"
                size_hint_y: None
                height: self.minimum_height

                RTLLabel:
                    id: info_label
                    text: ""
                    size_hint_y: None
                    height: "120dp"

                RTLButton:
                    text: root.tr("حق عضویت / جدول ماهانه")
                    size_hint_y: None
                    height: "50dp"
                    on_release: root.goto_dues()

                RTLButton:
                    text: root.tr("قرض‌های این عضو")
                    size_hint_y: None
                    height: "50dp"
                    on_release: root.goto_loans()

                RTLButton:
                    text: root.tr("ویرایش اطلاعات")
                    size_hint_y: None
                    height: "50dp"
                    background_color: 0.55, 0.55, 0.58, 1
                    on_release: root.edit_member()

                DangerButton:
                    text: root.tr("حذف عضو")
                    size_hint_y: None
                    height: "50dp"
                    on_release: root.confirm_delete()
""")


class MemberDetailScreen(Screen):
    member_id = None

    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        m = db.get_member(self.member_id)
        if not m:
            self.manager.current = "members"
            return
        self.ids.name_label.text = rtl(m["name"])
        lines = [
            f"نام پدر: {m['father_name'] or '-'}",
            f"شماره تماس: {m['phone'] or '-'}",
            f"آدرس: {m['address'] or '-'}",
            f"تاریخ عضویت: {m['join_date'] or '-'}",
        ]
        self.ids.info_label.text = rtl("\\n".join(lines))

    def goto_dues(self):
        dues = self.manager.get_screen("dues")
        dues.member_id = self.member_id
        self.manager.current = "dues"

    def goto_loans(self):
        loans = self.manager.get_screen("loans")
        loans.member_id = self.member_id
        self.manager.current = "loans"

    def edit_member(self):
        form = self.manager.get_screen("member_form")
        form.member_id = self.member_id
        self.manager.current = "member_form"

    def confirm_delete(self):
        content = BoxLayout(orientation="vertical", spacing="10dp", padding="10dp")
        content.add_widget(Label(
            text=rtl("این عضو و تمام سوابق او (حق عضویت، قرض، کمک) حذف می‌شود. مطمئن هستید؟"),
            font_name="PersianFont", halign="center"))
        btn_row = BoxLayout(size_hint_y=None, height="44dp", spacing="8dp")
        from kivy.uix.button import Button
        yes_btn = Button(text=rtl("بله، حذف شود"), font_name="PersianFont",
                          background_normal="", background_color=(0.75, 0.22, 0.22, 1))
        no_btn = Button(text=rtl("انصراف"), font_name="PersianFont",
                         background_normal="", background_color=(0.55, 0.55, 0.58, 1))
        btn_row.add_widget(yes_btn)
        btn_row.add_widget(no_btn)
        content.add_widget(btn_row)

        popup = Popup(title=rtl("تایید حذف"), content=content,
                       size_hint=(0.85, 0.4), title_font="PersianFont")
        no_btn.bind(on_release=popup.dismiss)

        def do_delete(*_):
            db.delete_member(self.member_id)
            popup.dismiss()
            self.manager.current = "members"

        yes_btn.bind(on_release=do_delete)
        popup.open()
