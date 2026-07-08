# KrakenSOC Labs

> Colección de laboratorios Blue Team empaquetados en Docker para la plataforma **SOCForge / KrakenSOC**.
> Cada carpeta es un laboratorio independiente que el alumno despliega en su propia máquina.

Todos los escenarios transcurren en la organización ficticia **Northwind Global Systems** y están
pensados para practicar detección, investigación y respuesta como analista de un SOC real
(no es un CTF ni un cuestionario: es un turno de trabajo).

## Laboratorios

| Lab | Dominio | Técnicas MITRE ATT&CK |
| :-- | :------ | :-------------------- |
| [`operation-black-quill`](./operation-black-quill) | Initial Access / Phishing | T1566.001, T1204.002, T1059 |
| [`operation-iron-gate`](./operation-iron-gate) | Perimeter / Exploitation of Public-Facing App | T1190, T1133, T1505.003 |
| [`phantom-storm`](./phantom-storm) | Command & Control / Beaconing | T1071, T1573, T1008 |
| [`apt29-midnight-blizzard`](./apt29-midnight-blizzard) | Identity / Cloud (M365) | T1078.004, T1114, T1528, T1550.001 |
| [`silent-harvest`](./silent-harvest) | Credential Access / Collection | T1003, T1555, T1560 |
| [`unauthorized-horizon`](./unauthorized-horizon) | Cloud / Unauthorized Access | T1078, T1530, T1580 |
| [`operation-root-shadow`](./operation-root-shadow) | Privilege Escalation (Linux) | T1548, T1068, T1053.003 |
| [`operation-lockbit`](./operation-lockbit) | Impact / Ransomware (defensivo) | T1486, T1490, T1489 |
| [`operation-kerberos`](./operation-kerberos) | Credential Access / Active Directory | T1558.003, T1558.001, T1550.003 |

## Cómo se usa un lab

```bash
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git
cd KrakenSOC-Labs/<nombre-del-lab>
docker compose up
```

Sigue el `README.md` de cada laboratorio para las instrucciones concretas.

---

_SOCForge // KrakenSOC — Simula la amenaza. Domina la respuesta._
