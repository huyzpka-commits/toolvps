#Requires -RunAsAdministrator
<#
.SYNOPSIS
    Windows System Optimizer PowerShell Edition
    Khong bi AV xoa - dung san cong cu Windows
.DESCRIPTION
    Toi uu RAM, CPU, giai phong o cung, tat service khong can thiet
    Phu hop: Windows 10/11, Windows Server 2022, PC/Laptop/VPS cau hinh thap
#>

$Host.UI.RawUI.BackgroundColor = "Black"
$Host.UI.RawUI.ForegroundColor = "White"
Clear-Host

function Draw-Header {
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host "       WINDOWS SYSTEM OPTIMIZER v2.0 - PowerShell Edition" -ForegroundColor Cyan
    Write-Host "       Toi uu cho PC | Laptop | VPS cau hinh thap" -ForegroundColor White
    Write-Host "       Windows 10/11 & Windows Server 2022" -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Show-SystemInfo {
    Draw-Header
    Write-Host "  [ THONG TIN HE THONG ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    # CPU
    $cpu = Get-CimInstance Win32_Processor | Select-Object -First 1
    $cpuLoad = (Get-CimInstance Win32_Processor | Measure-Object -Property LoadPercentage -Average).Average
    Write-Host "  CPU: $($cpu.Name)" -ForegroundColor White
    Write-Host "  Core: $($cpu.NumberOfCores) | Luong: $($cpu.NumberOfLogicalProcessors)" -ForegroundColor White
    Write-Host "  Su dung CPU: $([math]::Round($cpuLoad,1))%" -ForegroundColor $(if($cpuLoad -lt 80){"Yellow"}else{"Red"})
    $barLen = 40
    $filled = [math]::Floor($barLen * $cpuLoad / 100)
    $bar = "[" + ("#"*$filled) + ("-"*($barLen-$filled)) + "]"
    Write-Host "  $bar" -ForegroundColor $(if($cpuLoad -lt 50){"Green"}elseif($cpuLoad -lt 80){"Yellow"}else{"Red"})

    # RAM
    $os = Get-CimInstance Win32_OperatingSystem
    $totalRAM = $os.TotalVisibleMemorySize / 1MB
    $freeRAM = $os.FreePhysicalMemory / 1MB
    $usedRAM = $totalRAM - $freeRAM
    $ramPercent = [math]::Round(($usedRAM / $totalRAM) * 100, 1)
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  RAM Tong:    $([math]::Round($totalRAM,2)) GB" -ForegroundColor White
    Write-Host "  RAM Da dung: $([math]::Round($usedRAM,2)) GB ($ramPercent%)" -ForegroundColor $(if($ramPercent -lt 85){"Yellow"}else{"Red"})
    Write-Host "  RAM Trong:   $([math]::Round($freeRAM,2)) GB" -ForegroundColor Green
    $rFilled = [math]::Floor($barLen * $ramPercent / 100)
    $rBar = "[" + ("#"*$rFilled) + ("-"*($barLen-$rFilled)) + "]"
    Write-Host "  $rBar" -ForegroundColor $(if($ramPercent -lt 70){"Green"}elseif($ramPercent -lt 85){"Yellow"}else{"Red"})

    # Swap
    $pf = Get-CimInstance Win32_PageFileUsage | Select-Object -First 1
    if ($pf) {
        Write-Host "  Pagefile: $([math]::Round($pf.CurrentUsage/1024,2)) GB / $([math]::Round($pf.AllocatedBaseSize/1024,2)) GB" -ForegroundColor White
    }

    # Disk
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 3} | ForEach-Object {
        $used = $_.Size - $_.FreeSpace
        $pct = [math]::Round(($used / $_.Size) * 100, 1)
        $color = if ($pct -lt 80) { "Green" } elseif ($pct -lt 90) { "Yellow" } else { "Red" }
        Write-Host "  O $($_.DeviceID) | $([math]::Round($used/1GB,2)) GB / $([math]::Round($_.Size/1GB,2)) GB ($pct%)" -ForegroundColor $color
    }

    # Uptime
    $lastBoot = (Get-CimInstance Win32_OperatingSystem).LastBootUpTime
    $uptime = (Get-Date) - $lastBoot
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  Uptime: $($uptime.Days) ngay $($uptime.Hours) gio $($uptime.Minutes) phut" -ForegroundColor White
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Clean-Disk {
    Draw-Header
    Write-Host "  [ DON DEP O CUNG & FILE TAM ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    $totalFreed = 0

    $targets = @(
        @{Name="Temp nguoi dung"; Path=$env:TEMP},
        @{Name="Temp he thong"; Path="C:\Windows\Temp"},
        @{Name="Prefetch"; Path="C:\Windows\Prefetch"},
        @{Name="Recent Items"; Path="$env:USERPROFILE\Recent"},
        @{Name="Windows Update Cache"; Path="C:\Windows\SoftwareDistribution\Download"},
        @{Name="Windows Logs"; Path="C:\Windows\Logs"},
        @{Name="Minidump"; Path="C:\Windows\Minidump"},
        @{Name="Internet Cache"; Path="$env:LOCALAPPDATA\Microsoft\Windows\INetCache"},
        @{Name="Thumbnail Cache"; Path="$env:LOCALAPPDATA\Microsoft\Windows\Explorer"},
        @{Name="WER Reports"; Path="C:\ProgramData\Microsoft\Windows\WER"},
        @{Name="Temp Internet Explorer"; Path="$env:LOCALAPPDATA\Microsoft\Windows\Temporary Internet Files"}
    )

    foreach ($t in $targets) {
        if (Test-Path $t.Path) {
            try {
                $before = (Get-ChildItem $t.Path -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                if ($before -eq $null) { $before = 0 }
                Remove-Item -Path "$($t.Path)\*" -Recurse -Force -ErrorAction SilentlyContinue -Exclude *.log
                $after = (Get-ChildItem $t.Path -Recurse -Force -ErrorAction SilentlyContinue | Measure-Object -Property Length -Sum).Sum
                if ($after -eq $null) { $after = 0 }
                $freed = $before - $after
                $totalFreed += $freed
                Write-Host "  [OK] $($t.Name.PadRight(25)) - $([math]::Round($freed/1MB,2)) MB" -ForegroundColor Green
            } catch {
                Write-Host "  [ERR] $($t.Name.PadRight(25)) - $($_.Exception.Message.Substring(0,[Math]::Min(40,$_.Exception.Message.Length)))" -ForegroundColor Red
            }
        } else {
            Write-Host "  [SKIP] $($t.Name.PadRight(25)) - Khong ton tai" -ForegroundColor Yellow
        }
    }

    # Empty Recycle Bin
    try {
        Clear-RecycleBin -Force -ErrorAction SilentlyContinue
        Write-Host "  [OK] Recycle Bin             - Da don sach" -ForegroundColor Green
    } catch {
        Write-Host "  [WARN] Recycle Bin           - Khong the don" -ForegroundColor Yellow
    }

    # Windows Disk Cleanup (if available)
    try {
        Start-Process -FilePath "cleanmgr" -ArgumentList "/sagerun:1" -Wait -WindowStyle Hidden -ErrorAction SilentlyContinue
        Write-Host "  [OK] Disk Cleanup           - Da chay" -ForegroundColor Green
    } catch {
        Write-Host "  [SKIP] Disk Cleanup         - Khong khoi chay duoc" -ForegroundColor Yellow
    }

    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  [+] TONG DA GIAI PHONG: $([math]::Round($totalFreed/1MB,2)) MB ($([math]::Round($totalFreed/1GB,2)) GB)" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Optimize-RAM {
    Draw-Header
    Write-Host "  [ TOI UU & GIAI PHONG RAM ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    $os = Get-CimInstance Win32_OperatingSystem
    $beforeUsed = ($os.TotalVisibleMemorySize - $os.FreePhysicalMemory) / 1MB
    Write-Host "  Truoc khi toi uu: $([math]::Round($beforeUsed,2)) GB da dung" -ForegroundColor Yellow

    # 1. Trim working sets using RAMMap technique (via rundll32)
    Write-Host "`n  [1] Dang trim working sets..." -ForegroundColor White
    try {
        # ProcessIdleTasks flushes cache
        Start-Process -FilePath "rundll32.exe" -ArgumentList "advapi32.dll,ProcessIdleTasks" -Wait -WindowStyle Hidden -ErrorAction SilentlyContinue
        Write-Host "  -> Idle tasks hoan tat" -ForegroundColor Green
    } catch {
        Write-Host "  -> Idle tasks loi" -ForegroundColor Yellow
    }

    # 2. Clear standby list using RAMMap command if available
    Write-Host "`n  [2] Dang co gang giai phong standby list..." -ForegroundColor White
    $rammap = "C:\Sysinternals\RAMMap.exe"
    if (Test-Path $rammap) {
        try {
            Start-Process -FilePath $rammap -ArgumentList "-Ew" -Wait -WindowStyle Hidden -ErrorAction SilentlyContinue
            Write-Host "  -> RAMMap: Da giai phong standby list" -ForegroundColor Green
        } catch {
            Write-Host "  -> RAMMap loi" -ForegroundColor Yellow
        }
    } else {
        Write-Host "  -> RAMMap chua co. Khuyen nghi: tai Sysinternals RAMMap de giai phong sau hon." -ForegroundColor Yellow
    }

    # 3. Force garbage collection
    [System.GC]::Collect()
    [System.GC]::WaitForPendingFinalizers()

    # 4. Restart explorer if user agrees
    Write-Host "`n  [3] Khoi dong lai Explorer de giai phong handle?" -ForegroundColor Yellow
    Write-Host "      (Nhap 'y' de khoi dong lai, hoac Enter de bo qua)" -ForegroundColor Yellow
    $ans = Read-Host "  > "
    if ($ans -eq 'y') {
        try {
            Stop-Process -Name explorer -Force -ErrorAction SilentlyContinue
            Start-Sleep -Seconds 1
            Start-Process explorer
            Write-Host "  -> Explorer da khoi dong lai" -ForegroundColor Green
        } catch {
            Write-Host "  -> Loi khoi dong lai Explorer" -ForegroundColor Red
        }
    }

    Start-Sleep -Seconds 2
    $os2 = Get-CimInstance Win32_OperatingSystem
    $afterUsed = ($os2.TotalVisibleMemorySize - $os2.FreePhysicalMemory) / 1MB
    $saved = $beforeUsed - $afterUsed
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  Sau khi toi uu:  $([math]::Round($afterUsed,2)) GB da dung" -ForegroundColor Green
    if ($saved -gt 0) {
        Write-Host "  [+] RAM da giai phong: $([math]::Round($saved,2)) GB" -ForegroundColor Green
    } else {
        Write-Host "  [~] RAM on dinh (cache co the da tai su dung)" -ForegroundColor Yellow
    }
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Optimize-Services {
    Draw-Header
    Write-Host "  [ TOI UU DICH VU & NANG LUONG ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    $services = @(
        @{Name="WSearch"; Desc="Windows Search (lap chi muc)"},
        @{Name="SysMain"; Desc="SysMain / Superfetch"},
        @{Name="WMPNetworkSvc"; Desc="Windows Media Player Network Sharing"},
        @{Name="Fax"; Desc="Fax Service"},
        @{Name="DiagTrack"; Desc="Connected User Experiences and Telemetry"},
        @{Name="dmwappushservice"; Desc="WAP Push Service"},
        @{Name="MapsBroker"; Desc="Downloaded Maps Manager"},
        @{Name="WbioSrvc"; Desc="Windows Biometric Service"}
    )

    foreach ($svc in $services) {
        try {
            $s = Get-Service -Name $svc.Name -ErrorAction SilentlyContinue
            if ($s) {
                Stop-Service -Name $svc.Name -Force -ErrorAction SilentlyContinue
                Set-Service -Name $svc.Name -StartupType Disabled -ErrorAction SilentlyContinue
                Write-Host "  [OK] $($svc.Name.PadRight(20)) - $($svc.Desc)" -ForegroundColor Green
            } else {
                Write-Host "  [SKIP] $($svc.Name.PadRight(20)) - Khong tim thay" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "  [ERR] $($svc.Name.PadRight(20)) - $($_.Exception.Message.Substring(0,[Math]::Min(40,$_.Exception.Message.Length)))" -ForegroundColor Red
        }
    }

    # Power Plan High Performance
    Write-Host "`n  [+] Dang kich hoat High Performance..." -ForegroundColor White
    try {
        $hp = powercfg -duplicatescheme 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c 2>$null
        if ($hp -match "GUID: ([\w-]+)") {
            $guid = $matches[1]
            powercfg -setactive $guid | Out-Null
        } else {
            powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c | Out-Null
        }
        Write-Host "  -> High Performance da kich hoat" -ForegroundColor Green
    } catch {
        Write-Host "  -> Khong the doi power plan" -ForegroundColor Yellow
    }

    # Disable Hibernate
    Write-Host "`n  [+] Dang tat Hibernate..." -ForegroundColor White
    try {
        powercfg -h off | Out-Null
        Write-Host "  -> Hibernate da tat (giai phong o C:)" -ForegroundColor Green
    } catch {
        Write-Host "  -> Khong the tat Hibernate" -ForegroundColor Yellow
    }

    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Optimize-Performance {
    Draw-Header
    Write-Host "  [ TOI UU CPU & TANG TOC PHAN MEM ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    # 1. Visual Effects Best Performance
    Write-Host "  [1] Dang tat hieu ung hinh anh (Best Performance)..." -ForegroundColor White
    try {
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects" -Name "VisualFXSetting" -Value 2 -Type DWord -Force
        Set-ItemProperty -Path "HKCU:\Control Panel\Desktop" -Name "UserPreferencesMask" -Value ([byte[]](0x90,0x12,0x03,0x80,0x10,0x00,0x00,0x00)) -Force
        Write-Host "  -> Visual Effects: Best Performance" -ForegroundColor Green
    } catch {
        Write-Host "  -> Loi registry" -ForegroundColor Red
    }

    # 2. Disable Transparency
    Write-Host "`n  [2] Dang tat Transparency & Animations..." -ForegroundColor White
    try {
        Set-ItemProperty -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" -Name "EnableTransparency" -Value 0 -Type DWord -Force
        Set-ItemProperty -Path "HKCU:\Control Panel\Desktop\WindowMetrics" -Name "MinAnimate" -Value "0" -Type String -Force
        Write-Host "  -> Transparency & Animations: OFF" -ForegroundColor Green
    } catch {
        Write-Host "  -> Khong ap dung (co the la Windows Server)" -ForegroundColor Yellow
    }

    # 3. Network TCP optimization
    Write-Host "`n  [3] Dang toi uu TCP/IP..." -ForegroundColor White
    try {
        New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "TcpTimedWaitDelay" -Value 30 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters" -Name "MaxUserPort" -Value 65534 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Host "  -> Network stack da toi uu" -ForegroundColor Green
    } catch {
        Write-Host "  -> Khong the toi uu network" -ForegroundColor Yellow
    }

    # 4. Set current process priority to High
    Write-Host "`n  [4] Dang tang priority..." -ForegroundColor White
    try {
        $proc = Get-Process -Id $PID
        $proc.PriorityClass = [System.Diagnostics.ProcessPriorityClass]::High
        Write-Host "  -> Priority: HIGH" -ForegroundColor Green
    } catch {
        Write-Host "  -> Loi priority" -ForegroundColor Red
    }

    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Kill-BackgroundApps {
    Draw-Header
    Write-Host "  [ TAT UNG DUNG NEN KHONG CAN THIET ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    $apps = @(
        @{Process="OneDrive"; Name="OneDrive"},
        @{Process="Teams"; Name="Microsoft Teams"},
        @{Process="Skype"; Name="Skype"},
        @{Process="Spotify"; Name="Spotify"},
        @{Process="Dropbox"; Name="Dropbox"},
        @{Process="GoogleDriveFS"; Name="Google Drive"},
        @{Process="Steam"; Name="Steam Client"},
        @{Process="EpicGamesLauncher"; Name="Epic Games Launcher"}
    )

    for ($i=0; $i -lt $apps.Count; $i++) {
        Write-Host "  $($i+1). $($apps[$i].Process.PadRight(20)) ($($apps[$i].Name))" -ForegroundColor White
    }
    Write-Host "  0. Quay lai" -ForegroundColor White
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  Nhap so thu tu cach nhau boi dau phay (vi du: 1,2,3) hoac 'all'" -ForegroundColor Yellow
    $choice = Read-Host "  > "

    if ($choice -eq '0' -or $choice -eq '') { return }

    $selected = @()
    if ($choice -eq 'all') {
        $selected = 0..($apps.Count-1)
    } else {
        $choice.Split(',') | ForEach-Object {
            try { $selected += ([int]$_.Trim() - 1) } catch {}
        }
    }

    $killed = 0
    foreach ($idx in $selected) {
        if ($idx -ge 0 -and $idx -lt $apps.Count) {
            $app = $apps[$idx]
            try {
                Get-Process -Name $app.Process -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
                Write-Host "  [OK] Da tat $($app.Name)" -ForegroundColor Green
                $killed++
            } catch {
                Write-Host "  [ERR] $($app.Name): $($_.Exception.Message)" -ForegroundColor Red
            }
        }
    }
    Write-Host "`n  [+] Tong so process da tat: $killed" -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Optimize-Network {
    Draw-Header
    Write-Host "  [ TOI UU MANG (NETWORK) ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    # 1. Flush DNS
    Write-Host "  [1] Dang xoa DNS cache..." -ForegroundColor White
    try {
        ipconfig /flushdns | Out-Null
        Write-Host "  -> DNS cache da duoc xoa" -ForegroundColor Green
    } catch {
        Write-Host "  -> Loi xoa DNS cache" -ForegroundColor Red
    }

    # 2. TCP Registry
    Write-Host "`n  [2] Dang toi uu TCP/IP stack..." -ForegroundColor White
    $tcpParams = @{
        "TcpNoDelay" = 1
        "TcpAckFrequency" = 1
        "TCPWindowSize" = 65535
        "GlobalMaxTcpWindowSize" = 65535
        "DefaultTTL" = 64
        "EnablePMTUDiscovery" = 1
        "SackOpts" = 1
        "TcpMaxDupAcks" = 2
        "DisableTaskOffload" = 0
    }
    try {
        $key = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters"
        if (!(Test-Path $key)) { New-Item -Path $key -Force | Out-Null }
        foreach ($p in $tcpParams.GetEnumerator()) {
            New-ItemProperty -Path $key -Name $p.Key -Value $p.Value -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        }
        Write-Host "  -> TCP/IP registry da toi uu" -ForegroundColor Green
    } catch {
        Write-Host "  -> Loi registry TCP: $($_.Exception.Message)" -ForegroundColor Red
    }

    # 3. Netsh global
    Write-Host "`n  [3] Dang toi uu Netsh TCP/IP global..." -ForegroundColor White
    try {
        netsh interface tcp set global autotuninglevel=normal | Out-Null
        netsh interface tcp set global rss=enabled | Out-Null
        netsh interface tcp set global netdma=enabled | Out-Null
        netsh interface tcp set global timestamps=disabled | Out-Null
        netsh interface tcp set global ecncapability=disabled | Out-Null
        netsh interface tcp set global chimney=disabled | Out-Null
        Write-Host "  -> Netsh global da toi uu" -ForegroundColor Green
    } catch {
        Write-Host "  -> Loi netsh" -ForegroundColor Red
    }

    # 4. QoS / Throttling
    Write-Host "`n  [4] Dang toi uu QoS & Throttling..." -ForegroundColor White
    try {
        $sysProfile = "HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Multimedia\SystemProfile"
        if (!(Test-Path $sysProfile)) { New-Item -Path $sysProfile -Force | Out-Null }
        New-ItemProperty -Path $sysProfile -Name "SystemResponsiveness" -Value 0 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null

        $psched = "HKLM:\SOFTWARE\Policies\Microsoft\Windows\Psched"
        if (!(Test-Path $psched)) { New-Item -Path $psched -Force | Out-Null }
        New-ItemProperty -Path $psched -Name "NonBestEffortLimit" -Value 0 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Host "  -> QoS & Throttling da toi uu" -ForegroundColor Green
    } catch {
        Write-Host "  -> QoS: Mot so gia tri khong ap dung duoc" -ForegroundColor Yellow
    }

    # 5. Disable IPv6 optional
    Write-Host "`n  [5] Tat IPv6 de giam overhead? (Nhap 'y' de tat, Enter de bo qua)" -ForegroundColor Yellow
    $ans = Read-Host "  > "
    if ($ans -eq 'y') {
        try {
            $ipv6Key = "HKLM:\SYSTEM\CurrentControlSet\Services\Tcpip6\Parameters"
            if (!(Test-Path $ipv6Key)) { New-Item -Path $ipv6Key -Force | Out-Null }
            New-ItemProperty -Path $ipv6Key -Name "DisabledComponents" -Value 0xFF -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
            Write-Host "  -> IPv6 da tat (can khoi dong lai)" -ForegroundColor Green
        } catch {
            Write-Host "  -> Loi tat IPv6" -ForegroundColor Red
        }
    }

    Write-Host "`n  [TIP] Khuyen nghi khoi dong lai may de ap dung toi uu mang." -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Optimize-SSD {
    Draw-Header
    Write-Host "  [ TOI UU SSD ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    # Detect SSD
    Write-Host "  Dang quet o dia..." -ForegroundColor White
    $ssdFound = $false
    try {
        $disks = Get-CimInstance Win32_DiskDrive | Where-Object { $_.MediaType -match "SSD|Solid" }
        if ($disks) {
            foreach ($disk in $disks) {
                $ssdFound = $true
                Write-Host "  [SSD] $($disk.Model) ($([math]::Round($disk.Size/1GB,0)) GB)" -ForegroundColor Green
            }
        }
    } catch {}
    if (-not $ssdFound) {
        Write-Host "  [CANH BAO] Khong phat hien SSD ro rang. Toi uu van se chay (co the khong co hieu qua tren HDD)." -ForegroundColor Yellow
    }

    # 1. TRIM
    Write-Host "`n  [1] Kiem tra TRIM..." -ForegroundColor White
    try {
        $trim = fsutil behavior query DisableDeleteNotify 2>$null
        if ($trim -match "DisableDeleteNotify = 0") {
            Write-Host "  -> TRIM da BAT (OK)" -ForegroundColor Green
        } else {
            fsutil behavior set DisableDeleteNotify 0 | Out-Null
            Write-Host "  -> TRIM da duoc BAT" -ForegroundColor Green
        }
    } catch {
        Write-Host "  -> Loi TRIM" -ForegroundColor Red
    }

    # 2. Disable Last Access Timestamp
    Write-Host "`n  [2] Tat Last Access Timestamp..." -ForegroundColor White
    try {
        fsutil behavior set DisableLastAccess 1 | Out-Null
        Write-Host "  -> Last Access Timestamp: TAT" -ForegroundColor Green
    } catch {
        Write-Host "  -> Loi" -ForegroundColor Red
    }

    # 3. Disable Prefetch & Superfetch
    Write-Host "`n  [3] Tat Prefetch & Superfetch..." -ForegroundColor White
    try {
        $pfKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management\PrefetchParameters"
        if (!(Test-Path $pfKey)) { New-Item -Path $pfKey -Force | Out-Null }
        New-ItemProperty -Path $pfKey -Name "EnablePrefetcher" -Value 0 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        New-ItemProperty -Path $pfKey -Name "EnableSuperfetch" -Value 0 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        New-ItemProperty -Path $pfKey -Name "EnableBoottrace" -Value 0 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Host "  -> Prefetch & Superfetch: TAT" -ForegroundColor Green
    } catch {
        Write-Host "  -> Loi registry" -ForegroundColor Red
    }

    # 4. Disable Scheduled Defrag
    Write-Host "`n  [4] Tat Scheduled Defrag..." -ForegroundColor White
    try {
        schtasks /Change /TN "\Microsoft\Windows\Defrag\ScheduledDefrag" /DISABLE 2>$null | Out-Null
        Write-Host "  -> Scheduled Defrag: TAT" -ForegroundColor Green
    } catch {
        Write-Host "  -> Scheduled Defrag khong tim thay hoac da tat" -ForegroundColor Yellow
    }

    # 5. Disable ClearPageFileAtShutdown
    Write-Host "`n  [5] Tat ClearPageFileAtShutdown..." -ForegroundColor White
    try {
        $mmKey = "HKLM:\SYSTEM\CurrentControlSet\Control\Session Manager\Memory Management"
        New-ItemProperty -Path $mmKey -Name "ClearPageFileAtShutdown" -Value 0 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Host "  -> ClearPageFileAtShutdown: TAT" -ForegroundColor Green
    } catch {
        Write-Host "  -> Khong the set ClearPageFileAtShutdown" -ForegroundColor Yellow
    }

    # 6. NTFS Memory Usage
    Write-Host "`n  [6] Tang NTFS Memory Usage..." -ForegroundColor White
    try {
        $fsKey = "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem"
        New-ItemProperty -Path $fsKey -Name "NtfsMemoryUsage" -Value 2 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
        Write-Host "  -> NTFS MemoryUsage: 2 (High)" -ForegroundColor Green
    } catch {
        Write-Host "  -> Khong the set NtfsMemoryUsage" -ForegroundColor Yellow
    }

    Write-Host "`n  [TIP] Khuyen nghi khoi dong lai de ap dung tat ca toi uu SSD." -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Toggle-WindowsUpdate {
    Draw-Header
    Write-Host "  [ QUAN LY WINDOWS UPDATE ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  1. TAT Windows Update tam thoi" -ForegroundColor Red
    Write-Host "  2. BAT lai Windows Update" -ForegroundColor Green
    Write-Host "  0. Quay lai" -ForegroundColor White
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan

    $choice = Read-Host "  Nhap lua chon"
    switch ($choice) {
        '1' {
            Write-Host "`n  Dang TAT Windows Update..." -ForegroundColor Yellow
            $services = @("wuauserv", "bits", "dosvc", "usosvc", "WaaSMedicSvc")
            foreach ($svc in $services) {
                try {
                    Stop-Service -Name $svc -Force -ErrorAction SilentlyContinue
                    Set-Service -Name $svc -StartupType Disabled -ErrorAction SilentlyContinue
                    Write-Host "  [OK] $svc : TAT" -ForegroundColor Green
                } catch {
                    Write-Host "  [WARN] $svc : Khong the tat" -ForegroundColor Yellow
                }
            }
            # Registry fallback for WaaSMedicSvc
            try {
                New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\WaaSMedicSvc" -Name "Start" -Value 4 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
            } catch {}
            Write-Host "`n  [+] Windows Update da TAT tam thoi." -ForegroundColor Green
            Write-Host "  [TIP] Chon '2' trong menu nay de BAT lai khi can." -ForegroundColor Cyan
        }
        '2' {
            Write-Host "`n  Dang BAT Windows Update..." -ForegroundColor Green
            $services = @("wuauserv", "bits", "dosvc", "usosvc")
            foreach ($svc in $services) {
                try {
                    Set-Service -Name $svc -StartupType Manual -ErrorAction SilentlyContinue
                    Start-Service -Name $svc -ErrorAction SilentlyContinue
                    Write-Host "  [OK] $svc : BAT" -ForegroundColor Green
                } catch {
                    Write-Host "  [WARN] $svc : Khong the bat" -ForegroundColor Yellow
                }
            }
            try {
                New-ItemProperty -Path "HKLM:\SYSTEM\CurrentControlSet\Services\WaaSMedicSvc" -Name "Start" -Value 3 -PropertyType DWord -Force -ErrorAction SilentlyContinue | Out-Null
            } catch {}
            Write-Host "`n  [+] Windows Update da BAT lai." -ForegroundColor Green
        }
    }
    Write-Host "======================================================================" -ForegroundColor Cyan
}

function Auto-OptimizeAll {
    Draw-Header
    Write-Host "  [ TU DONG TOI UU TOAN BO - 1 CLICK ]" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  Bat dau toi uu toan dien..." -ForegroundColor Yellow
    Start-Sleep -Seconds 1

    Show-SystemInfo
    Read-Host "`n  Nhan Enter de bat dau toi uu..."

    Clean-Disk
    Read-Host "`n  Nhan Enter de tiep tuc..."

    Optimize-RAM
    Read-Host "`n  Nhan Enter de tiep tuc..."

    Optimize-Services
    Read-Host "`n  Nhan Enter de tiep tuc..."

    Optimize-Performance
    Read-Host "`n  Nhan Enter de tiep tuc..."

    Draw-Header
    Write-Host "  [ TOI UU HOAN TAT ]" -ForegroundColor Green
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Show-SystemInfo
    Write-Host "`n  [TIP] Khoi dong lai may de ap dung tat ca thay doi dich vu." -ForegroundColor Cyan
    Write-Host "======================================================================" -ForegroundColor Cyan
}

# MAIN MENU
while ($true) {
    Draw-Header
    Write-Host "  MENU CHINH:" -ForegroundColor Cyan
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  1. Xem thong tin he thong (CPU, RAM, Disk, Uptime)" -ForegroundColor White
    Write-Host "  2. Don dep o cung & file tam (giai phong GB)" -ForegroundColor White
    Write-Host "  3. Toi uu & giai phong RAM (flush cache, idle tasks)" -ForegroundColor White
    Write-Host "  4. Toi uu dich vu & nang luong (High Performance)" -ForegroundColor White
    Write-Host "  5. Toi uu CPU & tang toc phan mem (tat hieu ung, toi uu TCP)" -ForegroundColor White
    Write-Host "  6. Tat ung dung nen khong can thiet (OneDrive, Teams...)" -ForegroundColor White
    Write-Host "  7. TU DONG TOI UU TAT CA (1-Click)" -ForegroundColor Green
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  8. Toi uu mang (flush DNS, TCP/IP, RSS, QoS, IPv6)" -ForegroundColor White
    Write-Host "  9. Toi uu SSD (TRIM, Prefetch, Defrag, NTFS)" -ForegroundColor White
    Write-Host " 10. Tat/Bat Windows Update tam thoi" -ForegroundColor White
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  0. Thoat" -ForegroundColor Red
    Write-Host "----------------------------------------------------------------------" -ForegroundColor Cyan
    Write-Host "  Yeu cau: Chay bang Administrator de toi uu dich vu & services." -ForegroundColor Yellow
    Write-Host "======================================================================" -ForegroundColor Cyan

    $choice = Read-Host "  Nhap lua chon"
    switch ($choice) {
        '1' { Show-SystemInfo; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '2' { Clean-Disk; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '3' { Optimize-RAM; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '4' { Optimize-Services; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '5' { Optimize-Performance; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '6' { Kill-BackgroundApps; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '7' { Auto-OptimizeAll }
        '8' { Optimize-Network; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '9' { Optimize-SSD; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '10' { Toggle-WindowsUpdate; Read-Host "`n  Nhan Enter de quay lai menu..." }
        '0' {
            Draw-Header
            Write-Host "  Cam on da su dung Windows System Optimizer!" -ForegroundColor Green
            Write-Host "  Hen gap lai." -ForegroundColor White
            Write-Host "======================================================================" -ForegroundColor Cyan
            Start-Sleep -Seconds 1
            exit
        }
        default { Write-Host "  Lua chon khong hop le!" -ForegroundColor Red; Start-Sleep -Seconds 1 }
    }
}
