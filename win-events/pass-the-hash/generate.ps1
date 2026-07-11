<#
  Pass-the-Hash — generador de evidencia SINTETICA (Windows Event Logs).

  NO ejecuta ningun ataque: escribe en un canal propio los registros que un
  Pass-the-Hash produciria. La firma es un 4624 Logon Type 3 con Authentication
  Package NTLM y Logon Process NtLmSsp (autenticacion con el hash, no con la
  contraseña ni Kerberos), reforzado por un 4776 (validacion de credenciales
  NTLM). 100% benigno, sin dominio, sin tooling.

  Flag por env SI_FLAG. MITRE: T1550.002 (Use Alternate Authentication Material:
  Pass the Hash).
#>
param([string]$OutDir = "C:\evidence")
$ErrorActionPreference = "Continue"
$Flag = $env:SI_FLAG; if (-not $Flag) { $Flag = "NORTHWIND{unset_flag}" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Log = "KrakenSOC-Range"
$Src = "Security-Auditing-Sim"
Write-Host "[*] 1/3 Registrando canal del range (sintetico)..."
if (-not [System.Diagnostics.EventLog]::SourceExists($Src)) { New-EventLog -LogName $Log -Source $Src }
wevtutil cl $Log 2>$null
Start-Sleep -Seconds 1

Write-Host "[*] 2/3 Escribiendo el incidente (4624 NTLM tipo 3 + 4776)..."
$acct   = "Administrator"
$src_ws = "WKSTN-07"          # el host desde el que salta el atacante
$target = "FS01"
# 4776: la maquina valida las credenciales NTLM
$m4776 = @"
The computer attempted to validate the credentials for an account.

Authentication Package:	MICROSOFT_AUTHENTICATION_PACKAGE_V1_0
Logon Account:		$acct
Source Workstation:	$src_ws
Error Code:		0x0
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4776 -EntryType Information -Category 0 -Message $m4776
Start-Sleep -Milliseconds 400

# 4624: logon de red con NTLM usando el hash (no la contraseña)
$m4624 = @"
An account was successfully logged on.

Subject:
	Security ID:		NULL SID

Logon Information:
	Logon Type:		3
	Restricted Admin Mode:	-
	Virtual Account:	No
	Elevated Token:		Yes

New Logon:
	Account Name:		$acct
	Account Domain:		NORTHWIND

Process Information:
	Process Name:		-

Network Information:
	Workstation Name:	$src_ws
	Source Network Address:	10.0.42.55

Detailed Authentication Information:
	Logon Process:		NtLmSsp
	Authentication Package:	NTLM
	Package Name (NTLM only):	NTLM V2
	Key Length:		0
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4624 -EntryType Information -Category 0 -Message $m4624
Start-Sleep -Milliseconds 400

$loot = @"
Lateral authentication with stolen NT hash (Pass-the-Hash).

Reused NT hash for: NORTHWIND\$acct
No plaintext password or Kerberos TGT involved.
Analyst token: $Flag
Tooling: mimikatz sekurlsa::pth
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4104 -EntryType Warning -Category 0 -Message $loot
Start-Sleep -Seconds 2

Write-Host "[*] 3/3 Exportando el .evtx..."
wevtutil epl $Log "$OutDir\Range-Security.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
