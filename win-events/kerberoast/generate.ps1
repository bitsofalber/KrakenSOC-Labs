<#
  Kerberoasting — generador de evidencia SINTETICA (Windows Event Logs).

  IMPORTANTE: este generador NO ejecuta ningun ataque. No toca Defender, no
  accede a LSASS, no descarga herramientas, no necesita un dominio. Simplemente
  ESCRIBE en un canal de eventos propio los registros que un Kerberoasting
  produciria en un DC real (Event ID 4769 con cifrado RC4). Es un cyber-range
  de logs, 100% benigno — pensado para que un analista los estudie en su Event
  Viewer. Por eso no dispara ninguna alerta de seguridad.

  Flag por env SI_FLAG. MITRE: T1558.003 (Steal or Forge Kerberos Tickets:
  Kerberoasting).
#>
param([string]$OutDir = "C:\evidence")
$ErrorActionPreference = "Continue"
$Flag = $env:SI_FLAG; if (-not $Flag) { $Flag = "NORTHWIND{unset_flag}" }
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null

$Log = "KrakenSOC-Range"
$Src = "Security-Auditing-Sim"
Write-Host "[*] 1/3 Registrando canal de eventos del range (sintetico, benigno)..."
if (-not [System.Diagnostics.EventLog]::SourceExists($Src)) {
  New-EventLog -LogName $Log -Source $Src
}
# Log limpio para dejar solo los eventos del incidente
wevtutil cl $Log 2>$null
Start-Sleep -Seconds 1

Write-Host "[*] 2/3 Escribiendo los eventos del incidente (4769 RC4)..."
$attacker = "m.stone"
$domain   = "NORTHWIND.LOCAL"
$client   = "::ffff:10.0.42.55"
# El atacante pide TGS de varias cuentas de servicio, forzando RC4 (0x17) para
# poder crackear el hash offline. La ráfaga de 4769 con 0x17 es la firma.
$spns = @(
  @{ svc="MSSQLSvc/db01.northwind.local:1433"; acct="svc_sql" },
  @{ svc="HTTP/intranet.northwind.local";      acct="svc_web" },
  @{ svc="CIFS/fs01.northwind.local";          acct="svc_files" },
  @{ svc="MSSQLSvc/db02.northwind.local:1433"; acct="svc_sql2" },
  @{ svc="HTTP/reports.northwind.local";       acct="svc_report" }
)
foreach ($s in $spns) {
  $msg = @"
A Kerberos service ticket was requested.

Account Information:
	Account Name:		$attacker
	Account Domain:		$domain
	Logon GUID:		{9f2c1b70-5a11-4c88-9d2e-77aa10bb42cd}

Service Information:
	Service Name:		$($s.svc)
	Service ID:		$domain\$($s.acct)

Network Information:
	Client Address:		$client
	Client Port:		0

Additional Information:
	Ticket Options:		0x40810000
	Ticket Encryption Type:	0x17
	Failure Code:		0x0
	Transited Services:	-
"@
  Write-EventLog -LogName $Log -Source $Src -EventId 4769 -EntryType Information -Category 0 -Message $msg
  Start-Sleep -Milliseconds 400
}

# El atacante crackea offline el hash RC4 del servicio mas debil -> recupera la
# contraseña (la flag). Registro sintetico de la salida de la herramienta.
$crack = @"
Offline credential recovery (kerberoasting).

The RC4-HMAC service ticket for 'svc_sql' was extracted and cracked offline.
Cracked Service Account: $domain\svc_sql
Recovered Password: $Flag
Tooling: hashcat -m 13100
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4104 -EntryType Warning -Category 0 -Message $crack
Start-Sleep -Seconds 2

Write-Host "[*] 3/3 Exportando el .evtx..."
wevtutil epl $Log "$OutDir\Range-Security.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
