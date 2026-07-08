#!/usr/bin/env bash
# doctor.sh — Pre-flight checks. Never mutates anything. Exit 0 = ready.
# SFRS §5. Standard across every KrakenSOC Runtime Lab.
set -uo pipefail
cd "$(dirname "$0")"
[ -f .env ] && set -a && . ./.env && set +a
[ -f .env.example ] && [ ! -f .env ] && set -a && . ./.env.example && set +a

LAB_ID="${LAB_ID:-krakensoc-lab}"
MIN_RAM_MB="${MIN_RAM_MB:-2048}"
MIN_DISK_MB="${MIN_DISK_MB:-4096}"
REQUIRED_PORTS="${REQUIRED_PORTS:-}"

red=$'\033[1;31m'; grn=$'\033[1;32m'; ylw=$'\033[1;33m'; cyn=$'\033[1;36m'; rst=$'\033[0m'
fail=0
ok()   { printf "  ${grn}[OK]${rst}   %s\n" "$1"; }
warn() { printf "  ${ylw}[WARN]${rst} %s\n" "$1"; }
bad()  { printf "  ${red}[FAIL]${rst} %s\n" "$1"; fail=1; }

printf "${cyn}== doctor: %s ==${rst}\n" "$LAB_ID"

# Docker installed & running
if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then ok "Docker en marcha ($(docker --version | awk '{print $3}' | tr -d ,))"
  else bad "Docker está instalado pero el daemon no responde. Arranca Docker Desktop / el servicio."; fi
else bad "Docker no está instalado. https://docs.docker.com/get-docker/"; fi

# Docker Compose v2
if docker compose version >/dev/null 2>&1; then ok "Docker Compose v2 ($(docker compose version --short 2>/dev/null))"
else bad "Falta Docker Compose v2 (plugin 'docker compose')."; fi

# Arquitectura (AMD/ARM) — SFRS §7
case "$(uname -m)" in
  x86_64|amd64)        ok "Arquitectura: amd64 (Intel/AMD) — Splunk corre nativo";;
  aarch64|arm64)       ok "Arquitectura: arm64 (Apple Silicon/ARM)"
                       warn "La imagen de Splunk es solo amd64: aquí corre EMULADA (Docker Desktop/QEMU)."
                       warn "Funciona, pero arranca más lento (varios minutos) y usa más RAM. Dale >=6GB a Docker.";;
  *) bad "Arquitectura no soportada: $(uname -m). Solo amd64 y arm64.";;
esac

# Sistema operativo
ok "SO: $(uname -s) $(uname -r)"

# RAM disponible
ram_mb=""
if command -v free >/dev/null 2>&1; then ram_mb=$(free -m | awk '/^Mem:/{print $2}')
elif [ "$(uname -s)" = "Darwin" ]; then ram_mb=$(( $(sysctl -n hw.memsize) / 1048576 )); fi
if [ -n "$ram_mb" ]; then
  [ "$ram_mb" -ge "$MIN_RAM_MB" ] && ok "RAM: ${ram_mb}MB (min ${MIN_RAM_MB}MB)" \
    || warn "RAM: ${ram_mb}MB por debajo del mínimo recomendado (${MIN_RAM_MB}MB)"
else warn "No pude determinar la RAM."; fi

# Disco disponible
disk_mb=$(df -Pm . | awk 'NR==2{print $4}')
if [ -n "$disk_mb" ]; then
  [ "$disk_mb" -ge "$MIN_DISK_MB" ] && ok "Disco libre: ${disk_mb}MB (min ${MIN_DISK_MB}MB)" \
    || warn "Disco libre: ${disk_mb}MB por debajo del mínimo (${MIN_DISK_MB}MB)"
fi

# Puertos requeridos libres
for p in $REQUIRED_PORTS; do
  if command -v lsof >/dev/null 2>&1 && lsof -iTCP:"$p" -sTCP:LISTEN >/dev/null 2>&1; then
    bad "Puerto $p ocupado. Libéralo o cambia el mapeo en .env"
  else ok "Puerto $p libre"; fi
done

# Permisos para escribir en el directorio del lab
[ -w . ] && ok "Permisos de escritura en $(pwd)" || bad "Sin permisos de escritura en $(pwd)"

echo
if [ "$fail" -eq 0 ]; then printf "${grn}doctor: entorno listo.${rst}\n"; exit 0
else printf "${red}doctor: corrige los [FAIL] antes de desplegar.${rst}\n"; exit 1; fi
