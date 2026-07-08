# APT29 — Midnight Blizzard

> Emulación defensiva de TTPs de APT29: abuso de identidad, robo de tokens y acceso a correo en la nube corporativa.

**Dominio:** Identity / Cloud (M365)
**MITRE ATT&CK:** T1078.004, T1114, T1528, T1550.001
**Estado:** 🚧 work in progress — contenido en construcción.

---

## Escenario

Emulación defensiva de TTPs de APT29: abuso de identidad, robo de tokens y acceso a correo en la nube corporativa.

Contexto: **Northwind Global Systems**. El alumno opera como analista L1/L2 del SOC
y debe investigar el incidente a partir de la telemetría proporcionada.

## Objetivos de aprendizaje

- Identificar los indicadores de compromiso (IoCs) del incidente.
- Reconstruir la línea temporal del ataque.
- Mapear la actividad observada al framework MITRE ATT&CK.
- Redactar las conclusiones como lo haría un analista de SOC.

## Despliegue (próximamente)

```bash
docker compose up
```

## Estructura prevista

```
apt29-midnight-blizzard/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
