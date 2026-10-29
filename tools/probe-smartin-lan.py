#!/usr/bin/env python3
# Przygotowane przez Jan Koneiczny.
"""
SMART2 / SmartIN — pierwsza próba komunikacji LAN (bez oficjalnej apki).

Evidence: q3/a.java (UDP #SMT_AMC#), o3/h.java (obfuskacja seed 123), q3/c.java (ServerSocket).

Użycie — patrz PROBE-LAN-RUNTIME.md (katalog główny projektu Amica).
"""
from __future__ import annotations

import argparse
import ipaddress
import socket
import struct
import sys
import threading
import time
from typing import Optional


def o3_h_byte_a(b: int, d: int, i: int) -> int:
    mod = d % 10
    b = b & 0xFF
    if mod == 0:
        v = b - i * 11
    elif mod == 1:
        v = b - i * 16
    elif mod == 2:
        v = b + i * (d % 12)
    elif mod == 3:
        v = b + i * (d % 45)
    elif mod == 4:
        v = b - i * 13
    elif mod == 5:
        v = b - i * (d % 13)
    elif mod == 6:
        v = b - i * 10
    elif mod == 7:
        v = b - i * 8
    elif mod == 8:
        v = b + i * 16
    elif mod == 9:
        v = b + i * 18
    else:
        v = 0
    return int(v) % 256


def o3_h_d(data: bytes, seed: int = 123, mode: int = 1) -> bytes:
    out = bytearray(len(data))
    j = seed
    for idx, byte in enumerate(data):
        out[idx] = o3_h_byte_a(byte, j, mode)
        j = (j + 1) % 268435456
    return bytes(out)


def pad_left(s: str, width: int) -> str:
    return f"{s:>{width}}"[:width].ljust(width)


def pad_right(s: str, width: int) -> str:
    return f"{s:<{width}}"[:width].ljust(width)


def build_smt_amc_payload(session_id: str, local_ip: str, listen_port: int, counter: int = 1) -> bytes:
    plain = (
        "#SMT_AMC#"
        + session_id
        + pad_left(local_ip, 15)
        + pad_right(str(listen_port), 6)
        + pad_right(str(counter), 6)
    )
    return o3_h_d(plain.encode("ascii", errors="replace"), 123, 1)


def pick_local_ipv4() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()


def scan_ports(host: str, ports: list[int], timeout: float = 1.0) -> dict[int, bool]:
    result: dict[int, bool] = {}
    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        try:
            result[port] = sock.connect_ex((host, port)) == 0
        finally:
            sock.close()
    return result


def listen_for_inbound(port: int, stop: threading.Event, log: list[str], timeout: float) -> None:
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind(("0.0.0.0", port))
        srv.listen(1)
        srv.settimeout(1.0)
        log.append(f"listen:0.0.0.0:{port}")
        deadline = time.time() + timeout
        while not stop.is_set() and time.time() < deadline:
            try:
                conn, addr = srv.accept()
            except socket.timeout:
                continue
            data = conn.recv(4096)
            log.append(f"inbound_tcp:{addr[0]}:{addr[1]} len={len(data)} hex={data[:64].hex()}")
            conn.close()
            break
    except OSError as e:
        log.append(f"listen_error:{e}")
    finally:
        srv.close()


def udp_broadcast(
    payload: bytes,
    udp_port: int,
    target: Optional[str],
    local_ip: str,
) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    if target:
        dest = (target, udp_port)
    else:
        net = ipaddress.IPv4Network(f"{local_ip}/24", strict=False)
        dest = (str(net.broadcast_address), udp_port)
    sock.sendto(payload, dest)
    sock.close()


def main() -> int:
    ap = argparse.ArgumentParser(description="SMART2 LAN probe (discovery + listen)")
    ap.add_argument("--oven-ip", help="Znany IP piekarnika (opcjonalnie — bez tego tylko broadcast)")
    ap.add_argument("--local-ip", help="IPv4 komputera w tej samej sieci co piekarnik")
    ap.add_argument("--session-id", default="", help="ID sesji jak k3.a.t() — po sparowaniu AmicaIN lub z backupu")
    ap.add_argument("--listen-port", type=int, default=7776, help="Port TCP na którym czekamy (jak apka)")
    ap.add_argument("--udp-port", type=int, default=7777)
    ap.add_argument("--scan-only", action="store_true", help="Tylko skan portów na --oven-ip")
    ap.add_argument("--wait", type=float, default=25.0, help="Sekundy nasłuchu TCP po UDP")
    ap.add_argument("--repeat", type=int, default=3, help="Ile razy wysłać UDP")
    args = ap.parse_args()

    local_ip = args.local_ip or pick_local_ipv4()
    log: list[str] = []
    log.append(f"local_ip={local_ip}")

    if args.oven_ip:
        open_ports = scan_ports(args.oven_ip, [7776, 7777, 7770])
        log.append(f"scan:{args.oven_ip} {open_ports}")
        for p, ok in open_ports.items():
            print(f"  TCP {p}: {'OPEN' if ok else 'closed/filtered'}")
        if args.scan_only:
            for line in log:
                print(line)
            return 0

    if not args.session_id:
        print(
            "UWAGA: brak --session-id. UDP #SMT_AMC# w apce wymaga k3.a.t() (po FORMALNE/LOGUJ lub sparowaniu).\n"
            "  → Poproś właściciela o jednorazowe połączenie AmicaIN (tryb WI) albo backup id z telefonu.\n"
            "  → Agent: szukaj w jadx k3/a.java pole G, q3/e.java, albo capture z działającej apki.\n",
            file=sys.stderr,
        )
        session = "PROBE0000000001"
    else:
        session = args.session_id

    stop = threading.Event()
    t = threading.Thread(
        target=listen_for_inbound,
        args=(args.listen_port, stop, log, args.wait),
        daemon=True,
    )
    t.start()
    time.sleep(0.3)

    for n in range(1, args.repeat + 1):
        payload = build_smt_amc_payload(session, local_ip, args.listen_port, n)
        target = args.oven_ip if args.oven_ip else None
        try:
            udp_broadcast(payload, args.udp_port, target, local_ip)
            log.append(
                f"udp_sent:{target or 'broadcast'}:{args.udp_port} counter={n} plain_prefix=#SMT_AMC#..."
            )
        except OSError as e:
            log.append(f"udp_error:{e}")
        time.sleep(2.0)

    t.join(timeout=args.wait + 2)
    stop.set()

    print("--- log ---")
    for line in log:
        print(line)

    if not any("inbound_tcp" in x for x in log):
        print(
            "\nBrak połączenia TCP od piekarnika. Typowe przyczyny:\n"
            "  • piekarnik nie w trybie WI / nie sparowany z tym session-id\n"
            "  • AP=0 / M=0 / S=0 w menu WiFi piekarnika\n"
            "  • VLAN / izolacja klientów WiFi\n"
            "  • to Amica Home (Tuya), nie SMART2 — inna apka\n"
            "  • firewall blokuje inbound TCP na --listen-port\n"
            "Agent: patrz PROBE-LAN-RUNTIME.md § pętla naprawcza.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
