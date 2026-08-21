# -*- coding: utf-8 -*-
"""
لایه دیتابیس سیستم مدیریت صندوق اتحادیه - نسخه موبایل
تمام دسترسی به SQLite از این ماژول انجام می‌شود.
منطق این فایل عیناً از نسخه دسکتاپ (database.py) گرفته شده؛ تنها تفاوت،
محل ذخیره فایل دیتابیس است که با init_app_db() از مسیر اختصاصی اپ روی
گوشی (user_data_dir در کیوی) تنظیم می‌شود.
"""
import sqlite3
import os
import hashlib
import secrets

DARI_MONTHS = ["حمل", "ثور", "جوزا", "سرطان", "اسد", "سنبله",
               "میزان", "عقرب", "قوس", "جدی", "دلو", "حوت"]

# مقداردهی واقعی در main.py با init_app_db(path) انجام می‌شود
DB_PATH = "sandogh.db"


def init_app_db(path):
    """مسیر فایل دیتابیس را روی مسیر اختصاصی اپ (Android/iOS/desktop) تنظیم می‌کند."""
    global DB_PATH
    DB_PATH = path


def get_connection(db_path=None):
    conn = sqlite3.connect(db_path or DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    h = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
    return salt, h


def verify_password(password, salt, stored_hash):
    _, h = hash_password(password, salt)
    return h == stored_hash


def init_db(db_path=None):
    """Create all tables if they don't exist, and seed default admin/settings."""
    conn = get_connection(db_path)
    cur = conn.cursor()

    cur.executescript("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    );

    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        father_name TEXT,
        phone TEXT,
        address TEXT,
        join_date TEXT,
        created_at TEXT DEFAULT (datetime('now'))
    );

    CREATE TABLE IF NOT EXISTS dues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
        year INTEGER NOT NULL,
        month INTEGER NOT NULL,
        paid INTEGER NOT NULL DEFAULT 0,
        paid_date TEXT,
        UNIQUE(member_id, year, month)
    );

    CREATE TABLE IF NOT EXISTS loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        note TEXT
    );

    CREATE TABLE IF NOT EXISTS loan_payments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        loan_id INTEGER NOT NULL REFERENCES loans(id) ON DELETE CASCADE,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS aid_received (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        amount REAL NOT NULL,
        date TEXT NOT NULL,
        donor_name TEXT
    );

    CREATE TABLE IF NOT EXISTS aid_given (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        member_id INTEGER NOT NULL REFERENCES members(id) ON DELETE CASCADE,
        amount REAL NOT NULL,
        date TEXT NOT NULL
    );
    """)

    try:
        cur.execute("ALTER TABLE members ADD COLUMN join_date TEXT")
    except sqlite3.OperationalError:
        pass

    cur.execute("SELECT value FROM settings WHERE key='monthly_fee'")
    if cur.fetchone() is None:
        cur.execute("INSERT INTO settings(key, value) VALUES ('monthly_fee', '0')")

    cur.execute("SELECT value FROM settings WHERE key='admin_username'")
    if cur.fetchone() is None:
        salt, h = hash_password("admin")
        cur.execute("INSERT INTO settings(key, value) VALUES ('admin_username', 'admin')")
        cur.execute("INSERT INTO settings(key, value) VALUES ('admin_salt', ?)", (salt,))
        cur.execute("INSERT INTO settings(key, value) VALUES ('admin_password_hash', ?)", (h,))

    conn.commit()
    conn.close()


# ---------------- settings ----------------
def get_setting(key, default=None):
    conn = get_connection()
    row = conn.execute("SELECT value FROM settings WHERE key=?", (key,)).fetchone()
    conn.close()
    return row["value"] if row else default


def set_setting(key, value):
    conn = get_connection()
    conn.execute("INSERT INTO settings(key, value) VALUES (?, ?) "
                 "ON CONFLICT(key) DO UPDATE SET value=excluded.value", (key, value))
    conn.commit()
    conn.close()


def check_login(username, password):
    stored_user = get_setting("admin_username")
    salt = get_setting("admin_salt")
    stored_hash = get_setting("admin_password_hash")
    if username != stored_user:
        return False
    return verify_password(password, salt, stored_hash)


def change_password(new_password):
    salt, h = hash_password(new_password)
    set_setting("admin_salt", salt)
    set_setting("admin_password_hash", h)


def get_monthly_fee():
    return float(get_setting("monthly_fee", "0") or 0)


def set_monthly_fee(amount):
    set_setting("monthly_fee", str(amount))


# ---------------- members ----------------
def add_member(name, father_name, phone, address, join_date=None):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO members(name, father_name, phone, address, join_date) VALUES (?,?,?,?,?)",
        (name, father_name, phone, address, join_date))
    conn.commit()
    mid = cur.lastrowid
    conn.close()
    return mid


def update_member(member_id, name, father_name, phone, address, join_date=None):
    conn = get_connection()
    conn.execute(
        "UPDATE members SET name=?, father_name=?, phone=?, address=?, join_date=? WHERE id=?",
        (name, father_name, phone, address, join_date, member_id))
    conn.commit()
    conn.close()


def delete_member(member_id):
    conn = get_connection()
    conn.execute("DELETE FROM members WHERE id=?", (member_id,))
    conn.commit()
    conn.close()


def search_members(query=""):
    conn = get_connection()
    if query:
        rows = conn.execute(
            "SELECT * FROM members WHERE name LIKE ? OR phone LIKE ? ORDER BY name",
            (f"%{query}%", f"%{query}%")).fetchall()
    else:
        rows = conn.execute("SELECT * FROM members ORDER BY name").fetchall()
    conn.close()
    return rows


def get_member(member_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM members WHERE id=?", (member_id,)).fetchone()
    conn.close()
    return row


# ---------------- dues ----------------
def get_dues_for_member_year(member_id, year):
    conn = get_connection()
    rows = conn.execute(
        "SELECT month, paid, paid_date FROM dues WHERE member_id=? AND year=?",
        (member_id, year)).fetchall()
    conn.close()
    result = {m: {"paid": False, "paid_date": None} for m in range(1, 13)}
    for r in rows:
        result[r["month"]] = {"paid": bool(r["paid"]), "paid_date": r["paid_date"]}
    return result


def set_due_paid(member_id, year, month, paid, paid_date=None):
    conn = get_connection()
    conn.execute("""
        INSERT INTO dues(member_id, year, month, paid, paid_date) VALUES (?,?,?,?,?)
        ON CONFLICT(member_id, year, month)
        DO UPDATE SET paid=excluded.paid, paid_date=excluded.paid_date
    """, (member_id, year, month, 1 if paid else 0, paid_date))
    conn.commit()
    conn.close()


def get_unpaid_months_count(member_id, year):
    dues = get_dues_for_member_year(member_id, year)
    applicable = get_applicable_months(member_id, year)
    return sum(1 for m in applicable if not dues[m]["paid"])


def get_member_join_year_month(member_id):
    """تاریخ عضویت عضو را به صورت (سال, ماه) شمسی برمی‌گرداند؛ اگر ثبت نشده None."""
    m = get_member(member_id)
    if not m or not m["join_date"]:
        return None
    try:
        parts = str(m["join_date"]).split("-")
        return int(parts[0]), int(parts[1])
    except (ValueError, IndexError):
        return None


def get_applicable_months(member_id, year):
    """ماه‌هایی از سال داده‌شده که عضو باید حق عضویت بپردازد (بعد از تاریخ عضویت)."""
    join = get_member_join_year_month(member_id)
    if join is None:
        return list(range(1, 13))
    join_year, join_month = join
    if year < join_year:
        return []
    if year > join_year:
        return list(range(1, 13))
    return list(range(join_month, 13))


def total_dues_collected():
    conn = get_connection()
    fee_row = conn.execute("SELECT value FROM settings WHERE key='monthly_fee'").fetchone()
    fee = float(fee_row["value"]) if fee_row else 0
    count = conn.execute("SELECT COUNT(*) c FROM dues WHERE paid=1").fetchone()["c"]
    conn.close()
    return fee * count


# ---------------- loans ----------------
def add_loan(member_id, amount, date, note=""):
    conn = get_connection()
    cur = conn.execute(
        "INSERT INTO loans(member_id, amount, date, note) VALUES (?,?,?,?)",
        (member_id, amount, date, note))
    conn.commit()
    lid = cur.lastrowid
    conn.close()
    return lid


def add_loan_payment(loan_id, amount, date):
    """ثبت قسط بازپرداخت"""
    conn = get_connection()
    conn.execute("INSERT INTO loan_payments(loan_id, amount, date) VALUES (?,?,?)",
                 (loan_id, amount, date))
    conn.commit()
    conn.close()


def get_loans_for_member(member_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM loans WHERE member_id=? ORDER BY date DESC", (member_id,)).fetchall()
    conn.close()
    return rows


def get_all_loans():
    conn = get_connection()
    rows = conn.execute("""
        SELECT loans.*, members.name as member_name FROM loans
        JOIN members ON members.id = loans.member_id
        ORDER BY loans.date DESC
    """).fetchall()
    conn.close()
    return rows


def get_loan(loan_id):
    conn = get_connection()
    row = conn.execute("""
        SELECT loans.*, members.name as member_name FROM loans
        JOIN members ON members.id = loans.member_id WHERE loans.id=?
    """, (loan_id,)).fetchone()
    conn.close()
    return row


def get_loan_balance(loan_id):
    conn = get_connection()
    loan = conn.execute("SELECT amount FROM loans WHERE id=?", (loan_id,)).fetchone()
    paid = conn.execute(
        "SELECT COALESCE(SUM(amount),0) s FROM loan_payments WHERE loan_id=?",
        (loan_id,)).fetchone()
    conn.close()
    if not loan:
        return 0
    return loan["amount"] - paid["s"]


def get_loan_payments(loan_id):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM loan_payments WHERE loan_id=? ORDER BY date", (loan_id,)).fetchall()
    conn.close()
    return rows


def total_loans_outstanding():
    conn = get_connection()
    total_loans = conn.execute("SELECT COALESCE(SUM(amount),0) s FROM loans").fetchone()["s"]
    total_paid = conn.execute("SELECT COALESCE(SUM(amount),0) s FROM loan_payments").fetchone()["s"]
    conn.close()
    return total_loans - total_paid


def total_loans_given():
    conn = get_connection()
    r = conn.execute("SELECT COALESCE(SUM(amount),0) s FROM loans").fetchone()
    conn.close()
    return r["s"]


def total_loan_repayments():
    conn = get_connection()
    r = conn.execute("SELECT COALESCE(SUM(amount),0) s FROM loan_payments").fetchone()
    conn.close()
    return r["s"]


# ---------------- aid ----------------
def add_aid_received(amount, date, donor_name):
    """ثبت کمک دریافتی (بدون نیاز به بررسی موجودی چون درآمد است)"""
    conn = get_connection()
    conn.execute("INSERT INTO aid_received(amount, date, donor_name) VALUES (?,?,?)",
                 (amount, date, donor_name))
    conn.commit()
    conn.close()


def add_aid_given(member_id, amount, date):
    """ثبت کمک اهدائی با بررسی موجودی"""
    if not check_fund_balance_for_expense(amount):
        raise ValueError(f"موجودی صندوق کافی نیست! موجودی فعلی: {get_fund_balance():,.0f}")

    conn = get_connection()
    conn.execute("INSERT INTO aid_given(member_id, amount, date) VALUES (?,?,?)",
                 (member_id, amount, date))
    conn.commit()
    conn.close()


def get_all_aid_received():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM aid_received ORDER BY date DESC").fetchall()
    conn.close()
    return rows


def get_all_aid_given():
    conn = get_connection()
    rows = conn.execute("""
        SELECT aid_given.*, members.name as member_name FROM aid_given
        JOIN members ON members.id = aid_given.member_id
        ORDER BY aid_given.date DESC
    """).fetchall()
    conn.close()
    return rows


def total_aid_received():
    conn = get_connection()
    r = conn.execute("SELECT COALESCE(SUM(amount),0) s FROM aid_received").fetchone()
    conn.close()
    return r["s"]


def total_aid_given():
    conn = get_connection()
    r = conn.execute("SELECT COALESCE(SUM(amount),0) s FROM aid_given").fetchone()
    conn.close()
    return r["s"]


# ---------------- fund balance ----------------
def check_fund_balance_for_expense(amount):
    return get_fund_balance() >= amount


def get_fund_balance():
    dues_total = total_dues_collected()
    aid_in = total_aid_received()
    loan_repay = total_loan_repayments()
    aid_out = total_aid_given()
    loans_out = total_loans_given()
    return dues_total + aid_in + loan_repay - aid_out - loans_out


def get_transactions_ledger(year=None):
    """Unified list of all fund-affecting transactions for reporting."""
    conn = get_connection()
    fee = get_monthly_fee()
    txns = []

    q = "SELECT dues.*, members.name as member_name FROM dues JOIN members ON members.id=dues.member_id WHERE paid=1"
    params = ()
    if year:
        q += " AND year=?"
        params = (year,)
    for r in conn.execute(q, params).fetchall():
        txns.append({
            "date": r["paid_date"] or "", "type": "حق عضویت",
            "desc": f"{r['member_name']} - {DARI_MONTHS[r['month']-1]} {r['year']}",
            "in": fee, "out": 0
        })

    for r in conn.execute("SELECT * FROM aid_received ORDER BY date").fetchall():
        txns.append({"date": r["date"], "type": "کمک دریافتی",
                     "desc": r["donor_name"] or "-", "in": r["amount"], "out": 0})

    for r in conn.execute("""
        SELECT aid_given.*, members.name as member_name FROM aid_given
        JOIN members ON members.id=aid_given.member_id ORDER BY date""").fetchall():
        txns.append({"date": r["date"], "type": "کمک اهدائی",
                     "desc": r["member_name"], "in": 0, "out": r["amount"]})

    for r in conn.execute("""
        SELECT loans.*, members.name as member_name FROM loans
        JOIN members ON members.id=loans.member_id ORDER BY date""").fetchall():
        txns.append({"date": r["date"], "type": "قرض پرداختی",
                     "desc": r["member_name"], "in": 0, "out": r["amount"]})

    for r in conn.execute("SELECT * FROM loan_payments ORDER BY date").fetchall():
        txns.append({"date": r["date"], "type": "قسط بازپرداخت قرض",
                     "desc": "", "in": r["amount"], "out": 0})

    conn.close()
    txns.sort(key=lambda t: t["date"] or "")
    return txns


# ============================================================
# ==================== RESET DATABASE ========================
# ============================================================

def reset_database():
    """حذف کامل داده‌ها و بازنشانی دیتابیس؛ نام کاربری و رمز عبور حفظ می‌شوند"""
    try:
        conn = get_connection()
        cur = conn.cursor()

        admin_username = get_setting("admin_username")
        admin_salt = get_setting("admin_salt")
        admin_password_hash = get_setting("admin_password_hash")
        monthly_fee = get_setting("monthly_fee", "0")

        cur.execute("DELETE FROM members")
        cur.execute("DELETE FROM dues")
        cur.execute("DELETE FROM loans")
        cur.execute("DELETE FROM loan_payments")
        cur.execute("DELETE FROM aid_received")
        cur.execute("DELETE FROM aid_given")

        cur.execute("DELETE FROM sqlite_sequence WHERE name IN "
                    "('members', 'dues', 'loans', 'loan_payments', 'aid_received', 'aid_given')")

        if admin_username:
            set_setting("admin_username", admin_username)
        if admin_salt:
            set_setting("admin_salt", admin_salt)
        if admin_password_hash:
            set_setting("admin_password_hash", admin_password_hash)
        if monthly_fee:
            set_setting("monthly_fee", monthly_fee)

        conn.commit()
        conn.close()
        return True

    except Exception as e:
        print(f"reset_database error: {e}")
        return False
