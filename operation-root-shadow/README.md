# Operation Root Shadow

> Escalada a root en un host Linux; el alumno identifica el vector de escalada y la persistencia posterior.

**Dominio:** Privilege Escalation (Linux)
**MITRE ATT&CK:** T1548, T1068, T1053.003
**Estado:** 🚧 work in progress — contenido en construcción.

---

## Escenario

Escalada a root en un host Linux; el alumno identifica el vector de escalada y la persistencia posterior.

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
operation-root-shadow/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
