[app]
title = صندوق اتحادیه
package.name = sandoghapp
package.domain = org.sandogh
source.dir = .
source.include_exts = py,png,jpg,kv,ttf,atlas,db
version = 1.0

requirements = python3,kivy==2.3.0,jdatetime,arabic-reshaper,python-bidi,sqlite3

orientation = portrait
fullscreen = 0

# اگر آیکون اختصاصی دارید، فایل icon.png (حداقل ۵۱۲×۵۱۲) را در همین پوشه بگذارید و خط زیر را فعال کنید:
# icon.filename = %(source.dir)s/icon.png

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
