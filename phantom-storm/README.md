# Phantom Storm

> Un endpoint comprometido late hacia un C2 escondido entre el tráfico normal; el alumno aísla el patrón de beaconing.

**Dominio:** Command & Control / Beaconing
**MITRE ATT&CK:** T1071, T1573, T1008
**Estado:** 🚧 work in progress — contenido en construcción.

---

## Escenario

Un endpoint comprometido late hacia un C2 escondido entre el tráfico normal; el alumno aísla el patrón de beaconing.

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
phantom-storm/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
