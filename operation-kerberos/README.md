# Operation Kerberos

> Ataques a Kerberos (Kerberoasting, Golden Ticket) en el AD de Northwind; el alumno los caza en la telemetría.

**Dominio:** Credential Access / Active Directory
**MITRE ATT&CK:** T1558.003, T1558.001, T1550.003
**Estado:**  work in progress — contenido en construcción.

---

## Escenario

Ataques a Kerberos (Kerberoasting, Golden Ticket) en el AD de Northwind; el alumno los caza en la telemetría.

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
operation-kerberos/
├── docker-compose.yml     # orquestación del laboratorio
├── README.md              # esta guía
├── data/                  # telemetría / artefactos del escenario
└── solution/              # clave de corrección (spoilers)
```
