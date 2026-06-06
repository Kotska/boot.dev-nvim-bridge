#!/usr/bin/env python3
import json
import struct
import sys
import os
import subprocess
from pynvim import attach
from pynvim.api.common import NvimError

if os.name == 'nt':
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

def send_to_nvim(data):
    if "posix" in os.name:
        run_path = "/run/user/1000/"
    else:
        run_path = "//./pipe/"

    sockets = []
    for filename in os.listdir(run_path):
        if "nvim" in filename:
            sockets.append(os.path.join(run_path, filename))

    success = False
    for target_buffer, text in data.items():
        for socket in sockets:
            nvim = attach('socket', path=socket)

            for buf in nvim.buffers:
                try:
                    if target_buffer in buf.name:
                        nvim.current.buffer = buf
                        buf[:] = text.split('\n')
                        nvim.command('write')
                        success = True
                        break
                except NvimError:
                    continue

    return {"success": success}

def read_message():
    raw = sys.stdin.buffer.read(4)
    if not raw:
        return None
    length = struct.unpack('=I', raw)[0]
    return json.loads(sys.stdin.buffer.read(length))

def write_message(data):
    payload = json.dumps(data).encode('utf-8')
    sys.stdout.buffer.write(struct.pack('=I', len(payload)))
    sys.stdout.buffer.write(payload)
    sys.stdout.buffer.flush()

def main():
    data = read_message()
    if data is None:
        return
    result = send_to_nvim(data)
    write_message(result)

if __name__ == "__main__":
    main()
