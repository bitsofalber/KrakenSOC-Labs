<#
  DCSync — generador de evidencia SINTETICA (Windows Event Logs).

  NO ejecuta ningun ataque: escribe en un canal propio los registros que un
  DCSync produciria en un DC real (Event ID 4662 con los GUID de derechos de
  replicacion de Active Directory). 100% benigno, sin dominio, sin tooling —
  cyber-range de logs para analisis. No dispara alertas de seguridad.

  Flag por env SI_FLAG. MITRE: T1003.006 (OS Credential Dumping: DCSync).
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

Write-Host "[*] 2/3 Escribiendo el incidente (4662 con derechos de replicacion)..."
$attacker = "NORTHWIND\m.stone"     # cuenta NO-DC que abusa de replicacion
$dc       = "DC01"
# Los GUID de los extended rights que exige un DCSync:
$guids = @(
  "1131f6aa-9c07-11d1-f79f-00c04fc2dcd2",  # DS-Replication-Get-Changes
  "1131f6ad-9c07-11d1-f79f-00c04fc2dcd2",  # DS-Replication-Get-Changes-All
  "89e95b76-444d-4c62-991a-0facbeda640c"   # DS-Replication-Get-Changes-In-Filtered-Set
)
foreach ($g in $guids) {
  $msg = @"
An operation was performed on an object.

Subject:
	Account Name:		$attacker
	Account Domain:		NORTHWIND

Object:
	Object Server:		DS
	Object Type:		domainDNS
	Object Name:		DC=northwind,DC=local
	Handle ID:		0x0

Operation:
	Operation Type:		Object Access
	Accesses:		Control Access
	Properties:		Control Access
				{$g}
	Additional Info:	Replication rights requested from $dc
"@
  Write-EventLog -LogName $Log -Source $Src -EventId 4662 -EntryType Information -Category 0 -Message $msg
  Start-Sleep -Milliseconds 400
}

# Resultado: el atacante extrae los hashes del dominio (incl. krbtgt). La flag
# es el "loot" registrado por su herramienta.
$loot = @"
Directory replication completed (DCSync).

Replicated secrets for principal: NORTHWIND\krbtgt
NTLM Hash (krbtgt): a1b2c3d4e5f6...   [REDACTED]
Analyst token: $Flag
Tooling: mimikatz lsadump::dcsync
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4104 -EntryType Warning -Category 0 -Message $loot
Start-Sleep -Seconds 2

Write-Host "[*] 3/3 Exportando el .evtx..."
wevtutil epl $Log "$OutDir\Range-Security.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
