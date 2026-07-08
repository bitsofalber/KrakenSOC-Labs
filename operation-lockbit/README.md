# Operation LockBit

> Análisis defensivo de actividad tipo ransomware LockBit; el alumno detecta la fase previa al cifrado y los IoCs.

**Dominio:** Impact / Ransomware (defensivo)
**MITRE ATT&CK:** T1486, T1490, T1489
**Estado:**  work in progress — contenido en construcción.

---

## Escenario

Análisis defensivo de actividad tipo ransomware LockBit; el alumno detecta la fase previa al cifrado y los IoCs.

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
operation-lockbit/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
