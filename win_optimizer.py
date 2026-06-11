#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Windows System Optimizer v1.0
Author: System Expert
Mục đích: Tối ưu RAM, CPU, tăng tốc phần mềm, giải phóng ổ cứng và RAM
Phù hợp: Windows 10/11, Windows Server 2022, PC/Laptop/VPS cấu hình thấp
Yêu cầu: Chạy với quyền Administrator để tối ưu tối đa
"""

import os
import sys
import shutil
import ctypes
import subprocess
import tempfile
import time
import winreg
import threading
from datetime import datetime

# Kiểm tra và tự động cài psutil nếu chưa có (tùy chọn)
try:
    import psutil
except ImportError:
    print("Đang cài đặt thư viện psutil...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "psutil", "--quiet"])
    import psutil

# Setup UTF-8 console
def setup_console():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    try:
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception:
        pass
    ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    ctypes.windll.kernel32.SetConsoleCP(65001)
    os.system("chcp 65001 >nul 2>&1")

setup_console()

# Windows APIs
kernel32 = ctypes.windll.kernel32
psapi = ctypes.windll.psapi
shell32 = ctypes.windll.shell32

# Constants
STD_OUTPUT_HANDLE = -11
FOREGROUND_BLACK = 0x0000
FOREGROUND_BLUE = 0x0001
FOREGROUND_GREEN = 0x0002
FOREGROUND_CYAN = 0x0003
FOREGROUND_RED = 0x0004
FOREGROUND_MAGENTA = 0x0005
FOREGROUND_YELLOW = 0x0006
FOREGROUND_WHITE = 0x0007
FOREGROUND_INTENSITY = 0x0008

BACKGROUND_BLACK = 0x0000
BACKGROUND_BLUE = 0x0010
BACKGROUND_GREEN = 0x0020
BACKGROUND_CYAN = 0x0030
BACKGROUND_RED = 0x0040
BACKGROUND_MAGENTA = 0x0050
BACKGROUND_YELLOW = 0x0060
BACKGROUND_WHITE = 0x0070
BACKGROUND_INTENSITY = 0x0080

def set_console_color(color):
    handle = kernel32.GetStdHandle(STD_OUTPUT_HANDLE)
    kernel32.SetConsoleTextAttribute(handle, color)

def print_color(text, color=FOREGROUND_WHITE, newline=True):
    set_console_color(color)
    if newline:
        print(text)
    else:
        print(text, end='')
    set_console_color(FOREGROUND_WHITE)

def clear_screen():
    os.system('cls')

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def format_size(bytes_size):
    if bytes_size <= 0:
        return "0 B"
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if abs(bytes_size) < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"

def wait_input():
    print_color("\nNhấn Enter để quay lại menu...", FOREGROUND_YELLOW)
    input()

def print_banner():
    clear_screen()
    print_color("=" * 70, FOREGROUND_CYAN)
    print_color("       WINDOWS SYSTEM OPTIMIZER v1.0", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("       Tối ưu cho PC | Laptop | VPS cấu hình thấp", FOREGROUND_WHITE)
    print_color("       Windows 10/11 & Windows Server 2022", FOREGROUND_WHITE)
    print_color("=" * 70, FOREGROUND_CYAN)
    if not is_admin():
        print_color("  [CẢNH BÁO] Chưa chạy với quyền Administrator! Một số tính năng sẽ bị giới hạn.", FOREGROUND_RED + FOREGROUND_INTENSITY)
        print_color("=" * 70, FOREGROUND_CYAN)

def show_system_info():
    print_banner()
    print_color("  [ THÔNG TIN HỆ THỐNG ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    # CPU
    cpu_count_logical = psutil.cpu_count(logical=True)
    cpu_count_phys = psutil.cpu_count(logical=False)
    cpu_freq = psutil.cpu_freq()
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_percents = psutil.cpu_percent(interval=0, percpu=True)
    
    print_color(f"  CPU Vật lý: {cpu_count_phys} core | Luồng: {cpu_count_logical}", FOREGROUND_WHITE)
    if cpu_freq:
        print_color(f"  Tốc độ: {cpu_freq.current:.0f} MHz (Min: {cpu_freq.min:.0f} | Max: {cpu_freq.max:.0f})", FOREGROUND_WHITE)
    print_color(f"  Sử dụng CPU: {cpu_percent}%", FOREGROUND_YELLOW if cpu_percent < 80 else FOREGROUND_RED)
    bar_len = 40
    filled = int(bar_len * cpu_percent / 100)
    bar = '[' + '█' * filled + '░' * (bar_len - filled) + ']'
    print_color(f"  {bar}", FOREGROUND_GREEN if cpu_percent < 50 else (FOREGROUND_YELLOW if cpu_percent < 80 else FOREGROUND_RED))
    
    # RAM
    print_color("-" * 70, FOREGROUND_CYAN)
    mem = psutil.virtual_memory()
    print_color(f"  RAM Tổng:    {format_size(mem.total)}", FOREGROUND_WHITE)
    print_color(f"  RAM Đã dùng: {format_size(mem.used)} ({mem.percent}%)", FOREGROUND_YELLOW if mem.percent < 85 else FOREGROUND_RED)
    print_color(f"  RAM Trống:   {format_size(mem.available)}", FOREGROUND_GREEN)
    ram_bar = '[' + '█' * int(bar_len * mem.percent / 100) + '░' * (bar_len - int(bar_len * mem.percent / 100)) + ']'
    print_color(f"  {ram_bar}", FOREGROUND_GREEN if mem.percent < 70 else (FOREGROUND_YELLOW if mem.percent < 85 else FOREGROUND_RED))
    
    # Swap
    swap = psutil.swap_memory()
    print_color(f"  SWAP/Pagefile: {format_size(swap.used)}/{format_size(swap.total)} ({swap.percent}%)", FOREGROUND_WHITE)
    
    # Disk
    print_color("-" * 70, FOREGROUND_CYAN)
    for part in psutil.disk_partitions():
        if 'cdrom' in part.opts or part.fstype == '':
            continue
        try:
            usage = psutil.disk_usage(part.mountpoint)
            color = FOREGROUND_GREEN if usage.percent < 80 else (FOREGROUND_YELLOW if usage.percent < 90 else FOREGROUND_RED)
            print_color(f"  Ổ {part.device:4s} {part.mountpoint:6s} | {format_size(usage.used):>10s}/{format_size(usage.total):>10s} ({usage.percent}%)", color)
        except Exception:
            pass
    
    # Boot time
    print_color("-" * 70, FOREGROUND_CYAN)
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    print_color(f"  Thời gian hoạt động: {boot_time.strftime('%Y-%m-%d %H:%M:%S')} (Uptime: {int((datetime.now() - boot_time).total_seconds() // 3600)} giờ)", FOREGROUND_WHITE)
    print_color("=" * 70, FOREGROUND_CYAN)

def clean_disk():
    print_banner()
    print_color("  [ DỌN DẸP Ổ CỨNG & FILE TẠM ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    total_freed = 0
    targets = []
    
    # User temp
    user_temp = os.path.expandvars(r"%TEMP%")
    if os.path.exists(user_temp):
        targets.append(("Temp người dùng", user_temp))
    
    # Windows temp
    win_temp = r"C:\Windows\Temp"
    if os.path.exists(win_temp):
        targets.append(("Temp hệ thống", win_temp))
    
    # Prefetch (giữ lại file mới hơn 7 ngày)
    prefetch = r"C:\Windows\Prefetch"
    if os.path.exists(prefetch):
        targets.append(("Prefetch", prefetch))
    
    # Recent
    recent = os.path.expandvars(r"%USERPROFILE%\Recent")
    if os.path.exists(recent):
        targets.append(("Recent Items", recent))
    
    # Windows Update Download cache
    wu_cache = r"C:\Windows\SoftwareDistribution\Download"
    if os.path.exists(wu_cache):
        targets.append(("Windows Update Cache", wu_cache))
    
    # Windows Logs
    win_logs = r"C:\Windows\Logs"
    if os.path.exists(win_logs):
        targets.append(("Windows Logs", win_logs))
    
    # Crash dumps
    dumps = r"C:\Windows\Minidump"
    if os.path.exists(dumps):
        targets.append(("Minidump", dumps))
    
    # Event Viewer temp logs
    evt_logs = r"C:\Windows\System32\winevt\Logs"
    if os.path.exists(evt_logs):
        targets.append(("Event Logs", evt_logs))
    
    # Temporary Internet Files
    ie_temp = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\INetCache")
    if os.path.exists(ie_temp):
        targets.append(("Internet Cache", ie_temp))
    
    # Thumbnail cache
    thumb_cache = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer")
    if os.path.exists(thumb_cache):
        targets.append(("Thumbnail Cache", thumb_cache))
    
    for name, path in targets:
        freed = 0
        try:
            for root, dirs, files in os.walk(path, topdown=False):
                # Skip system protected directories
                if '\\System32' in root or '\\SysWOW64' in root:
                    if name not in ["Windows Logs", "Event Logs"]:
                        continue
                
                for f in files:
                    try:
                        fp = os.path.join(root, f)
                        if os.path.exists(fp):
                            size = os.path.getsize(fp)
                            os.remove(fp)
                            freed += size
                            total_freed += size
                    except Exception:
                        pass
                
                for d in dirs:
                    try:
                        dp = os.path.join(root, d)
                        if os.path.exists(dp) and not os.listdir(dp):
                            os.rmdir(dp)
                    except Exception:
                        pass
            
            print_color(f"  [OK] {name:25s} - {format_size(freed):>10s}", FOREGROUND_GREEN)
        except Exception as e:
            print_color(f"  [ERR] {name:25s} - {str(e)[:40]}", FOREGROUND_RED)
    
    # Empty Recycle Bin
    try:
        # SHERB_NOCONFIRMATION = 0x00000001
        # SHERB_NOPROGRESSUI = 0x00000002
        # SHERB_NOSOUND = 0x00000004
        result = shell32.SHEmptyRecycleBinW(None, None, 0x00000001 | 0x00000002 | 0x00000004)
        print_color(f"  [OK] {'Recycle Bin':25s} - Đã dọn sạch", FOREGROUND_GREEN)
    except Exception:
        print_color(f"  [WARN] {'Recycle Bin':25s} - Không thể dọn", FOREGROUND_YELLOW)
    
    # Run Windows Disk Cleanup scripts (optional)
    try:
        # Tự động dọn Windows Error Reporting
        wer_path = r"C:\ProgramData\Microsoft\Windows\WER"
        if os.path.exists(wer_path):
            shutil.rmtree(wer_path, ignore_errors=True)
            print_color(f"  [OK] {'Error Reports':25s} - Đã dọn", FOREGROUND_GREEN)
    except Exception:
        pass
    
    print_color("-" * 70, FOREGROUND_CYAN)
    print_color(f"  [+] TỔNG ĐÃ GIẢI PHÓNG: {format_size(total_freed)}", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
    print_color("=" * 70, FOREGROUND_CYAN)

def optimize_ram():
    print_banner()
    print_color("  [ TỐI ƯU & GIẢI PHÓNG RAM ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    mem_before = psutil.virtual_memory()
    print_color(f"  Trước khi tối ưu: {format_size(mem_before.used)} đã dùng ({mem_before.percent}%)", FOREGROUND_YELLOW)
    
    # 1. Trim working sets of all accessible processes
    count = 0
    failed = 0
    
    print_color("\n  [1] Đang trim working sets của các process...", FOREGROUND_WHITE)
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            pid = proc.info['pid']
            # PROCESS_QUERY_INFORMATION | PROCESS_SET_QUOTA | PROCESS_VM_OPERATION | PROCESS_VM_READ = 0x400 | 0x100 | 0x8 | 0x10 = 0x518
            # Sử dụng 0x1F0FFF (PROCESS_ALL_ACCESS) để đảm bảo, nhưng với system process có thể fail
            hProcess = kernel32.OpenProcess(0x001F0FFF, False, pid)
            if hProcess:
                if psapi.EmptyWorkingSet(hProcess):
                    count += 1
                else:
                    failed += 1
                kernel32.CloseHandle(hProcess)
            else:
                failed += 1
        except Exception:
            failed += 1
    
    print_color(f"  -> Đã trim {count} process thành công", FOREGROUND_GREEN)
    
    # 2. Run idle tasks to flush cache
    print_color("\n  [2] Đang chạy idle tasks...", FOREGROUND_WHITE)
    try:
        subprocess.run(["rundll32.exe", "advapi32.dll,ProcessIdleTasks"], timeout=30, capture_output=True)
        print_color("  -> Idle tasks hoàn tất", FOREGROUND_GREEN)
    except Exception:
        print_color("  -> Idle tasks bỏ qua", FOREGROUND_YELLOW)
    
    # 3. Clear Standby List / File Cache (if possible via NtSetSystemInformation)
    print_color("\n  [3] Đang cố gắng giải phóng standby list...", FOREGROUND_WHITE)
    try:
        ntdll = ctypes.windll.ntdll
        # SystemMemoryListInformation class = 80
        # MemoryPurgeStandbyList = 3
        # MemoryPurgeStandbyList + MemoryPurgeModifiedPageList = 3
        # Define MemoryListCommand structure
        class MEMORY_LIST_COMMAND(ctypes.Structure):
            _fields_ = [("MemoryListCommand", ctypes.c_ulong)]
        
        cmd = MEMORY_LIST_COMMAND()
        cmd.MemoryListCommand = 3  # MemoryPurgeStandbyList
        
        # SystemMemoryListInformation = 80
        status = ntdll.NtSetSystemInformation(80, ctypes.byref(cmd), ctypes.sizeof(cmd))
        if status == 0:  # STATUS_SUCCESS
            print_color("  -> Standby list đã được giải phóng", FOREGROUND_GREEN)
        else:
            print_color(f"  -> Standby list: cần quyền cao hơn (Status: 0x{status:08X})", FOREGROUND_YELLOW)
    except Exception as e:
        print_color(f"  -> Không thể clear standby list (cần driver hoặc RAMMap): {str(e)[:50]}", FOREGROUND_YELLOW)
    
    # 4. Force garbage collection of Python itself
    import gc
    gc.collect()
    
    # 5. Wait a moment for system to stabilize
    time.sleep(1)
    
    mem_after = psutil.virtual_memory()
    saved = mem_before.used - mem_after.used
    print_color("-" * 70, FOREGROUND_CYAN)
    print_color(f"  Sau khi tối ưu:  {format_size(mem_after.used)} đã dùng ({mem_after.percent}%)", FOREGROUND_GREEN)
    if saved > 0:
        print_color(f"  [+] RAM đã giải phóng: {format_size(saved)}", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
    else:
        print_color(f"  [~] RAM ổn định (có thể đã được dùng lại bởi cache)", FOREGROUND_YELLOW)
    print_color("=" * 70, FOREGROUND_CYAN)

def optimize_services():
    print_banner()
    print_color("  [ TỐI ƯU DỊCH VỤ & HỆ THỐNG ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    if not is_admin():
        print_color("  [LỖI] Cần quyền Administrator để tối ưu dịch vụ!", FOREGROUND_RED)
        print_color("=" * 70, FOREGROUND_CYAN)
        return
    
    services = [
        ("WSearch", "Windows Search (lập chỉ mục, tốn nhiều tài nguyên)"),
        ("SysMain", "SysMain / Superfetch (prefetch tự động, không cần thiết trên SSD/VPS)"),
        ("WMPNetworkSvc", "Windows Media Player Network Sharing"),
        ("Fax", "Fax Service"),
        ("DiagTrack", "Connected User Experiences and Telemetry (thu thập dữ liệu)"),
        ("dmwappushservice", "WAP Push Service"),
        ("MapsBroker", "Downloaded Maps Manager"),
        ("WbioSrvc", "Windows Biometric Service (nếu không dùng vân tay/face)"),
    ]
    
    print_color("  Đang tắt các dịch vụ không cần thiết...", FOREGROUND_WHITE)
    for svc_name, desc in services:
        try:
            # Stop service
            stop_result = subprocess.run(["sc", "stop", svc_name], capture_output=True, text=True, check=False)
            # Disable service
            config_result = subprocess.run(["sc", "config", svc_name, "start=", "disabled"], capture_output=True, text=True, check=False)
            
            if config_result.returncode == 0 or stop_result.returncode == 0 or stop_result.returncode == 1062:  # 1062 = service not started
                print_color(f"  [OK] {svc_name:20s} - {desc}", FOREGROUND_GREEN)
            else:
                print_color(f"  [WARN] {svc_name:20s} - Không tìm thấy hoặc không thể tắt", FOREGROUND_YELLOW)
        except Exception as e:
            print_color(f"  [ERR] {svc_name:20s} - {str(e)[:40]}", FOREGROUND_RED)
    
    # Power plan - High Performance
    print_color("\n  [+] Đang kích hoạt chế độ High Performance...", FOREGROUND_WHITE)
    try:
        # First, try to duplicate the built-in High Performance plan
        dup = subprocess.run(["powercfg", "-duplicatescheme", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], 
                          capture_output=True, text=True, check=False)
        if dup.returncode == 0:
            # Extract GUID from output
            output = dup.stdout
            if "GUID:" in output:
                guid = output.split("GUID:")[1].split(" ")[1].strip()
                subprocess.run(["powercfg", "-setactive", guid], capture_output=True, check=False)
                print_color(f"  -> High Performance đã kích hoạt (GUID: {guid})", FOREGROUND_GREEN)
            else:
                subprocess.run(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True, check=False)
                print_color("  -> High Performance đã kích hoạt", FOREGROUND_GREEN)
        else:
            # Maybe the plan already exists
            subprocess.run(["powercfg", "-setactive", "8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], capture_output=True, check=False)
            print_color("  -> High Performance đã kích hoạt (fallback)", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Không thể đổi power plan: {str(e)[:50]}", FOREGROUND_YELLOW)
    
    # Disable Hibernation (free up disk space equal to RAM size)
    print_color("\n  [+] Đang tắt Hibernate để giải phóng ổ cứng...", FOREGROUND_WHITE)
    try:
        subprocess.run(["powercfg", "-h", "off"], capture_output=True, check=False)
        print_color("  -> Hibernate đã tắt (giải phóng RAM-size trên ổ C:)", FOREGROUND_GREEN)
    except Exception:
        print_color("  -> Không thể tắt Hibernate", FOREGROUND_YELLOW)
    
    print_color("=" * 70, FOREGROUND_CYAN)

def optimize_performance():
    print_banner()
    print_color("  [ TỐI ƯU CPU & TĂNG TỐC PHẦN MỀM ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    # 1. Set priority of current process to High
    print_color("  [1] Đang tăng priority của optimizer...", FOREGROUND_WHITE)
    try:
        p = psutil.Process(os.getpid())
        p.nice(psutil.HIGH_PRIORITY_CLASS)
        print_color("  -> Priority: HIGH", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Lỗi: {str(e)[:50]}", FOREGROUND_RED)
    
    # 2. Disable visual effects via registry
    print_color("\n  [2] Đang tắt hiệu ứng hình ảnh (Best Performance)...", FOREGROUND_WHITE)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "VisualFXSetting", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
        
        # Also set via SystemPropertiesPerformance
        key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Control Panel\Desktop",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key2, "UserPreferencesMask", 0, winreg.REG_BINARY, b'\x90\x12\x03\x80\x10\x00\x00\x00')
        winreg.CloseKey(key2)
        
        print_color("  -> Hiệu ứng hình ảnh: Best Performance", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Lỗi registry: {str(e)[:50]}", FOREGROUND_RED)
    
    # 3. Disable transparency and animations (if Windows 10/11)
    print_color("\n  [3] Đang tắt Transparency & Animations...", FOREGROUND_WHITE)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                            r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "EnableTransparency", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        
        key2 = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Control Panel\Desktop\WindowMetrics",
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key2, "MinAnimate", 0, winreg.REG_SZ, "0")
        winreg.CloseKey(key2)
        print_color("  -> Transparency & Animations: OFF", FOREGROUND_GREEN)
    except Exception:
        print_color("  -> Không áp dụng (có thể là Windows Server)", FOREGROUND_YELLOW)
    
    # 4. Increase responsiveness (disable Nagle algorithm hints for networking)
    print_color("\n  [4] Đang tối u hóa TCP/IP & Network...", FOREGROUND_WHITE)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters\Interfaces",
                            0, winreg.KEY_READ)
        
        # We can't iterate here easily without knowing subkeys, but we can set global
        winreg.CloseKey(key)
        
        # Set global TCP params
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                            r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters",
                            0, winreg.KEY_SET_VALUE)
        try:
            winreg.SetValueEx(key, "TcpTimedWaitDelay", 0, winreg.REG_DWORD, 30)
        except:
            pass
        try:
            winreg.SetValueEx(key, "MaxUserPort", 0, winreg.REG_DWORD, 65534)
        except:
            pass
        winreg.CloseKey(key)
        print_color("  -> Network stack đã tối ưu", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Không thể tối ưu network: {str(e)[:50]}", FOREGROUND_YELLOW)
    
    print_color("\n  [5] Gợi ý: Khởi động l Explorer để áp dụng hiệu ứng ngay?", FOREGROUND_YELLOW)
    print_color("      (Nhập 'y' để khởi động lại Explorer, hoặc Enter để bỏ qua)", FOREGROUND_YELLOW)
    choice = input("  > ").strip().lower()
    if choice == 'y':
        try:
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], capture_output=True, check=False)
            time.sleep(1)
            subprocess.Popen(["explorer.exe"], creationflags=subprocess.CREATE_NEW_CONSOLE)
            print_color("  -> Explorer đã khởi động lại", FOREGROUND_GREEN)
        except Exception as e:
            print_color(f"  -> Lỗi: {str(e)[:50]}", FOREGROUND_RED)
    
    print_color("=" * 70, FOREGROUND_CYAN)

def kill_background_apps():
    print_banner()
    print_color("  [ TẮT ỨNG DỤNG NỀN KHÔNG CẦN THIẾT ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    print_color("  DANH SÁCH CÓ THỂ TẮT:", FOREGROUND_YELLOW)
    
    candidates = [
        ("OneDrive.exe", "OneDrive"),
        ("Teams.exe", "Microsoft Teams"),
        ("Skype.exe", "Skype"),
        ("Spotify.exe", "Spotify"),
        ("Dropbox.exe", "Dropbox"),
        ("GoogleDriveFS.exe", "Google Drive"),
        ("Creative Cloud.exe", "Adobe Creative Cloud"),
        ("Steam.exe", "Steam Client"),
        ("EpicGamesLauncher.exe", "Epic Games Launcher"),
    ]
    
    for idx, (exe, name) in enumerate(candidates, 1):
        print_color(f"  {idx}. {exe:25s} ({name})", FOREGROUND_WHITE)
    print_color("  0. Quay lại (không tắt gì)", FOREGROUND_WHITE)
    print_color("-" * 70, FOREGROUND_CYAN)
    print_color("  Nhập số thứ tự cách nhau bởi dấu phẩy (ví dụ: 1,2,3) hoặc 'all'", FOREGROUND_YELLOW)
    choice = input("  > ").strip().lower()
    
    if choice == '0' or choice == '':
        return
    
    selected = []
    if choice == 'all':
        selected = list(range(len(candidates)))
    else:
        try:
            for x in choice.split(','):
                idx = int(x.strip()) - 1
                if 0 <= idx < len(candidates):
                    selected.append(idx)
        except ValueError:
            print_color("  Lựa chọn không hợp lệ!", FOREGROUND_RED)
            return
    
    killed = 0
    for idx in selected:
        exe, name = candidates[idx]
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'] and proc.info['name'].lower() == exe.lower():
                    p = psutil.Process(proc.info['pid'])
                    p.terminate()
                    try:
                        p.wait(timeout=3)
                    except psutil.TimeoutExpired:
                        p.kill()
                    killed += 1
            print_color(f"  [OK] Đã tắt {name} ({exe})", FOREGROUND_GREEN)
        except Exception as e:
            print_color(f"  [ERR] {name}: {str(e)[:50]}", FOREGROUND_RED)
    
    print_color(f"\n  [+] Tổng số process đã tắt: {killed}", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
    print_color("=" * 70, FOREGROUND_CYAN)

def optimize_network():
    print_banner()
    print_color("  [ TOI UU MANG (NETWORK) ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    if not is_admin():
        print_color("  [CANH BAO] Chua chay voi quyen Administrator! Mot so toi uu se bi gioi han.", FOREGROUND_RED)
    
    # 1. Flush DNS
    print_color("  [1] Dang xoa DNS cache...", FOREGROUND_WHITE)
    try:
        subprocess.run(["ipconfig", "/flushdns"], capture_output=True, check=False)
        print_color("  -> DNS cache da duoc xoa", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Loi: {str(e)[:50]}", FOREGROUND_RED)
    
    # 2. TCP Registry Optimizations
    print_color("\n  [2] Dang toi uu TCP/IP stack...", FOREGROUND_WHITE)
    tcp_params = [
        ("TcpNoDelay", 1),
        ("TcpAckFrequency", 1),
        ("TCPWindowSize", 65535),
        ("GlobalMaxTcpWindowSize", 65535),
        ("DefaultTTL", 64),
        ("EnablePMTUDiscovery", 1),
        ("SackOpts", 1),
        ("TcpMaxDupAcks", 2),
        ("DisableTaskOffload", 0),
    ]
    
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SYSTEM\CurrentControlSet\Services\Tcpip\Parameters", 
                            0, winreg.KEY_SET_VALUE)
        for name, value in tcp_params:
            try:
                winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            except Exception:
                pass
        winreg.CloseKey(key)
        print_color("  -> TCP/IP registry da toi uu", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Loi registry TCP: {str(e)[:50]}", FOREGROUND_RED)
    
    # 3. NIC RSS / Task Offload
    print_color("\n  [3] Dang toi uu Network Interface (RSS, Offload)...", FOREGROUND_WHITE)
    try:
        subprocess.run(["netsh", "interface", "tcp", "set", "global", "autotuninglevel=normal"], 
                     capture_output=True, check=False, timeout=10)
        subprocess.run(["netsh", "interface", "tcp", "set", "global", "rss=enabled"], 
                     capture_output=True, check=False, timeout=10)
        subprocess.run(["netsh", "interface", "tcp", "set", "global", "netdma=enabled"], 
                     capture_output=True, check=False, timeout=10)
        subprocess.run(["netsh", "interface", "tcp", "set", "global", "timestamps=disabled"], 
                     capture_output=True, check=False, timeout=10)
        subprocess.run(["netsh", "interface", "tcp", "set", "global", "ecncapability=disabled"], 
                     capture_output=True, check=False, timeout=10)
        subprocess.run(["netsh", "interface", "tcp", "set", "global", "chimney=disabled"], 
                     capture_output=True, check=False, timeout=10)
        print_color("  -> Netsh TCP/IP global da toi uu", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Loi netsh: {str(e)[:50]}", FOREGROUND_RED)
    
    # 4. QoS / Multimedia Throttling
    print_color("\n  [4] Dang toi uu QoS & Multimedia Throttling...", FOREGROUND_WHITE)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "SystemResponsiveness", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        
        key2 = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                             r"SOFTWARE\Policies\Microsoft\Windows\Psched", 
                             0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key2, "NonBestEffortLimit", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key2)
        print_color("  -> QoS & Throttling da toi uu", FOREGROUND_GREEN)
    except Exception:
        print_color("  -> QoS: Mot so gia tri khong ap dung duoc", FOREGROUND_YELLOW)
    
    # 5. Disable IPv6 (optional, ask user)
    print_color("\n  [5] Tat IPv6 de giam overhead? (Nhap 'y' de tat, Enter de bo qua)", FOREGROUND_YELLOW)
    ans = input("  > ").strip().lower()
    if ans == 'y':
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "DisabledComponents", 0, winreg.REG_DWORD, 0xFF)
            winreg.CloseKey(key)
            print_color("  -> IPv6 da tat (can khoi dong lai)", FOREGROUND_GREEN)
        except Exception as e:
            print_color(f"  -> Loi tat IPv6: {str(e)[:50]}", FOREGROUND_RED)
    
    print_color("\n  [TIP] Khuyen nghi khoi dong lai may de ap dung toi uu mang.", FOREGROUND_CYAN)
    print_color("=" * 70, FOREGROUND_CYAN)


def optimize_ssd():
    print_banner()
    print_color("  [ TOI UU SSD ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    if not is_admin():
        print_color("  [CANH BAO] Chua chay voi quyen Administrator!", FOREGROUND_RED)
    
    # Detect SSDs
    print_color("  Dang quet o dia...", FOREGROUND_WHITE)
    try:
        import wmi
    except ImportError:
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "wmi", "--quiet"])
            import wmi
        except Exception:
            wmi = None
    
    ssd_found = False
    drives = []
    if wmi:
        try:
            c = wmi.WMI()
            for disk in c.Win32_DiskDrive():
                media = str(disk.MediaType).lower()
                if "ssd" in media or "solid" in media:
                    ssd_found = True
                    drives.append(disk.DeviceID)
                    print_color(f"  [SSD] {disk.Model} ({disk.Size/1GB:.0f} GB)", FOREGROUND_GREEN)
        except Exception:
            pass
    
    if not ssd_found:
        # Fallback: try MSStorageDriver_FailurePredictStatus
        try:
            c = wmi.WMI()
            for pd in c.Win32_DiskDrive():
                if pd.MediaType and "fixed" in str(pd.MediaType).lower():
                    # Check if rotational (not perfect but better than nothing)
                    if "rotational" not in str(pd.MediaType).lower():
                        ssd_found = True
                        drives.append(pd.DeviceID)
                        print_color(f"  [SSD?] {pd.Model} (MediaType: {pd.MediaType})", FOREGROUND_YELLOW)
        except Exception:
            pass
    
    if not ssd_found:
        print_color("  [CANH BAO] Khong phat hien SSD ro rang. Toi uu van se chay (co the khong co hieu qua tren HDD).", FOREGROUND_YELLOW)
    
    # 1. TRIM
    print_color("\n  [1] Kiem tra TRIM...", FOREGROUND_WHITE)
    try:
        result = subprocess.run(["fsutil", "behavior", "query", "DisableDeleteNotify"], 
                               capture_output=True, text=True, check=False, timeout=10)
        if "DisableDeleteNotify = 0" in result.stdout:
            print_color("  -> TRIM da BAT (OK)", FOREGROUND_GREEN)
        else:
            subprocess.run(["fsutil", "behavior", "set", "DisableDeleteNotify", "0"], 
                          capture_output=True, check=False, timeout=10)
            print_color("  -> TRIM da duoc BAT", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Loi TRIM: {str(e)[:50]}", FOREGROUND_RED)
    
    # 2. Disable Last Access Timestamp
    print_color("\n  [2] Tat Last Access Timestamp...", FOREGROUND_WHITE)
    try:
        subprocess.run(["fsutil", "behavior", "set", "DisableLastAccess", "1"], 
                      capture_output=True, check=False, timeout=10)
        print_color("  -> Last Access Timestamp: TAT", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Loi: {str(e)[:50]}", FOREGROUND_RED)
    
    # 3. Disable Prefetch & Superfetch
    print_color("\n  [3] Tat Prefetch & Superfetch (khong can tren SSD)...", FOREGROUND_WHITE)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "EnablePrefetcher", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "EnableSuperfetch", 0, winreg.REG_DWORD, 0)
        winreg.SetValueEx(key, "EnableBoottrace", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print_color("  -> Prefetch & Superfetch: TAT", FOREGROUND_GREEN)
    except Exception as e:
        print_color(f"  -> Loi registry: {str(e)[:50]}", FOREGROUND_RED)
    
    # 4. Disable Scheduled Defrag
    print_color("\n  [4] Tat Scheduled Defrag...", FOREGROUND_WHITE)
    try:
        subprocess.run(["schtasks", "/Change", "/TN", r"\Microsoft\Windows\Defrag\ScheduledDefrag", "/DISABLE"], 
                     capture_output=True, check=False, timeout=10)
        print_color("  -> Scheduled Defrag: TAT", FOREGROUND_GREEN)
    except Exception:
        print_color("  -> Scheduled Defrag khong tim thay hoac da tat", FOREGROUND_YELLOW)
    
    # 5. Disable ClearPageFileAtShutdown
    print_color("\n  [5] Tat ClearPageFileAtShutdown (giam write cycle)...", FOREGROUND_WHITE)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ClearPageFileAtShutdown", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(key)
        print_color("  -> ClearPageFileAtShutdown: TAT", FOREGROUND_GREEN)
    except Exception:
        print_color("  -> Khong the set ClearPageFileAtShutdown", FOREGROUND_YELLOW)
    
    # 6. Increase NTFS Memory Usage
    print_color("\n  [6] Tang NTFS Memory Usage...", FOREGROUND_WHITE)
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                            r"SYSTEM\CurrentControlSet\Control\FileSystem", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "NtfsMemoryUsage", 0, winreg.REG_DWORD, 2)
        winreg.CloseKey(key)
        print_color("  -> NTFS MemoryUsage: 2 (High)", FOREGROUND_GREEN)
    except Exception:
        print_color("  -> Khong the set NtfsMemoryUsage", FOREGROUND_YELLOW)
    
    print_color("\n  [TIP] Khuyen nghi khoi dong lai de ap dung tat ca toi uu SSD.", FOREGROUND_CYAN)
    print_color("=" * 70, FOREGROUND_CYAN)


def toggle_windows_update():
    print_banner()
    print_color("  [ QUAN LY WINDOWS UPDATE ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    print_color("  1. TAT Windows Update tam thoi", FOREGROUND_RED)
    print_color("  2. BAT lai Windows Update", FOREGROUND_GREEN)
    print_color("  0. Quay lai", FOREGROUND_WHITE)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    choice = input("  Nhap lua chon: ").strip()
    
    if choice == '1':
        print_color("\n  Dang TAT Windows Update...", FOREGROUND_YELLOW)
        services = ["wuauserv", "bits", "dosvc", "usosvc", "WaaSMedicSvc"]
        for svc in services:
            try:
                subprocess.run(["sc", "stop", svc], capture_output=True, check=False, timeout=15)
                subprocess.run(["sc", "config", svc, "start=", "disabled"], capture_output=True, check=False, timeout=15)
                print_color(f"  [OK] {svc}: TAT", FOREGROUND_GREEN)
            except Exception:
                print_color(f"  [WARN] {svc}: Khong the tat", FOREGROUND_YELLOW)
        
        # Disable WaaSMedicSvc via registry (protected service)
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SYSTEM\CurrentControlSet\Services\WaaSMedicSvc", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 4)
            winreg.CloseKey(key)
        except Exception:
            pass
        
        print_color("\n  [+] Windows Update da TAT tam thoi.", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
        print_color("  [TIP] Chon '2' trong menu nay de BAT lai khi can.", FOREGROUND_CYAN)
        
    elif choice == '2':
        print_color("\n  Dang BAT Windows Update...", FOREGROUND_GREEN)
        services = ["wuauserv", "bits", "dosvc", "usosvc"]
        for svc in services:
            try:
                subprocess.run(["sc", "config", svc, "start=", "demand"], capture_output=True, check=False, timeout=15)
                subprocess.run(["sc", "start", svc], capture_output=True, check=False, timeout=15)
                print_color(f"  [OK] {svc}: BAT", FOREGROUND_GREEN)
            except Exception:
                print_color(f"  [WARN] {svc}: Khong the bat", FOREGROUND_YELLOW)
        
        # Re-enable WaaSMedicSvc
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                                r"SYSTEM\CurrentControlSet\Services\WaaSMedicSvc", 
                                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "Start", 0, winreg.REG_DWORD, 3)
            winreg.CloseKey(key)
        except Exception:
            pass
        
        print_color("\n  [+] Windows Update da BAT lai.", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
    
    print_color("=" * 70, FOREGROUND_CYAN)


def toggle_context_menu():
    print_banner()
    print_color("  [ CHUYEN DOI MENU CHUOT PHAI (Windows 11) ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    print_color("  1. Menu CLASSIC (Windows 10 style - show full menu always)", FOREGROUND_GREEN)
    print_color("  2. Menu MODERN (Windows 11 style - 'Show more options')", FOREGROUND_WHITE)
    print_color("  0. Quay lai", FOREGROUND_WHITE)
    print_color("-" * 70, FOREGROUND_CYAN)
    
    choice = input("  Nhap lua chon: ").strip()
    
    clsid_key = r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}"
    
    if choice == '1':
        print_color("\n  Dang bat Menu CLASSIC...", FOREGROUND_YELLOW)
        try:
            # Create the key path
            key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, clsid_key + r"\InprocServer32")
            winreg.SetValueEx(key, "", 0, winreg.REG_SZ, "")
            winreg.CloseKey(key)
            print_color("  -> Menu CLASSIC da duoc BAT", FOREGROUND_GREEN)
            print_color("  [TIP] Nhap chuot phai voi nut chuot phai bat ky de test.", FOREGROUND_CYAN)
            print_color("  [TIP] Khoi dong lai Explorer hoac khoi dong lai may de ap dung.", FOREGROUND_CYAN)
        except Exception as e:
            print_color(f"  -> Loi: {str(e)[:50]}", FOREGROUND_RED)
    
    elif choice == '2':
        print_color("\n  Dang khoi phuc Menu MODERN...", FOREGROUND_YELLOW)
        try:
            # Delete the entire CLSID key
            import _winreg
            # Need to recursively delete
            def delete_sub_key(root, sub):
                try:
                    open_key = winreg.OpenKey(root, sub, 0, winreg.KEY_ALL_ACCESS)
                    info = winreg.QueryInfoKey(open_key)
                    for x in range(0, info[0]):
                        child = winreg.EnumKey(open_key, 0)
                        delete_sub_key(open_key, child)
                        winreg.DeleteKey(open_key, child)
                    winreg.CloseKey(open_key)
                    winreg.DeleteKey(root, sub)
                except Exception:
                    pass
            delete_sub_key(winreg.HKEY_CURRENT_USER, clsid_key)
            print_color("  -> Menu MODERN da duoc khoi phuc", FOREGROUND_GREEN)
            print_color("  [TIP] Khoi dong lai Explorer hoac khoi dong lai may de ap dung.", FOREGROUND_CYAN)
        except Exception as e:
            print_color(f"  -> Loi: {str(e)[:50]}", FOREGROUND_RED)
    
    print_color("=" * 70, FOREGROUND_CYAN)


def auto_optimize_all():
    print_banner()
    print_color("  [ TỰ ĐỘNG TỐI ƯU TOÀN BỘ - 1 CLICK ]", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    print_color("  Bắt đầu tối ưu toàn diện...", FOREGROUND_YELLOW + FOREGROUND_INTENSITY)
    time.sleep(1)
    
    show_system_info()
    input("\n  Nhấn Enter để bắt đầu tối ưu...")
    
    clean_disk()
    wait_input()
    
    optimize_ram()
    wait_input()
    
    optimize_services()
    wait_input()
    
    optimize_performance()
    wait_input()
    
    print_banner()
    print_color("  [ TỐI ƯU HOÀN TẤT ]", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
    print_color("-" * 70, FOREGROUND_CYAN)
    show_system_info()
    print_color("\n  [TIP] Khởi động lại máy để áp dụng tất cả thay đổi dịch vụ.", FOREGROUND_CYAN)
    print_color("=" * 70, FOREGROUND_CYAN)

def main():
    while True:
        print_banner()
        print_color("  MENU CHÍN:", FOREGROUND_CYAN + FOREGROUND_INTENSITY)
        print_color("-" * 70, FOREGROUND_CYAN)
        print_color("  1. Xem thông tin hệ thống (CPU, RAM, Disk, Uptime)", FOREGROUND_WHITE)
        print_color("  2. Dọn dẹp ổ cứng & file tạm (giải phóng GB)", FOREGROUND_WHITE)
        print_color("  3. Tối ưu & giải phóng RAM (trim working sets, cache)", FOREGROUND_WHITE)
        print_color("  4. Tối ưu dịch vụ & năng lượng (High Performance)", FOREGROUND_WHITE)
        print_color("  5. Tối ưu CPU & tăng tốc phần mềm (tắt hiệu ứng, tối ưu TCP)", FOREGROUND_WHITE)
        print_color("  6. Tắt ứng dụng nền không cần thiết (OneDrive, Teams...)", FOREGROUND_WHITE)
        print_color("  7. TỰ ĐỘNG TỐI ƯU TẤT CẢ (1-Click)", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
        print_color("-" * 70, FOREGROUND_CYAN)
        print_color("  8. Tối ưu mạng (flush DNS, TCP/IP, RSS, QoS, IPv6)", FOREGROUND_WHITE)
        print_color("  9. Tối ưu SSD (TRIM, Prefetch, Defrag, NTFS)", FOREGROUND_WHITE)
        print_color(" 10. Tắt/Bật Windows Update tạm thời", FOREGROUND_WHITE)
        print_color(" 11. Chuyển menu chuột phải Classic/Modern (Windows 11)", FOREGROUND_WHITE)
        print_color("-" * 70, FOREGROUND_CYAN)
        print_color("  0. Thoát", FOREGROUND_RED + FOREGROUND_INTENSITY)
        print_color("-" * 70, FOREGROUND_CYAN)
        print_color("  Yêu cầu: Chạy bằng Administrator để tối ưu dịch vụ & services.", FOREGROUND_YELLOW)
        print_color("=" * 70, FOREGROUND_CYAN)
        
        choice = input("  Nhập lựa chọn: ").strip()
        
        if choice == '1':
            show_system_info()
            wait_input()
        elif choice == '2':
            clean_disk()
            wait_input()
        elif choice == '3':
            optimize_ram()
            wait_input()
        elif choice == '4':
            optimize_services()
            wait_input()
        elif choice == '5':
            optimize_performance()
            wait_input()
        elif choice == '6':
            kill_background_apps()
            wait_input()
        elif choice == '7':
            auto_optimize_all()
            wait_input()
        elif choice == '8':
            optimize_network()
            wait_input()
        elif choice == '9':
            optimize_ssd()
            wait_input()
        elif choice == '10':
            toggle_windows_update()
            wait_input()
        elif choice == '11':
            toggle_context_menu()
            wait_input()
        elif choice == '0':
            print_banner()
            print_color("  Cảm ơn đã sử dụng Windows System Optimizer!", FOREGROUND_GREEN + FOREGROUND_INTENSITY)
            print_color("  Hẹn gặp lại.", FOREGROUND_WHITE)
            print_color("=" * 70, FOREGROUND_CYAN)
            time.sleep(1)
            break
        else:
            print_color("  Lựa chọn không hợp lệ!", FOREGROUND_RED)
            time.sleep(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\nĐã thoát bởi người dùng.", FOREGROUND_YELLOW)
        sys.exit(0)
    except Exception as e:
        print_color(f"\n\nLỗi không mong muốn: {e}", FOREGROUND_RED)
        input("Nhấn Enter để thoát...")
        sys.exit(1)
