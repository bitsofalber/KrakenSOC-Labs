#!/bin/sh
sleep "${START_DELAY:-6}"
TARGET="${TARGET:-target}"
echo "[attacker] esperando al target ${TARGET}..."
i=0
until nc -z "$TARGET" 8080 2>/dev/null; do i=$((i+1)); [ "$i" -gt 40 ] && break; sleep 1; done

echo "[attacker] escaneo de puertos con Nmap..."
nmap -sS -Pn -p 22,80,443,3306,8080,9000,9090 "$TARGET" 2>/dev/null || true

# Banner grab explicito y ESPACIADO en cada puerto (handshakes completos,
# capturables de forma fiable en cualquier plataforma).
echo "[attacker] recogiendo banners de los servicios..."
for p in 22 80 3306 8080; do
  echo "[attacker]   -> puerto $p"
  echo "" | nc -w 3 "$TARGET" "$p" 2>/dev/null | head -c 200
  echo
  sleep 0.8
done
echo "[attacker] escaneo completado."
touch /tmp/session_done
tail -f /dev/null
