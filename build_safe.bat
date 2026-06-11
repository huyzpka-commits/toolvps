@echo off
chcp 65001 >nul
echo ==========================================
echo  Build Windows System Optimizer (Safe Mode)
echo  It bi nhan nham virus hon onefile
echo ==========================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo [LOI] Khong tim thay Python. Vui long cai dat Python 3.8+ tu python.org
    pause
    exit /b 1
)

echo [1] Cai dat thu vien...
pip install pyinstaller psutil --quiet
if errorlevel 1 (
    echo [LOI] Cai dat thu vien that bai.
    pause
    exit /b 1
)

echo [2] Dang build WinOptimizer (onedir + manifest + version info)...
REM Dung --onedir thay vi --onefile de giam false positive
REM Dung --uac-admin de yeu cau quyen admin khi chay
REM Dung --version-file de them thong tin phien ban
python -m PyInstaller ^
    --onedir ^
    --name "WinOptimizer" ^
    --uac-admin ^
    --version-file "version_info.txt" ^
    --clean ^
    --noconfirm ^
    win_optimizer.py

if errorlevel 1 (
    echo [LOI] Build that bai.
    pause
    exit /b 1
)

echo.
echo ==========================================
echo [OK] Build hoan tat!
echo File chay: dist\WinOptimizer\WinOptimizer.exe
echo LUU Y: Nen copy ca THU MUC dist\WinOptimizer\ de chay.
echo ==========================================
pause
