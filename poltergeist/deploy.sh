#!/usr/bin/env bash
# deploy.sh — One command to bring the lab up. SFRS §5.
set -euo pipefail
cd "$(dirname "$0")"

cyn=$'\033[1;36m'; grn=$'\033[1;32m'; ylw=$'\033[1;33m'; rst=$'\033[0m'
step() { printf "${cyn}>>> %s${rst}\n" "$1"; }

step "1/5 Comprobando el entorno (doctor)..."
./doctor.sh || { echo "Aborta: el entorno no está listo."; exit 1; }

step "2/5 Preparando configuración (.env)..."
if [ ! -f .env ]; then cp .env.example .env; echo "    .env creado desde .env.example"; else echo "    .env ya existe (se respeta)"; fi
set -a; . ./.env; set +a
LAB_ID="${LAB_ID:-krakensoc-lab}"
DC="docker compose -p ${LAB_ID}"

step "3/5 Descargando imágenes (multi-arch, arquitectura correcta automática)..."
$DC pull --ignore-pull-failures 2>/dev/null || true

step "4/5 Levantando el entorno..."
$DC up -d --build

step "5/5 Esperando a que los contenedores estén sanos..."
if ./verify.sh; then
  echo
  printf "${grn}Entorno '%s' desplegado y sano. El dataset ya está indexado en Splunk.${rst}\n" "$LAB_ID"
  echo
  printf "${grn}Splunk Web:${rst}  http://localhost:%s\n" "${SPLUNK_WEB_PORT:-8000}"
  printf "${grn}Usuario:${rst}     admin\n"
  printf "${grn}Contraseña:${rst}  %s   (variable SPLUNK_PASSWORD en .env)\n" "${SPLUNK_PASSWORD:-Changeme123!}"
  echo "  Todo el dataset vive en el índice 'northwind'. Empieza con:  index=northwind"
  echo
  printf "${ylw}Siguiente paso: investiga en Splunk y responde las preguntas en KrakenSOC.${rst}\n"
  echo "  Reset:   ./reset.sh    Apagar y limpiar:  ./destroy.sh"
else
  echo "El despliegue terminó pero verify.sh detectó contenedores no sanos. Revisa: $DC ps"
  exit 1
fi
