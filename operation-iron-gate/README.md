# Operation Iron Gate

> Un servicio expuesto en el perímetro de Northwind es explotado; el alumno detecta el acceso inicial y la webshell resultante.

**Dominio:** Perimeter / Exploitation of Public-Facing App
**MITRE ATT&CK:** T1190, T1133, T1505.003
**Estado:** 🚧 work in progress — contenido en construcción.

---

## Escenario

Un servicio expuesto en el perímetro de Northwind es explotado; el alumno detecta el acceso inicial y la webshell resultante.

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
operation-iron-gate/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
