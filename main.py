# -*- coding: utf-8 -*-
"""
سیستم مدیریت صندوق اتحادیه - نسخه موبایل (اندروید)
نقطه ورود برنامه
"""
import os
from kivy.app import App
from kivy.lang import Builder
from kivy.core.text import LabelBase
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition

import db

# --- ثبت فونت فارسی ---------------------------------------------------
# توجه: باید فایل‌های فونت فارسی (مثلاً Vazirmatn) را خودتان در پوشه‌ی
# fonts/ قرار دهید؛ به fonts/README.md مراجعه کنید. بدون این فونت،
# حروف فارسی/دری به‌درستی نمایش داده نمی‌شوند (تُهی/جدا از هم دیده می‌شوند).
FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
_regular = os.path.join(FONT_DIR, "Vazir.ttf")
_bold = os.path.join(FONT_DIR, "Vazir-Bold.ttf")

if os.path.exists(_regular):
    LabelBase.register(name="PersianFont", fn_regular=_regular,
                        fn_bold=_bold if os.path.exists(_bold) else _regular)
else:
    # سقوط ایمن به فونت پیش‌فرض کیوی تا برنامه کرش نکند (اما فارسی درست نمایش نمی‌یابد)
    LabelBase.register(name="PersianFont",
                        fn_regular=LabelBase.get_default_font())
    print("⚠️  فونت فارسی پیدا نشد! به fonts/README.md مراجعه کنید.")

Builder.load_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "style.kv"))

# وارد کردن صفحات پس از ثبت فونت (چون هر صفحه kv خودش را لود می‌کند)
from screens.login_screen import LoginScreen
from screens.dashboard_screen import DashboardScreen
from screens.members_screen import MembersScreen
from screens.member_form_screen import MemberFormScreen
from screens.member_detail_screen import MemberDetailScreen
from screens.dues_screen import DuesScreen
from screens.loans_screen import LoansScreen
from screens.loan_detail_screen import LoanDetailScreen
from screens.aid_screen import AidScreen
from screens.fund_screen import FundScreen
from screens.settings_screen import SettingsScreen
from screens.backup_screen import BackupScreen


class SandoghApp(App):
    title = "صندوق اتحادیه"

    def build(self):
        Window.clearcolor = (0.96, 0.96, 0.94, 1)

        # دیتابیس در پوشه‌ی اختصاصی و امن اپ روی گوشی ذخیره می‌شود
        db_path = os.path.join(self.user_data_dir, "sandogh.db")
        db.init_app_db(db_path)
        db.init_db()

        sm = ScreenManager(transition=FadeTransition(duration=0.15))
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(DashboardScreen(name="dashboard"))
        sm.add_widget(MembersScreen(name="members"))
        sm.add_widget(MemberFormScreen(name="member_form"))
        sm.add_widget(MemberDetailScreen(name="member_detail"))
        sm.add_widget(DuesScreen(name="dues"))
        sm.add_widget(LoansScreen(name="loans"))
        sm.add_widget(LoanDetailScreen(name="loan_detail"))
        sm.add_widget(AidScreen(name="aid"))
        sm.add_widget(FundScreen(name="fund"))
        sm.add_widget(SettingsScreen(name="settings"))
        sm.add_widget(BackupScreen(name="backup"))
        sm.current = "login"
        return sm


if __name__ == "__main__":
    SandoghApp().run()
