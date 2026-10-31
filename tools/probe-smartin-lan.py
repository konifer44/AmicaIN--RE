#!/usr/bin/env python3
# Prepared by Jan Konieczny.
"""
SMART2 / SmartIN - initial LAN communication attempt (without the official app).

Evidence: q3/a.java (UDP #SMT_AMC#), o3/h.java (obfuscation seed 123), q3/c.java (ServerSocket).

Usage: see LAN-RUNTIME-INVESTIGATION.md in the project root.
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
    ap.add_argument("--oven-ip", help="Known oven IP (optional; otherwise broadcast only)")
    ap.add_argument("--local-ip", help="Computer IPv4 address on the same network as the oven")
    ap.add_argument("--session-id", default="", help="Session ID as k3.a.t(), from a paired AmicaIN session or backup")
    ap.add_argument("--listen-port", type=int, default=7776, help="TCP port on which to listen (as used by the app)")
    ap.add_argument("--udp-port", type=int, default=7777)
    ap.add_argument("--scan-only", action="store_true", help="Only scan ports at --oven-ip")
    ap.add_argument("--wait", type=float, default=25.0, help="Seconds to listen for TCP after UDP")
    ap.add_argument("--repeat", type=int, default=3, help="Number of UDP transmissions")
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
            "WARNING: --session-id is missing. The app requires k3.a.t() for UDP #SMT_AMC# (after FORMALNE/LOGUJ or pairing).\n"
            "  → Ask the owner to connect once with AmicaIN (WI mode) or obtain an ID backup from the phone.\n"
            "  → Agent: inspect jadx k3/a.java field G, q3/e.java, or a capture from the working app.\n",
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
            "\nNo TCP connection from the oven. Common causes:\n"
            "  • oven not in WI mode / not paired with this session ID\n"
            "  • AP=0 / M=0 / S=0 in the oven Wi-Fi menu\n"
            "  • VLAN / Wi-Fi client isolation\n"
            "  • this is Amica Home (Tuya), not SMART2 - a different app\n"
            "  • firewall blocks inbound TCP on --listen-port\n"
            "Agent: see LAN-RUNTIME-INVESTIGATION.md, troubleshooting loop.",
            file=sys.stderr,
        )
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
