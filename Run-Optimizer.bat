@echo off
chcp 65001 >nul
echo ==========================================
echo  Windows System Optimizer - PowerShell
echo ==========================================
echo.

REM Kiem tra quyen Admin
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo [CANH BAO] Chua chay voi quyen Administrator!
    echo Mot so tinh nang se bi gioi han.
    echo.
    echo Nhan Enter de chay tiep (khuyen nghi: chay lai bang Administrator)...
    pause >nul
)

REM Bypass Execution Policy tam thoi de chay script
echo Dang khoi chay optimizer...
powershell -ExecutionPolicy Bypass -File "%~dp0WinOptimizer.ps1"

if errorlevel 1 (
    echo.
    echo [LOI] Khong the chay script. Dam bao PowerShell hoat dong.
    pause
)
