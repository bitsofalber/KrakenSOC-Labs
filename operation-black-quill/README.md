# Operation Black Quill

> Un documento ofimático malicioso llega a un empleado de Northwind; el alumno reconstruye la cadena desde el adjunto hasta la ejecución.

**Dominio:** Initial Access / Phishing
**MITRE ATT&CK:** T1566.001, T1204.002, T1059
**Estado:** 🚧 work in progress — contenido en construcción.

---

## Escenario

Un documento ofimático malicioso llega a un empleado de Northwind; el alumno reconstruye la cadena desde el adjunto hasta la ejecución.

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
operation-black-quill/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
