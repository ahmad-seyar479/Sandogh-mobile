# -*- coding: utf-8 -*-
"""کمک‌توابع تاریخ شمسی/دری - بر پایه jdatetime، همانند نسخه دسکتاپ."""
import jdatetime

DARI_MONTHS = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
               "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]


def today_str():
    """تاریخ امروز به فرمت YYYY-MM-DD شمسی."""
    today = jdatetime.date.today()
    return today.strftime("%Y-%m-%d")


def today_ymd():
    today = jdatetime.date.today()
    return today.year, today.month, today.day


def is_valid_date(text):
    """بررسی می‌کند رشته به‌فرمت ۱۴۰۵-۰۱-۰۱ (سال-ماه-روز) معتبر است یا نه."""
    try:
        parts = str(text).strip().split("-")
        if len(parts) != 3:
            return False
        y, m, d = int(parts[0]), int(parts[1]), int(parts[2])
        jdatetime.date(y, m, d)
        return True
    except (ValueError, TypeError):
        return False


def month_name(month_number):
    try:
        return DARI_MONTHS[int(month_number) - 1]
    except (IndexError, ValueError, TypeError):
        return str(month_number)
