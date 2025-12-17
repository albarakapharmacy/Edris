[app]

# عنوان التطبيق
title = صيدلية البركة

# اسم الحزمة (يجب أن يكون فريداً)
package.name = pharmacyapp

# اسم المجال
package.domain = com.barka

# إصدار التطبيق
version = 1.0

# متطلبات Python
requirements = python3,kivy,sqlite3

# مصدر التطبيق
source.dir = .

# ملف البداية
source.include_exts = py,png,jpg,kv,atlas,db

# حجم الشاشة
orientation = portrait

# إصدار Android المطلوب
android.api = 30
android.minapi = 21
android.sdk = 24
android.ndk = 23b

# الأذونات المطلوبة
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE

# التصريح باستخدام SQLite
android.add_src = java

# إعدادات أخرى
android.accept_sdk_license = True
android.allow_backup = True
android.enable_androidx = True

# الأيقونة
icon.filename = %(source.dir)s/assets/icon.png

# الشاشة الافتتاحية
presplash.filename = %(source.dir)s/assets/presplash.png

# إعدادات التجميع
fullscreen = 0
window.fullscreen = 0
