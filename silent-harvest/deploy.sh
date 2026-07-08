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
  printf "${grn}Entorno '%s' desplegado y sano.${rst}\n" "$LAB_ID"
  # Mostrar URLs/puertos expuestos
  urls=$($DC ps --format '{{.Names}} {{.Ports}}' 2>/dev/null | grep -Eo '0\.0\.0\.0:[0-9]+|127\.0\.0\.1:[0-9]+' | sort -u || true)
  if [ -n "$urls" ]; then echo "Accesos:"; echo "$urls" | sed 's/^/  http:\/\//'; fi
  echo
  printf "${ylw}Siguiente paso: vuelve a KrakenSOC para investigar y responder las preguntas.${rst}\n"
  echo "  Reset:   ./reset.sh    Apagar y limpiar:  ./destroy.sh"
else
  echo "El despliegue terminó pero verify.sh detectó contenedores no sanos. Revisa: $DC ps"
  exit 1
fi
