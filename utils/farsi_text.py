# -*- coding: utf-8 -*-
"""
کیوی به‌صورت پیش‌فرض حروف فارسی/دری را به هم متصل نمی‌کند و جهت راست‌به‌چپ را
رعایت نمی‌کند. این تابع کمکی از arabic_reshaper و python-bidi (همان دو کتابخانه‌ای
که در نسخه دسکتاپ برای خروجی PDF استفاده شده بودند) برای اصلاح نمایش متن فارسی/دری
در تمام Label ها و Button ها استفاده می‌کند.

استفاده: هرجا متن فارسی روی صفحه نشان داده می‌شود، آن را با rtl() یا میان‌بر
کوتاه‌تر f() پوشش دهید:  text: f("سلام دنیا")
"""
import arabic_reshaper
from bidi.algorithm import get_display

_reshaper_config = arabic_reshaper.config_for_true_type_font(
    None, arabic_reshaper.ENABLE_ALL_LIGATURES
) if False else None

_reshaper = arabic_reshaper.ArabicReshaper({
    "delete_harakat": False,
    "support_ligatures": True,
    "language": "Farsi",
})


def rtl(text):
    """متن فارسی/دری را برای نمایش صحیح در Kivy آماده می‌کند (شکل‌دهی حروف + جهت)."""
    if text is None:
        return ""
    text = str(text)
    try:
        reshaped = _reshaper.reshape(text)
        return get_display(reshaped)
    except Exception:
        return text


# میان‌بر کوتاه برای استفاده راحت‌تر در کد و فایل‌های kv (از طریق Builder)
f = rtl
