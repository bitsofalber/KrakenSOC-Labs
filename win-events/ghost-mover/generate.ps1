<#
  Ghost Mover — generador de evidencia (Windows Event Logs).

  Escenario (Lateral Movement): el atacante se mueve a este host al estilo
  PsExec — un logon de red (Event ID 4624, Logon Type 3) seguido de la
  instalacion de un SERVICIO que ejecuta su payload (Event ID 7045 en System,
  4697 en Security). El binPath del servicio esconde un PowerShell -enc.

  Flag por env SI_FLAG. Va Base64 dentro del binPath del servicio (7045) — el
  alumno lo decodifica. MITRE: T1021.002 (SMB/Admin Shares), T1569.002
  (Service Execution), T1059.001.
#>
param([string]$OutDir = "C:\evidence")
$ErrorActionPreference = "Continue"
$Flag = $env:SI_FLAG; if (-not $Flag) { $Flag = "NORTHWIND{unset_flag}" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "[*] 1/6 Audit policies + Script Block Logging..."
auditpol /set /subcategory:"Logon" /success:enable /failure:enable | Out-Null
auditpol /set /subcategory:"Security System Extension" /success:enable | Out-Null
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

Write-Host "[*] 3/6 Limpiando logs (evidencia enfocada)..."
wevtutil cl Security 2>$null
wevtutil cl System 2>$null
wevtutil cl "Microsoft-Windows-PowerShell/Operational" 2>$null
wevtutil cl "Microsoft-Windows-Sysmon/Operational" 2>$null
Start-Sleep -Seconds 2

Write-Host "[*] 4/6 Escenario: logon de red (tipo 3) del atacante..."
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class NL { [DllImport("advapi32.dll", SetLastError=true)]
  public static extern bool LogonUser(string u, string d, string p, int t, int pr, out IntPtr tok); }
"@
# Cuenta de servicio con la que "llega" el atacante desde otro host
net user svc_backup "R3m0te-2026!" /add | Out-Null
net localgroup Administrators svc_backup /add | Out-Null
$tok = [IntPtr]::Zero
[NL]::LogonUser("svc_backup", $env:COMPUTERNAME, "R3m0te-2026!", 3, 0, [ref]$tok) | Out-Null  # 4624 type 3

Write-Host "[*] 5/6 Escenario: instalacion del servicio malicioso (7045)..."
# El binPath esconde el payload en Base64 -> el 7045 lo registra, el alumno lo decodifica
$svcPayload = "`$c2='10.20.30.40'; `$key='$Flag'; Write-Output `$key"
$svcEnc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($svcPayload))
sc.exe create "NetSyncSvc" binPath= "cmd.exe /c powershell.exe -nop -w hidden -enc $svcEnc" start= demand DisplayName= "Network Sync Service" | Out-Null
Start-Sleep -Seconds 1
sc.exe start "NetSyncSvc" 2>$null | Out-Null   # el arranque falla (no es un servicio real), pero el 7045 ya se registro
Start-Sleep -Seconds 6

Write-Host "[*] 6/6 Exportando .evtx..."
wevtutil epl System   "$OutDir\System.evtx" /ow:true            # 7045 (service install)
wevtutil epl Security "$OutDir\Security.evtx" /ow:true          # 4624 type 3, 4697
wevtutil epl "Microsoft-Windows-Sysmon/Operational" "$OutDir\Sysmon.evtx" /ow:true
wevtutil epl "Microsoft-Windows-PowerShell/Operational" "$OutDir\PowerShell.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
