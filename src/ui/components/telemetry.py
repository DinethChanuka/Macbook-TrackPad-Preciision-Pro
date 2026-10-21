"""
Live System Telemetry Dashboard & Diagnostics Console.
Displays real-time hardware metrics and touch event activity stream.
"""

import customtkinter as ctk
from src.config import COLORS
from src.ui.theme import get_font

class TelemetryDashboard(ctk.CTkFrame):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, fg_color=COLORS["card"], corner_radius=10, **kwargs)

        # Header title
        header = ctk.CTkLabel(
            self, text="LIVE SYSTEM TELEMETRY & DIAGNOSTICS",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        )
        header.pack(anchor="w", padx=14, pady=(10, 8))

        # Metrics 6-tile grid
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=10, pady=(0, 10))

        self.labels = {}
        metrics = [
            ("Smooth Moves",    "moves",     COLORS["accent_light"]),
            ("Jumps Blocked",   "jumps",     COLORS["warning_light"]),
            ("Jitter Filtered", "jitter",    COLORS["success_light"]),
            ("ML Taps Blocked", "ml_filt",   COLORS["danger_light"]),
            ("Zones Blocked",   "zone_blk",  COLORS["info_light"]),
            ("Session Uptime",  "uptime",    COLORS["purple"]),
        ]

        for i, (title, key, col) in enumerate(metrics):
            tile = ctk.CTkFrame(grid, fg_color=COLORS["card_hover"], corner_radius=8, height=65)
            tile.grid(row=0, column=i, padx=4, sticky="nsew")
            grid.columnconfigure(i, weight=1)

            val_lbl = ctk.CTkLabel(
                tile, text="—", font=get_font(16, "bold", mono=True), text_color=col
            )
            val_lbl.pack(pady=(8, 0))
            self.labels[key] = val_lbl

            ctk.CTkLabel(
                tile, text=title, font=get_font(9), text_color=COLORS["text_muted"]
            ).pack(pady=(0, 6))

        # Live Event Console Ticker
        console_frame = ctk.CTkFrame(self, fg_color=COLORS["card_hover"], corner_radius=6)
        console_frame.pack(fill="x", padx=10, pady=(0, 10))

        ctk.CTkLabel(
            console_frame, text="EVENT STREAM:",
            font=get_font(8, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(10, 6), pady=6)

        self.event_msg = ctk.CTkLabel(
            console_frame, text="Multitouch engine ready. Waiting for user activation.",
            font=get_font(9, mono=True), text_color=COLORS["text_secondary"]
        )
        self.event_msg.pack(side="left", padx=4, pady=6)

    def update_metrics(self, data: dict):
        for k, v in data.items():
            if k in self.labels:
                self.labels[k].configure(text=str(v))

    def log_event(self, msg: str):
        self.event_msg.configure(text=msg)
