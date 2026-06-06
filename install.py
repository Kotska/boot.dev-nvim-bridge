#!/usr/bin/env python3
import base64
import hashlib
import json
import os
import platform
import re
import subprocess
import sys

sys.dont_write_bytecode = True

HOST_NAME = "nvim_bridge"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HOST_PATH = os.path.join(SCRIPT_DIR, "nvim-bridge.cmd" if platform.system() == "Windows" else "nvim-bridge.py")
MANIFEST_PATH = os.path.join(SCRIPT_DIR, "manifest.json")
KEY_FILE = os.path.join(SCRIPT_DIR, "private_key.pem")
ID_ALPHABET = "abcdefghijklmnop"


def get_host_dirs():
    system = platform.system()
    dirs = []

    if system == "Windows":
        local_app_data = os.environ.get("LOCALAPPDATA", "")
        if local_app_data:
            dirs.append(os.path.join(local_app_data, "Google", "Chrome",
                                     "User Data", "NativeMessagingHosts"))
        program_data = os.environ.get("ProgramData", "")
        if program_data:
            dirs.append(os.path.join(program_data, "Google", "Chrome",
                                     "NativeMessagingHosts"))
    elif system == "Darwin":
        home = os.path.expanduser("~")
        dirs.append(os.path.join(home, "Library", "Application Support",
                                 "Google", "Chrome", "NativeMessagingHosts"))
        dirs.append(os.path.join(home, "Library", "Application Support",
                                 "Chromium", "NativeMessagingHosts"))
    else:
        config_home = os.environ.get("XDG_CONFIG_HOME",
                                     os.path.expanduser("~/.config"))
        dirs.append(os.path.join(config_home, "google-chrome",
                                 "NativeMessagingHosts"))
        dirs.append(os.path.join(config_home, "chromium",
                                 "NativeMessagingHosts"))
        dirs.append(os.path.join(os.path.expanduser("~"), ".config",
                                 "BraveSoftware", "Brave-Browser",
                                 "NativeMessagingHosts"))

    return [d for d in dirs if d]


def ensure_key():
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE) as f:
            return f.read()

    try:
        subprocess.run(["openssl", "version"], capture_output=True, check=True)
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("Error: openssl is required to generate the extension key")
        print("Install openssl and try again.")
        sys.exit(1)

    subprocess.run([
        "openssl", "genpkey", "-algorithm", "RSA",
        "-out", KEY_FILE,
        "-pkeyopt", "rsa_keygen_bits:2048",
    ], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    with open(KEY_FILE) as f:
        return f.read()


def get_pub_key_b64():
    result = subprocess.run([
        "openssl", "pkey", "-in", KEY_FILE,
        "-pubout", "-outform", "DER",
    ], capture_output=True, check=True, text=False)

    return base64.b64encode(result.stdout).decode("ascii")


def compute_extension_id(pub_key_der_b64):
    der = base64.b64decode(pub_key_der_b64)
    h = hashlib.sha256(der).digest()[:16]
    chars = []
    for b in h:
        chars.append(ID_ALPHABET[(b >> 4) & 0xF])
        chars.append(ID_ALPHABET[b & 0xF])
    return "".join(chars)


def update_manifest(pub_key_b64):
    with open(MANIFEST_PATH) as f:
        manifest = json.load(f)

    manifest["key"] = pub_key_b64

    with open(MANIFEST_PATH, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def _install_registry(manifest_path):
    if platform.system() != "Windows":
        return
    import winreg
    key_path = r"SOFTWARE\Google\Chrome\NativeMessagingHosts\nvim_bridge"
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path)
        winreg.SetValueEx(key, None, 0, winreg.REG_SZ, manifest_path)
        winreg.CloseKey(key)
        print(f"Registry: HKCU\\{key_path} -> {manifest_path}")
    except PermissionError:
        print("Warning: Could not write to registry (permission denied)")


def install():
    ensure_key()
    pub_key_b64 = get_pub_key_b64()
    ext_id = compute_extension_id(pub_key_b64)
    update_manifest(pub_key_b64)

    host_dirs = get_host_dirs()
    if not host_dirs:
        print(f"Error: unsupported OS: {platform.system()}")
        sys.exit(1)

    manifest_host = {
        "name": HOST_NAME,
        "description": "Bridge from boot.dev to Neovim",
        "path": HOST_PATH,
        "type": "stdio",
        "allowed_origins": [f"chrome-extension://{ext_id}/"],
    }

    for d in host_dirs:
        os.makedirs(d, exist_ok=True)
        dest = os.path.join(d, f"{HOST_NAME}.json")
        with open(dest, "w") as f:
            json.dump(manifest_host, f, indent=2)
        print(f"Installed: {dest}")

    if platform.system() == "Windows":
        manifest_file = os.path.join(SCRIPT_DIR, f"{HOST_NAME}.json")
        with open(manifest_file, "w") as f:
            json.dump(manifest_host, f, indent=2)
        _install_registry(manifest_file)

    print(f"\nExtension ID: {ext_id}")
    print("Now load the extension in chrome://extensions (reload if already loaded).")


if __name__ == "__main__":
    install()
