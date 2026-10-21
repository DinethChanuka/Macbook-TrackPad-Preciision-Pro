"""
Global Configuration, Styling Constants, and Presets for TrackPad Precision Pro.
"""

from typing import Dict, Any

# ─── Color Palette ────────────────────────────────────────────────────────────
COLORS = {
    "bg":           "#0a0d14",  # Obsidian Dark base
    "surface":      "#101522",  # Top header and tab headers
    "card":         "#151a28",  # Elevated panel containers
    "card_hover":   "#1b2234",  # Card hover / interactive elements
    "border":       "#1f273d",  # Subtle dividing line
    "border_focus": "#374466",  # Highlighted border

    # Vibrant UI Action Colors (Guaranteed to render vividly in CustomTkinter)
    "accent":       "#6366f1",  # Electric Indigo (Primary Action)
    "accent_hover": "#4f46e5",
    "accent_light": "#818cf8",

    "success":      "#10b981",  # Emerald Green (Activate / Online)
    "success_hover":"#059669",
    "success_light":"#34d399",

    "danger":       "#ef4444",  # Crimson Red (Stop / Blocked)
    "danger_hover": "#dc2626",
    "danger_light": "#f87171",

    "info":         "#0ea5e9",  # Sky Blue (Reset / Presets)
    "info_hover":   "#0284c7",
    "info_light":   "#38bdf8",

    "warning":      "#f59e0b",  # Amber (ML Alert / Suspicious)
    "warning_hover":"#d97706",
    "warning_light":"#fbbf24",

    "purple":       "#a855f7",  # Violet accent
    "purple_hover": "#9333ea",

    # Typography
    "text_primary":   "#f8fafc",
    "text_secondary": "#cbd5e1",
    "text_muted":     "#64748b",
    "white":          "#ffffff",
}

# ─── System Preferences ───────────────────────────────────────────────────────
PREF_DOMAIN_TOUCH = "com.apple.AppleMultitouchTrackpad"
PREF_DOMAIN_GLOBAL = ".GlobalPreferences"

# ─── Profile Presets ──────────────────────────────────────────────────────────
PROFILE_PRESETS: Dict[str, Dict[str, Any]] = {
    "everyday": {
        "title": "⚡ Everyday Balanced",
        "description": "Natural acceleration and gentle smoothing for everyday navigation.",
        "smoothing": 0.30,
        "max_jump": 100.0,
        "deadzone": 1.2,
        "accel_mode": "ballistic",
        "sensitivity": 1.0,
        "tap_debounce": 40.0,
        "max_contact_size": 0.70,
    },
    "cad": {
        "title": "🎯 Precision CAD & Art",
        "description": "Dampened micro-movement for sub-pixel accuracy in Figma, Blender, and CAD.",
        "smoothing": 0.16,
        "max_jump": 55.0,
        "deadzone": 2.4,
        "accel_mode": "cad",
        "sensitivity": 0.55,
        "tap_debounce": 60.0,
        "max_contact_size": 0.65,
    },
    "shield": {
        "title": "🛡 Anti-Jitter Palm Shield",
        "description": "Strict rejection of resting palms, micro-tremors, and edge taps.",
        "smoothing": 0.35,
        "max_jump": 85.0,
        "deadzone": 3.0,
        "accel_mode": "ballistic",
        "sensitivity": 1.0,
        "tap_debounce": 80.0,
        "max_contact_size": 0.55,
        "ml_filter": True,
        "zone_preset": "corners",
    },
    "gaming": {
        "title": "🏎 Hyper Speed & FPS",
        "description": "Linear 1:1 direct tracking with zero acceleration delay.",
        "smoothing": 0.50,
        "max_jump": 260.0,
        "deadzone": 0.8,
        "accel_mode": "linear",
        "sensitivity": 1.8,
        "tap_debounce": 20.0,
        "max_contact_size": 0.85,
    },
}
