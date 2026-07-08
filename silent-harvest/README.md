# Silent Harvest

> Recolección sigilosa de credenciales y datos en varias máquinas; el alumno correlaciona la actividad de harvesting.

**Dominio:** Credential Access / Collection
**MITRE ATT&CK:** T1003, T1555, T1560
**Estado:** 🚧 work in progress — contenido en construcción.

---

## Escenario

Recolección sigilosa de credenciales y datos en varias máquinas; el alumno correlaciona la actividad de harvesting.

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
silent-harvest/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
