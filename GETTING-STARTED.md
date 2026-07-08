# Antes de empezar — Instalar Docker y lanzar tu primer lab

Guía para alumnos nuevos. Si nunca has usado Docker, empieza por aquí. Al terminar tendrás
Docker + Docker Compose v2 funcionando y sabrás lanzar cualquier KrakenSOC Runtime Lab.

---

## 1. Qué necesitas

- **Docker Engine** — el motor que ejecuta los contenedores.
- **Docker Compose v2** — el plugin que levanta el lab entero con un comando.
  > Ojo: es `docker compose` (con **espacio**), no el antiguo `docker-compose` (con **guion**, v1, obsoleto).

---

## 2. Instalar en Kali Linux (la vía rápida)

Kali es Debian por debajo. Estos paquetes traen Docker y Compose v2 ya integrados:

```bash
sudo apt update
sudo apt install -y docker.io docker-compose-v2
sudo systemctl enable --now docker
```

### Alternativa: repo oficial de Docker (versiones más nuevas)

```bash
sudo apt install -y ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/debian/gpg | sudo tee /etc/apt/keyrings/docker.asc >/dev/null
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list >/dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```
> En Kali (rolling) usa el codename `bookworm` en la línea del repo, aunque tu sistema sea rolling.

---

## 3. Usar Docker sin `sudo` (recomendado)

```bash
sudo usermod -aG docker $USER
newgrp docker      # o cierra sesión y vuelve a entrar
```

---

## 4. Comprueba que todo funciona

```bash
docker --version
docker compose version       # debe decir v2.x  (con ESPACIO)
docker run --rm hello-world  # descarga y ejecuta un contenedor de prueba
```

Si `hello-world` imprime un saludo, Docker está listo.

---

## 5. El error más típico: «`docker compose` no existe»

Casi siempre es porque tienes el antiguo `docker-compose` (v1, con guion) o te falta el plugin v2.
Solución en Kali/Debian:

```bash
sudo apt install -y docker-compose-v2
```

Y a partir de ahí usa siempre `docker compose` (con espacio).

---

## 6. Otros errores frecuentes

| Error | Causa y solución |
| :-- | :-- |
| `permission denied … /var/run/docker.sock` | Falta el paso 3 (`usermod -aG docker`) y reabrir la sesión. |
| `Cannot connect to the Docker daemon` | El servicio está parado: `sudo systemctl start docker`. |
| `docker: command not found` | No se instaló; repite el paso 2. |
| Lab lento / se queda sin memoria | Da ≥ 4 GB de RAM a tu VM de Kali. |

---

## 7. Windows y macOS

Instala **[Docker Desktop](https://www.docker.com/products/docker-desktop/)** — ya incluye Docker Engine y Compose v2.
En Mac con chip Apple (M1–M4) funciona igual: **todos los labs son multi-arquitectura** (ARM y AMD).

---

## 8. Cómo lanzar un lab (paso a paso)

```bash
# 1) Clona el repositorio de labs
git clone https://github.com/bitsofalber/KrakenSOC-Labs.git

# 2) Entra en la carpeta del lab
cd KrakenSOC-Labs/silent-harvest

# 3) Levanta el entorno (comprueba tu equipo, descarga imágenes y arranca)
./deploy.sh

# 4) Confirma que está sano
./verify.sh

# 5) Investiga con la evidencia generada (p.ej. la carpeta pcaps/),
# abre la ficha del lab en KrakenSOC y responde las preguntas para ganar XP.

# 6) Al terminar, apaga y limpia todo
./destroy.sh
```

¿Dudas con un lab concreto? Cada lab tiene su propio `README.md` con instrucciones específicas,
y dentro de **KrakenSOC → Docker BTLabs → Info** encontrarás la ficha completa, la resolución paso
a paso y dónde responder las preguntas.
