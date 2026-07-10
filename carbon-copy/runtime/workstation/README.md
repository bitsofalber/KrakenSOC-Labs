# workstation — Carbon Copy

Envia el correo de phishing por SMTP en claro. La flag va embebida en el adjunto
y se lee de `seed/mail_token.txt`. En el repo es un **DECOY**; el token real se
inyecta solo en CI desde el secret `CARBON_COPY_TOKEN`.
