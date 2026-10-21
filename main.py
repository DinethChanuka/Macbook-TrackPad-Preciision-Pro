#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════╗
║               TrackPad Precision Pro — macOS Edition  v3.2           ║
║   macOS 10.14 Mojave → 26.x+  ·  Built-in Multitouch & Precision Mice║
║   Architecture: Modular CustomTkinter + MultitouchSupport + ML Shield║
╚══════════════════════════════════════════════════════════════════════╝
"""

import os, sys, platform, subprocess

# ─── macOS Version Compatibility & Pre-exec Setup ─────────────────────────────
if platform.system() != "Darwin":
    print("TrackPad Precision Pro is designed specifically for macOS.")
    sys.exit(1)

def _get_macos_version() -> str:
    try:
        ver = platform.mac_ver()[0]
        if ver: return ver
    except Exception:
        pass
    try:
        r = subprocess.run(["sw_vers", "-productVersion"], capture_output=True, text=True, timeout=2)
        v = r.stdout.strip()
        if v: return v
    except Exception:
        pass
    return "15.0"

_MACOS_VER_STR = _get_macos_version()

# Patch platform.mac_ver so darkdetect and CustomTkinter don't fail on macOS 26+
_orig_mac_ver = platform.mac_ver
def _safe_mac_ver():
    res = _orig_mac_ver()
    if not res[0]:
        return (_MACOS_VER_STR, res[1], res[2])
    return res
platform.mac_ver = _safe_mac_ver

# Ensure Homebrew expat & tcl-tk libraries are in DYLD_LIBRARY_PATH
_SVC_KEY = "SYSTEM_VERSION_COMPAT"
_DYLD_PATCHED = os.environ.get("TP_DYLD_PATCHED") == "1"
if not _DYLD_PATCHED and __name__ == "__main__":
    _env = os.environ.copy()
    _env[_SVC_KEY] = "1"
    _env["TP_DYLD_PATCHED"] = "1"
    extra_paths = [
        "/opt/homebrew/opt/expat/lib",
        "/usr/local/opt/expat/lib",
        "/opt/homebrew/opt/tcl-tk/lib",
        "/usr/local/opt/tcl-tk/lib",
    ]
    existing = _env.get("DYLD_LIBRARY_PATH", "")
    valid = [p for p in extra_paths if os.path.isdir(p)]
    if valid:
        _env["DYLD_LIBRARY_PATH"] = ":".join(valid) + (":" + existing if existing else "")
    try:
        os.execve(sys.executable, [sys.executable] + sys.argv, _env)
    except Exception:
        pass

from src.ui.app import TrackpadApp

if __name__ == "__main__":
    app = TrackpadApp(mac_version=_MACOS_VER_STR)
    app.mainloop()