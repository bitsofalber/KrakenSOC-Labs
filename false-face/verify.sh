#!/usr/bin/env bash
# verify.sh — Readiness gate: every container running & healthy. SFRS §5.
set -uo pipefail
cd "$(dirname "$0")"
[ -f .env ] && set -a && . ./.env && set +a
LAB_ID="${LAB_ID:-krakensoc-lab}"
DC="docker compose -p ${LAB_ID}"

grn=$'\033[1;32m'; red=$'\033[1;31m'; ylw=$'\033[1;33m'; rst=$'\033[0m'
TIMEOUT="${VERIFY_TIMEOUT:-120}"; elapsed=0; interval=4

services=$($DC config --services 2>/dev/null)
[ -z "$services" ] && { echo "${red}No hay servicios definidos en docker-compose.yml${rst}"; exit 1; }

while :; do
  bad=0; report=""
  for svc in $services; do
    cid=$($DC ps -q "$svc" 2>/dev/null | head -1)
    if [ -z "$cid" ]; then report+="  ${red}[DOWN]${rst}    $svc\n"; bad=1; continue; fi
    state=$(docker inspect -f '{{.State.Status}}' "$cid" 2>/dev/null)
    health=$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}none{{end}}' "$cid" 2>/dev/null)
    if [ "$state" != "running" ]; then report+="  ${red}[$state]${rst} $svc\n"; bad=1
    elif [ "$health" = "unhealthy" ]; then report+="  ${red}[unhealthy]${rst} $svc\n"; bad=1
    elif [ "$health" = "starting" ]; then report+="  ${ylw}[starting]${rst} $svc\n"; bad=1
    else report+="  ${grn}[ready]${rst}   $svc ($health)\n"; fi
  done
  if [ "$bad" -eq 0 ]; then printf "$report"; printf "${grn}verify: todos los contenedores sanos.${rst}\n"; exit 0; fi
  [ "$elapsed" -ge "$TIMEOUT" ] && { printf "$report"; printf "${red}verify: timeout tras ${TIMEOUT}s.${rst}\n"; exit 1; }
  sleep "$interval"; elapsed=$((elapsed+interval))
done
