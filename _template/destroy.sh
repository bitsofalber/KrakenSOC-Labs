#!/usr/bin/env bash
# destroy.sh — Full teardown: containers, network, volumes, temp files. SFRS §5.
set -euo pipefail
cd "$(dirname "$0")"
[ -f .env ] && set -a && . ./.env && set +a
LAB_ID="${LAB_ID:-krakensoc-lab}"
DC="docker compose -p ${LAB_ID}"
cyn=$'\033[1;36m'; grn=$'\033[1;32m'; rst=$'\033[0m'

printf "${cyn}>>> Destruyendo '%s' (contenedores, red, volúmenes)...${rst}\n" "$LAB_ID"
$DC down -v --remove-orphans

# Limpiar ficheros temporales generados por el lab (evidencia reconstruida, logs, telemetría)
rm -rf logs/* telemetry/* 2>/dev/null || true
find . -name 'RECOVERED_*' -delete 2>/dev/null || true
for d in logs telemetry; do [ -d "$d" ] && touch "$d/.gitkeep"; done

printf "${grn}Lab '%s' eliminado por completo. .env se conserva (bórralo a mano si quieres).${rst}\n" "$LAB_ID"
