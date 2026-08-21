# -*- coding: utf-8 -*-
import os
import shutil
from datetime import datetime

from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.app import App
from kivy.lang import Builder

import db
from utils.farsi_text import rtl

Builder.load_string("""
<BackupScreen>:
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
                text: root.tr("بکاپ و بازیابی")
                color: 1, 1, 1, 1

        BoxLayout:
            orientation: "vertical"
            padding: "16dp"
            spacing: "14dp"

            RTLLabel:
                text: root.tr("یک نسخه پشتیبان از فایل دیتابیس در حافظه‌ی گوشی ذخیره می‌شود. "
                              "توصیه می‌شود گاه‌گاهی این فایل را به جای امنی (ایمیل، گوگل‌درایو) منتقل کنید.")
                size_hint_y: None
                height: "90dp"

            RTLButton:
                text: root.tr("تهیه نسخه پشتیبان")
                size_hint_y: None
                height: "50dp"
                on_release: root.backup_now()

            RTLLabel:
                text: root.tr("برای بازیابی، فایل sandogh_backup.db را در پوشه‌ی زیر جایگزین "
                              "sandogh.db کنید و برنامه را دوباره باز کنید (یا از یک برنامه "
                              "مدیریت فایل روی گوشی استفاده کنید):")
                size_hint_y: None
                height: "90dp"

            RTLLabel:
                id: path_label
                text: ""
                size_hint_y: None
                height: "60dp"
                color: 0.3, 0.3, 0.3, 1
""")


class BackupScreen(Screen):
    def tr(self, text):
        return rtl(text)

    def on_pre_enter(self, *args):
        app = App.get_running_app()
        self.ids.path_label.text = rtl(app.user_data_dir)

    def backup_now(self):
        app = App.get_running_app()
        src = os.path.join(app.user_data_dir, "sandogh.db")
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(app.user_data_dir, f"sandogh_backup_{stamp}.db")
        try:
            shutil.copyfile(src, dst)
            self._info(rtl(f"نسخه پشتیبان ذخیره شد:\\n{dst}"))
        except Exception as e:
            self._info(rtl(f"خطا در تهیه نسخه پشتیبان: {e}"))

    def _info(self, message):
        content = Label(text=message, font_name="PersianFont", halign="center")
        popup = Popup(title=rtl("بکاپ"), content=content,
                       size_hint=(0.9, 0.4), title_font="PersianFont")
        popup.open()
