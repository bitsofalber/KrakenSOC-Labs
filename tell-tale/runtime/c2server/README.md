# c2server — Tell Tale

C2 sobre TLS. La flag va en el **Subject del certificado** (campo O), que viaja
en claro en el handshake. En el repo el cert lleva un **DECOY**; el CI regenera el
cert con la flag real desde el secret `TELL_TALE_TOKEN` (openssl con -subj).
