# Unauthorized Horizon

> Accesos no autorizados a recursos cloud de Northwind; el alumno investiga el alcance y la exfiltración de datos.

**Dominio:** Cloud / Unauthorized Access
**MITRE ATT&CK:** T1078, T1530, T1580
**Estado:**  work in progress — contenido en construcción.

---

## Escenario

Accesos no autorizados a recursos cloud de Northwind; el alumno investiga el alcance y la exfiltración de datos.

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
unauthorized-horizon/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
