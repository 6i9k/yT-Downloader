@echo off
chcp 65001 >nul
title YouTube Downloader - Web Server
color 0B

echo ════════════════════════════════════════════════════════════
echo    YouTube Downloader - Web Server
echo    by Mohammed (Star)
echo ════════════════════════════════════════════════════════════
echo.

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python غير مثبت!
    echo.
    echo يرجى تثبيت Python من: https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo ✓ Python مثبت
echo.

:: Check if requirements are installed
echo جاري التحقق من المكتبات المطلوبة...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📦 جاري تثبيت المكتبات المطلوبة...
    echo.
    pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ❌ فشل تثبيت المكتبات!
        pause
        exit /b 1
    )
    echo.
    echo ✓ تم تثبيت المكتبات بنجاح
)

echo.
echo ════════════════════════════════════════════════════════════
echo    بدء تشغيل السيرفر...
echo ════════════════════════════════════════════════════════════
echo.
echo 🌐 افتح المتصفح على: http://localhost:5000
echo.
echo اضغط Ctrl+C لإيقاف السيرفر
echo.
echo ════════════════════════════════════════════════════════════
echo.

:: Start the server
python web_app.py

pause

