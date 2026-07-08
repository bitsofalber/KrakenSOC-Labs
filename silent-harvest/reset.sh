#!/usr/bin/env bash
# reset.sh — Restore the lab to its pristine state (no full re-download). SFRS §5.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] && set -a && . ./.env && set +a
LAB_ID="${LAB_ID:-krakensoc-lab}"
DC="docker compose -p ${LAB_ID}"
cyn=$'\033[1;36m'; grn=$'\033[1;32m'; rst=$'\033[0m'

printf "${cyn}>>> Reiniciando '%s' a su estado original...${rst}\n" "$LAB_ID"
# Bajar contenedores + volúmenes (borra estado), conservando imágenes ya descargadas
$DC down -v --remove-orphans
# Limpiar telemetría/logs generados
rm -rf logs/* telemetry/* 2>/dev/null || true
find logs telemetry -type d -empty -exec touch {}/.gitkeep \; 2>/dev/null || true
# Volver a levantar limpio
$DC up -d --build
./verify.sh
printf "${grn}Reset completado: entorno limpio y sano.${rst}\n"
