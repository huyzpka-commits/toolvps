# Windows System Optimizer

Tool tối ưu hóa hệ thống Windows dành cho **PC, Laptop, VPS cấu hình thấp** — chạy được trên Windows 10, Windows 11 và **Windows Server 2022**.

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

---

## Mục đích

- **Tối ưu RAM** — Giải phóng bộ nhớ, xóa cache, trim working sets
- **Tối ưu CPU** — Tắt hiệu ứng hình ảnh, bật High Performance, tối ưu TCP/IP
- **Tăng tốc phần mềm** — Tắt ứng dụng nền, tối ưu services
- **Giải phóng ổ cứng** — Dọn file tạm, cache, log, Recycle Bin, tắt Hibernate

---

## Tính năng chính

| Chức năng | Mô tả |
|-----------|-------|
| **1. Thông tin hệ thống** | Hiển thị real-time CPU, RAM, Disk, Uptime |
| **2. Dọn dẹp ổ cứng** | Xóa Temp, Prefetch, Update cache, Logs, Recycle Bin, WER... |
| **3. Giải phóng RAM** | Trim working sets, flush cache, ProcessIdleTasks, standby list |
| **4. Tối ưu dịch vụ** | Tắt WSearch, SysMain, DiagTrack, Fax... Bật High Performance |
| **5. Tối ưu CPU & hiệu năng** | Tắt visual effects, transparency, animations. Tối ưu TCP/IP |
| **6. Tắt ứng dụng nền** | OneDrive, Teams, Skype, Spotify, Steam, Epic Games... |
| **7. Tự động tất cả** | 1-Click chạy toàn bộ tối ưu tự động |
| **8. Tối ưu mạng** | Flush DNS, TCP/IP, RSS, Auto-Tuning, QoS, tùy chọn tắt IPv6 |
| **9. Tối ưu SSD** | TRIM, tắt Prefetch/Superfetch, Scheduled Defrag, NTFS cache |
| **10. Tắt/Bật Windows Update** | Tạm thời tắt hoặc bật lại Windows Update và dịch vụ liên quan |

---

## Cách sử dụng (khuyên dùng — không bị AV xóa)

### Cách 1: PowerShell + Batch (Không bị Antivirus xóa)

> Khuyên dùng cho PC, Laptop, VPS — không cần cài Python, không bị Windows Defender xóa.

1. **Download code**:
   ```bash
   git clone https://github.com/huyzpka-commits/toolvps.git
   cd toolvps
   ```

2. **Chạy tool** (có thể double-click file `Run-Optimizer.bat`):
   ```powershell
   powershell -ExecutionPolicy Bypass -File WinOptimizer.ps1
   ```

   Hoặc click đúp `Run-Optimizer.bat` — tool sẽ tự chạy.

3. **Chọn chức năng** bằng bàn phím (1-10).

### Cách 2: Build file `.exe` (Python cần thiết)

1. **Cài Python 3.8+** từ [python.org](https://python.org)

2. **Cài thư viện & build**:
   ```bash
   pip install -r requirements.txt
   build_safe.bat
   ```

3. **File `.exe` sẽ nằm trong** `dist\WinOptimizer\WinOptimizer.exe`

   > **Lưu ý:** File `.exe` build bằng PyInstaller đôi khi bị Windows Defender nhận nhầm (false positive). Nếu bị xóa, hãy dùng **Cách 1 (PowerShell)** hoặc thêm thư mục vào **Exclusion** của Windows Defender.

---

## Yêu cầu

| Thành phần | Bắt buộc | Ghi chú |
|------------|----------|---------|
| Windows 10/11 hoặc Server 2022 | ✅ | |
| PowerShell | ✅ | Có sẵn trên Windows |
| Python 3.8+ | ❌ | Chỉ cần nếu build `.exe` |
| Quyền Administrator | ✅ Khuyến nghị | Để tối ưu services, power plan, registry |

---

## Khắc phục lỗi Antivirus (False Positive)

### Thêm ngoại lệ Windows Defender (PowerShell Admin):
```powershell
Add-MpPreference -ExclusionPath "C:\Duong\Dan\Toi\toolvps"
```

### Hoặc tắt tạm Real-time Protection:
```powershell
Set-MpPreference -DisableRealtimeMonitoring $true
# Chạy tool xong, bật lại:
Set-MpPreference -DisableRealtimeMonitoring $false
```

> **Lưu ý an toàn:** Chỉ thêm ngoại lệ cho file/tool từ nguồn đáng tin cậy. Không bao giờ thêm ngoại lệ cho file tải từ Internet không rõ nguồn gốc.

---

## Danh sách file

| File | Mục đích |
|------|----------|
| `WinOptimizer.ps1` | Script PowerShell chính (không bị AV xóa) |
| `Run-Optimizer.bat` | Batch wrapper để chạy PS1 dễ dàng |
| `win_optimizer.py` | Mã nguồn Python gốc |
| `build.bat` | Build `.exe` dạng 1 file |
| `build_safe.bat` | Build `.exe` dạng thư mục (ít bị AV detect) |
| `requirements.txt` | Thư viện Python cần thiết |
| `version_info.txt` | Thông tin version cho file `.exe` |
| `AV_EXCEPTION_GUIDE.txt` | Hướng dẫn thêm ngoại lệ AV |

---

## Khuyến nghị sử dụng theo môi trường

| Môi trường | Phương án khuyên dùng |
|------------|----------------------|
| **PC/Laptop cá nhân** | `Run-Optimizer.bat` hoặc thêm AV exclusion rồi dùng `.exe` |
| **VPS/Server 2022 không có Python** | Copy cả thư mục `dist\WinOptimizer\` hoặc chạy PS1 trực tiếp |
| **VPS bị AV chặt chẽ** | Chỉ dùng `WinOptimizer.ps1` hoặc `Run-Optimizer.bat` |

---

## Lưu ý quan trọng

1. **Chạy với quyền Administrator** để tối ưu dịch vụ, đổi power plan, và sửa registry.
2. **Nên khởi động lại máy** sau khi tối ưu dịch vụ để các thay đổi có hiệu lực hoàn toàn.
3. **Chạy định kỳ** 1 tuần/lần hoặc sau mỗi lần cập nhật Windows lớn để dọn cache.
4. **Tool chỉ cần ~8-10 MB RAM** khi chạy, không cài đặt, không để lại rác registry.

---

## Giấy phép

MIT License — Sử dụng tự do cho mục đích cá nhân và thương mại.

---

**Mọi đóng góp và báo lỗi đều được hoan nghênh!**
