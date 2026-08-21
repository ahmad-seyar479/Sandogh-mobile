# -*- coding: utf-8 -*-
from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.lang import Builder

import db
from utils.farsi_text import rtl

Builder.load_string("""
<LoginScreen>:
    BoxLayout:
        orientation: "vertical"
        padding: "32dp"
        spacing: "16dp"
        canvas.before:
            Color:
                rgba: 0.16, 0.45, 0.42, 1
            Rectangle:
                pos: self.pos
                size: self.size

        Widget:
            size_hint_y: 0.3

        TitleLabel:
            text: root.tr("صندوق اتحادیه")
            color: 1, 1, 1, 1
            size_hint_y: None
            height: "48dp"

        Widget:
            size_hint_y: 0.1

        BoxLayout:
            orientation: "vertical"
            spacing: "14dp"
            size_hint_y: None
            height: "220dp"
            canvas.before:
                Color:
                    rgba: 1, 1, 1, 1
                RoundedRectangle:
                    pos: self.pos
                    size: self.size
                    radius: [16]
            padding: "20dp"

            RTLLabel:
                text: root.tr("نام کاربری")
                size_hint_y: None
                height: "24dp"
            RTLTextInput:
                id: username
                text: "admin"
            RTLLabel:
                text: root.tr("رمز عبور")
                size_hint_y: None
                height: "24dp"
            RTLTextInput:
                id: password
                password: True
                text: "admin"

        RTLButton:
            text: root.tr("ورود")
            size_hint_y: None
            height: "50dp"
            on_release: root.do_login(username.text, password.text)

        Widget:
""")


class LoginScreen(Screen):
    def tr(self, text):
        return rtl(text)

    def do_login(self, username, password):
        if db.check_login(username, password):
            self.ids.username.text = ""
            self.ids.password.text = ""
            self.manager.current = "dashboard"
        else:
            self._error(rtl("نام کاربری یا رمز عبور اشتباه است"))

    def _error(self, message):
        content = Label(text=message, font_name="PersianFont", halign="center")
        popup = Popup(title=rtl("خطا"), content=content,
                       size_hint=(0.8, 0.3), title_font="PersianFont")
        popup.open()
