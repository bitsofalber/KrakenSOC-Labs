<#
  Cover Tracks — generador de evidencia (Windows Event Logs).

  Escenario (Defense Evasion): tras actuar, el atacante BORRA el registro de
  Security y el de System para cubrir sus huellas (Event ID 1102 en Security,
  104 en System). Pero olvida dos canales: Sysmon (que capturo el wevtutil.exe
  que uso para borrar) y PowerShell/Operational (que conserva su payload). La
  leccion: nunca te fies de un solo log; correla varios.

  Flag por env SI_FLAG. Vive en el 4104 (PowerShell/Operational, NO borrado).
  MITRE: T1070.001 (Indicator Removal: Clear Windows Event Logs), T1059.001.
#>
param([string]$OutDir = "C:\evidence")
$ErrorActionPreference = "Continue"
$Flag = $env:SI_FLAG; if (-not $Flag) { $Flag = "NORTHWIND{unset_flag}" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "[*] 1/6 Audit policies + Script Block Logging..."
auditpol /set /subcategory:"Logon" /success:enable /failure:enable | Out-Null
auditpol /set /subcategory:"Process Creation" /success:enable | Out-Null
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f | Out-Null
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Name EnableScriptBlockLogging -Value 1

Write-Host "[*] 2/6 Instalando Sysmon..."
try {
  Invoke-WebRequest -UseBasicParsing -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "$env:TEMP\Sysmon.zip"
  Expand-Archive "$env:TEMP\Sysmon.zip" -DestinationPath "$env:TEMP\sysmon" -Force
  Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile "$env:TEMP\sysmonconfig.xml"
  & "$env:TEMP\sysmon\Sysmon64.exe" -accepteula -i "$env:TEMP\sysmonconfig.xml" | Out-Null
  Start-Sleep -Seconds 5
} catch { Write-Host "[!] Sysmon no disponible: $_" }

Write-Host "[*] 3/6 Limpiando logs de arranque (deja el escenario limpio)..."
wevtutil cl "Microsoft-Windows-PowerShell/Operational" 2>$null
wevtutil cl "Microsoft-Windows-Sysmon/Operational" 2>$null
Start-Sleep -Seconds 2

Write-Host "[*] 4/6 Escenario: actividad + payload (queda en PowerShell/Operational)..."
# El payload malicioso del atacante -> 4104 con la flag (este log NO lo borra)
$payload = "`$stage='exfil'; `$note='clearing my tracks next'; `$token='$Flag'; Write-Output `$token"
$enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($payload))
powershell.exe -NoProfile -EncodedCommand $enc | Out-Null
Start-Sleep -Seconds 3

Write-Host "[*] 5/6 Anti-forense: el atacante BORRA Security y System..."
# Esto genera 1102 (Security) y 104 (System). El wevtutil.exe queda en Sysmon (Event 1).
wevtutil cl System 2>$null
wevtutil cl Security 2>$null
Start-Sleep -Seconds 6

Write-Host "[*] 6/6 Exportando .evtx..."
wevtutil epl Security "$OutDir\Security.evtx" /ow:true          # contiene el 1102
wevtutil epl System   "$OutDir\System.evtx" /ow:true            # contiene el 104
wevtutil epl "Microsoft-Windows-Sysmon/Operational" "$OutDir\Sysmon.evtx" /ow:true
wevtutil epl "Microsoft-Windows-PowerShell/Operational" "$OutDir\PowerShell.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
