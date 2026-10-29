#!/usr/bin/env python3
"""Discard hea_input datagrams so hea_cam can run alone (OS-T1 timing without inference)."""
import os
import socket
import sys

path = sys.argv[1] if len(sys.argv) > 1 else "/tmp/hea_src.sock"
if os.path.exists(path):
    os.unlink(path)
sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
sock.bind(path)
try:
    while True:
        sock.recv(64)
except KeyboardInterrupt:
    pass
finally:
    os.unlink(path)
