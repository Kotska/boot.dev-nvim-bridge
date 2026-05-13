# nvim-bridge-extension

Chrome extension that sends code from boot.dev coding exercises directly into Neovim buffers.

## How it works

1. Click the extension icon on a boot.dev lesson page.
2. The content script extracts code from each open editor tab.
3. The background script sends the code via Chrome Native Messaging to a Python host.
4. The Python host connects to a running Neovim instance via its Unix socket.
5. Each editor's code is written to the matching buffer in Neovim.

## Setup

### 1. Install the Chrome extension

- Open `chrome://extensions`
- Enable **Developer mode**
- Click **Load unpacked** and select this directory

### 2. Register the native messaging host

```bash
python3 install.py
```

This generates a key, computes the extension ID, updates `manifest.json`, and registers the native messaging host. Then load (or reload) the extension in `chrome://extensions`.

### 4. Install Python dependencies

```bash
pip install pynvim
```

## Usage

Open a boot.dev lesson, open the corresponding files in Neovim, and click the extension icon. The code from each editor tab on boot.dev will be written to the matching buffer in Neovim.
