# YouTube Downloader - Web Deployment Package

## 📦 محتويات الفولدر

هذا الفولدر يحتوي على جميع الملفات المطلوبة لرفع الموقع على السيرفر أو منصة استضافة.

### الملفات:
- `web_app.py` - الملف الرئيسي للتطبيق
- `requirements.txt` - المكتبات المطلوبة
- `Procfile` - ملف التشغيل (لـ Heroku/Render)
- `runtime.txt` - إصدار Python المطلوب
- `templates/` - مجلد صفحات HTML
- `static/` - مجلد الملفات الثابتة (أيقونات، صور)

---

## 🚀 خطوات الرفع على Render.com

1. **إنشاء حساب على Render**
   - اذهب إلى: https://render.com
   - سجل حساب جديد

2. **رفع المشروع على GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin YOUR_GITHUB_REPO_URL
   git push -u origin main
   ```

3. **إنشاء Web Service على Render**
   - اضغط "New +"
   - اختر "Web Service"
   - اربط حساب GitHub الخاص بك
   - اختر المشروع
   - املأ البيانات:
     - **Name**: youtube-downloader
     - **Environment**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn web_app:app`
     - **Plan**: Free

4. **Deploy**
   - اضغط "Create Web Service"
   - انتظر حتى يكتمل الـ deployment

---

## 🚀 خطوات الرفع على Heroku

1. **تثبيت Heroku CLI**
   - حمل من: https://devcenter.heroku.com/articles/heroku-cli

2. **تسجيل الدخول**
   ```bash
   heroku login
   ```

3. **إنشاء تطبيق**
   ```bash
   heroku create youtube-downloader-app
   ```

4. **رفع المشروع**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git push heroku main
   ```

5. **فتح التطبيق**
   ```bash
   heroku open
   ```

---

## 🚀 خطوات الرفع على PythonAnywhere

1. **إنشاء حساب**
   - اذهب إلى: https://www.pythonanywhere.com
   - سجل حساب مجاني

2. **رفع الملفات**
   - اذهب إلى "Files"
   - ارفع جميع الملفات والمجلدات

3. **تثبيت المكتبات**
   - افتح Bash console
   ```bash
   pip install --user -r requirements.txt
   ```

4. **إعداد Web App**
   - اذهب إلى "Web"
   - أضف web app جديد
   - اختر Flask
   - اختار المسار لـ web_app.py

---

## 🖥️ تشغيل محلي

```bash
# تثبيت المكتبات
pip install -r requirements.txt

# تشغيل السيرفر
python web_app.py
```

ثم افتح المتصفح على: http://localhost:5000

---

## 📋 المتطلبات

- Python 3.11+
- FFmpeg (للتحويل بين الصيغ)

---

## 🔧 إعدادات إضافية

### متغيرات البيئة (Environment Variables):
- `PORT` - رقم المنفذ (5000 افتراضياً)
- `SECRET_KEY` - مفتاح سري للجلسات

### FFmpeg:
بعض المنصات تحتاج تثبيت FFmpeg يدوياً:
- **Heroku**: أضف buildpack
  ```bash
  heroku buildpacks:add https://github.com/jonathanong/heroku-buildpack-ffmpeg-latest.git
  ```
- **Render**: يأتي مثبت مسبقاً
- **PythonAnywhere**: اتصل بالدعم الفني

---

## 📝 ملاحظات

- الخطة المجانية على معظم المنصات لها قيود
- Heroku: يدخل في وضع السكون بعد 30 دقيقة من عدم الاستخدام
- Render: يدخل في وضع السكون بعد 15 دقيقة
- PythonAnywhere: حد أقصى للسرعة والموارد

---

## 🆘 استكشاف الأخطاء

### خطأ: "Application Error"
- تحقق من الـ logs
- تأكد من تثبيت جميع المكتبات من requirements.txt

### خطأ: "H10 - App Crashed" (Heroku)
- تحقق من `heroku logs --tail`
- تأكد من وجود Procfile صحيح

### خطأ: "Build Failed"
- تحقق من runtime.txt
- تأكد من إصدار Python المدعوم

---

## 👨‍💻 المطور

**Mohammed (Star)**
© 2025 جميع الحقوق محفوظة

---

## 📄 الترخيص

هذا المشروع للاستخدام الشخصي فقط.

