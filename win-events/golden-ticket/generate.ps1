<#
  Golden Ticket — generador de evidencia SINTETICA (Windows Event Logs).

  NO ejecuta ningun ataque: escribe en un canal propio los registros que un
  Golden Ticket produciria. La firma clasica es un 4769 (peticion de TGS) SIN
  el 4768 (peticion de TGT) que normalmente lo precede — porque el TGT fue
  FORJADO offline con el hash de krbtgt, no emitido por el KDC. Ademas: cifrado
  RC4 y anomalias de dominio (marca de mimikatz). 100% benigno.

  Flag por env SI_FLAG. MITRE: T1558.001 (Golden Ticket).
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

Write-Host "[*] 2/3 Escribiendo el incidente (4769 forjado, sin 4768 previo)..."
$forged  = "administrator"
$domain  = "NORTHWIND.LOCAL"
# 4769 de un TGS usando el ticket forjado. NO hay 4768 previo para esta sesion:
# esa ausencia es la prueba de que el TGT no lo emitio el KDC.
$msg1 = @"
A Kerberos service ticket was requested.

Account Information:
	Account Name:		$forged
	Account Domain:		eo.oe.kiwi:)          <-- dominio anomalo (marca de mimikatz)

Service Information:
	Service Name:		krbtgt
	Service ID:		$domain\krbtgt

Network Information:
	Client Address:		::ffff:10.0.42.55

Additional Information:
	Ticket Options:		0x40810010
	Ticket Encryption Type:	0x17          <-- RC4 (un TGT legitimo moderno seria AES 0x12)
	Failure Code:		0x0
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4769 -EntryType Information -Category 0 -Message $msg1
Start-Sleep -Milliseconds 400

# Uso del ticket para acceder a un recurso -> 4624 con la identidad forjada
$msg2 = @"
An account was successfully logged on.

Subject:
	Security ID:		NULL SID

Logon Information:
	Logon Type:		3

New Logon:
	Account Name:		$forged
	Account Domain:		$domain
	Logon GUID:		{00000000-0000-0000-0000-000000000000}

Detailed Authentication Information:
	Authentication Package:	Kerberos
	Ticket lifetime:	10 years   <-- vida util absurda (default de mimikatz)
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4624 -EntryType Information -Category 0 -Message $msg2
Start-Sleep -Milliseconds 400

# El "loot" con la flag
$loot = @"
Kerberos ticket forgery (Golden Ticket) confirmed.

Forged principal: $domain\$forged (impersonated Domain Admin)
Signed with: krbtgt NTLM hash
Analyst token: $Flag
Tooling: mimikatz kerberos::golden
"@
Write-EventLog -LogName $Log -Source $Src -EventId 4104 -EntryType Warning -Category 0 -Message $loot
Start-Sleep -Seconds 2

Write-Host "[*] 3/3 Exportando el .evtx..."
wevtutil epl $Log "$OutDir\Range-Security.evtx" /ow:true
Get-ChildItem $OutDir | Format-Table Name, Length
