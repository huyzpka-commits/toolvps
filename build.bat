@echo off
chcp 65001 >nul
echo ==========================================
echo  Windows System Optimizer - Build Script
echo ==========================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [LỖI] Không tìm thấy Python. Vui lòng cài đặt Python 3.8+ từ python.org
    pause
    exit /b 1
)

echo [1] Đang cài đặt thư viện...
pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo [LỖI] Không thể cài đặt thư viện.
    pause
    exit /b 1
)

echo [2] Đang build file .exe...
pyinstaller --onefile --name "WinOptimizer" --uac-admin --clean win_optimizer.py

if errorlevel 1 (
    echo [LỖI] Build thất bại.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [OK] Build hoàn tất!
echo File exe: dist\WinOptimizer.exe
echo ==========================================
pause
