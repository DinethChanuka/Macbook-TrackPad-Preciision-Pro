"""
macOS System Preferences Manager for Apple Multitouch Trackpad.
Provides safe mutation and guaranteed teardown restoration.
"""

import subprocess, atexit
from typing import Optional, Dict
from src.config import PREF_DOMAIN_TOUCH, PREF_DOMAIN_GLOBAL

_MANAGED_KEYS = {
    "TrackpadHandResting": "1",
    "TrackpadMomentumScroll": "1",
    "Clicking": "1",
    "FirstClickThreshold": "1",
}

_backup: Dict[str, Optional[str]] = {}

def read_pref(domain: str, key: str) -> Optional[str]:
    try:
        r = subprocess.run(["defaults", "read", domain, key], capture_output=True, text=True, timeout=2)
        return r.stdout.strip() if r.returncode == 0 else None
    except Exception:
        return None

def write_pref(domain: str, key: str, value: str):
    try:
        subprocess.run(["defaults", "write", domain, key, value], capture_output=True, timeout=2)
    except Exception:
        pass

def write_bool_pref(domain: str, key: str, value: bool):
    try:
        val = "true" if value else "false"
        subprocess.run(["defaults", "write", domain, key, "-bool", val], capture_output=True, timeout=2)
    except Exception:
        pass

def delete_pref(domain: str, key: str):
    try:
        subprocess.run(["defaults", "delete", domain, key], capture_output=True, timeout=2)
    except Exception:
        pass

def backup_system_preferences():
    global _backup
    _backup.clear()
    for key in _MANAGED_KEYS:
        _backup[key] = read_pref(PREF_DOMAIN_TOUCH, key)

def restore_system_preferences():
    global _backup
    for key, val in _backup.items():
        if val is not None:
            write_pref(PREF_DOMAIN_TOUCH, key, val)
        else:
            delete_pref(PREF_DOMAIN_TOUCH, key)

# Guarantee preferences restoration upon process termination
atexit.register(restore_system_preferences)
