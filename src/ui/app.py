"""
Main CustomTkinter Desktop Application Architecture.
"""

import time, subprocess, threading
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from typing import Dict, Optional

from src.config import COLORS, PROFILE_PRESETS
from src.ui.theme import init_theme, get_font
from src.core.engine import CursorEngine
from src.core.multitouch import MultitouchDeviceManager
from src.core.listener import GlobalMouseListener
from src.core.preferences import backup_system_preferences, restore_system_preferences
from src.zones.manager import ZoneManager
from src.ml.classifier import MLTouchGuardian
from assets.logo import draw_logo

from src.ui.tabs.surface_tab import SurfaceTab
from src.ui.tabs.precision_tab import PrecisionTab
from src.ui.tabs.ml_tab import MLTab
from src.ui.tabs.advanced_tab import AdvancedTab
from src.ui.components.telemetry import TelemetryDashboard

class TrackpadApp(ctk.CTk):
    def __init__(self, mac_version: str = "15.0"):
        super().__init__()
        self.mac_version = mac_version

        # Core subsystems
        self.engine = CursorEngine()
        self.zone_mgr = ZoneManager()
        self.ml_guardian = MLTouchGuardian()
        self.mt_manager = MultitouchDeviceManager()
        self.mouse_listener = GlobalMouseListener()

        # State flags
        self._running: bool = False
        self._session_start: Optional[float] = None
        self._stat_timer_id: Optional[str] = None
        self._fingers: Dict = {}
        self._last_tap_time: float = 0.0
        self._debounce_ms: float = 40.0
        self._max_contact_size: float = 0.70

        # Telemetry accumulators
        self._ml_filt_total: int = 0
        self._zone_blk_total: int = 0

        self._init_window()
        self._build_header()
        self._build_tabs()
        self._detect_hardware()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    def _init_window(self):
        init_theme()
        self.title("TrackPad Precision Pro")
        self.geometry("680x840")
        self.minsize(620, 580)
        self.configure(fg_color=COLORS["bg"])

        # Bring window into desktop view
        self.lift()
        self.attributes("-topmost", True)
        self.after(250, lambda: self.attributes("-topmost", False))

    def _build_header(self):
        # 1. Pinned Top Surface Container
        hdr_frame = ctk.CTkFrame(self, fg_color=COLORS["surface"], corner_radius=0)
        hdr_frame.pack(fill="x", side="top")

        # Neon Gradient accent top line
        accent_line = tk.Canvas(hdr_frame, height=3, bg=COLORS["surface"], highlightthickness=0)
        accent_line.pack(fill="x")
        self.after(50, lambda: self._render_gradient_bar(accent_line))

        # Main Header row
        row = ctk.CTkFrame(hdr_frame, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(10, 8))

        # Vector Logo Canvas
        logo_canvas = tk.Canvas(row, width=38, height=38, bg=COLORS["surface"], highlightthickness=0)
        logo_canvas.pack(side="left", padx=(0, 10))
        draw_logo(logo_canvas, 19, 19, size=32)

        # Title & Version Badge
        title_box = ctk.CTkFrame(row, fg_color="transparent")
        title_box.pack(side="left")

        ctk.CTkLabel(
            title_box, text="TrackPad Precision Pro",
            font=get_font(16, "bold"), text_color=COLORS["text_primary"]
        ).pack(anchor="w")

        meta_box = ctk.CTkFrame(title_box, fg_color="transparent")
        meta_box.pack(anchor="w", pady=(1, 0))

        ctk.CTkLabel(
            meta_box, text=f"macOS {self.mac_version}  ·  v3.2",
            font=get_font(9, mono=True), text_color=COLORS["text_muted"]
        ).pack(side="left")

        self.tp_badge = ctk.CTkLabel(
            meta_box, text="● Detecting hardware…",
            font=get_font(9, mono=True), text_color=COLORS["text_muted"]
        )
        self.tp_badge.pack(side="left", padx=(10, 0))

        # Action Buttons (Guaranteed vivid colors in CustomTkinter)
        btn_box = ctk.CTkFrame(row, fg_color="transparent")
        btn_box.pack(side="right")

        self.start_btn = ctk.CTkButton(
            btn_box, text="▶  Activate", width=110, height=32,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            font=get_font(11, "bold"), text_color=COLORS["white"],
            command=self._start
        )
        self.start_btn.pack(side="left", padx=3)

        self.stop_btn = ctk.CTkButton(
            btn_box, text="■  Stop", width=90, height=32,
            fg_color=COLORS["card_hover"], hover_color=COLORS["danger"],
            font=get_font(11, "bold"), text_color=COLORS["text_muted"],
            command=self._stop, state="disabled"
        )
        self.stop_btn.pack(side="left", padx=3)

        self.reset_btn = ctk.CTkButton(
            btn_box, text="⟳  Reset", width=90, height=32,
            fg_color=COLORS["card_hover"], hover_color=COLORS["info"],
            font=get_font(11, "bold"), text_color=COLORS["text_muted"],
            command=self._recalibrate, state="disabled"
        )
        self.reset_btn.pack(side="left", padx=3)

        # Status Ticker Row
        status_bar = ctk.CTkFrame(hdr_frame, fg_color=COLORS["card_hover"], corner_radius=6)
        status_bar.pack(fill="x", padx=16, pady=(0, 8))

        self.status_dot = ctk.CTkLabel(
            status_bar, text="●", font=get_font(12), text_color=COLORS["text_muted"]
        )
        self.status_dot.pack(side="left", padx=(10, 4), pady=4)

        self.status_text = ctk.CTkLabel(
            status_bar, text="System Idle  —  Ready to engage precision smoothing",
            font=get_font(10, "bold"), text_color=COLORS["text_secondary"]
        )
        self.status_text.pack(side="left", pady=4)

        # Quick Preset Profiles Bar
        prof_bar = ctk.CTkFrame(hdr_frame, fg_color="transparent")
        prof_bar.pack(fill="x", padx=16, pady=(0, 8))

        ctk.CTkLabel(
            prof_bar, text="Profiles:", font=get_font(9, "bold", mono=True),
            text_color=COLORS["text_muted"]
        ).pack(side="left", padx=(0, 6))

        for k, p in PROFILE_PRESETS.items():
            ctk.CTkButton(
                prof_bar, text=p["title"], height=24,
                fg_color=COLORS["card"], hover_color=COLORS["accent"],
                font=get_font(9, "bold"), text_color=COLORS["text_primary"],
                command=lambda key=k: self._apply_profile(key)
            ).pack(side="left", padx=2, expand=True, fill="x")

    def _render_gradient_bar(self, canvas: tk.Canvas):
        try:
            w = canvas.winfo_width() or 680
            colors = ["#6366f1", "#0ea5e9", "#10b981", "#a855f7"]
            steps = len(colors) - 1
            seg = w / steps
            for i in range(steps):
                r1, g1, b1 = int(colors[i][1:3], 16), int(colors[i][3:5], 16), int(colors[i][5:7], 16)
                r2, g2, b2 = int(colors[i+1][1:3], 16), int(colors[i+1][3:5], 16), int(colors[i+1][5:7], 16)
                for px in range(int(seg)):
                    t = px / seg
                    rv = int(r1 + (r2 - r1) * t)
                    gv = int(g1 + (g2 - g1) * t)
                    bv = int(b1 + (b2 - b1) * t)
                    x = int(i * seg + px)
                    canvas.create_line(x, 0, x, 3, fill=f"#{rv:02x}{gv:02x}{bv:02x}")
        except Exception:
            pass

    def _build_tabs(self):
        # Dedicated scrollable container or tabview
        self.tabview = ctk.CTkTabview(
            self, fg_color=COLORS["bg"], segmented_button_fg_color=COLORS["card"],
            segmented_button_selected_color=COLORS["accent"],
            segmented_button_selected_hover_color=COLORS["accent_hover"],
            segmented_button_unselected_hover_color=COLORS["card_hover"],
            text_color=COLORS["text_primary"]
        )
        self.tabview.pack(fill="both", expand=True, padx=10, pady=(0, 6))

        tab_surface   = self.tabview.add("🎛 Surface & Zones")
        tab_precision = self.tabview.add("⚡ Precision & Motion")
        tab_ml        = self.tabview.add("🧠 ML Guardian")
        tab_advanced  = self.tabview.add("🛠 System & Hardware")
        tab_telemetry = self.tabview.add("📊 Live Telemetry")

        # Instantiate tab views
        self.surface_tab = SurfaceTab(tab_surface, self.zone_mgr, self.ml_guardian)
        self.surface_tab.pack(fill="both", expand=True)

        self.precision_tab = PrecisionTab(tab_precision, self.engine)
        self.precision_tab.pack(fill="both", expand=True)

        self.ml_tab = MLTab(tab_ml, self.ml_guardian)
        self.ml_tab.pack(fill="both", expand=True)

        self.advanced_tab = AdvancedTab(tab_advanced, self.engine, self)
        self.advanced_tab.pack(fill="both", expand=True)

        self.telemetry = TelemetryDashboard(tab_telemetry)
        self.telemetry.pack(fill="both", expand=True, padx=6, pady=6)

    def _detect_hardware(self):
        found = False
        try:
            r = subprocess.run(
                ["ioreg", "-r", "-c", "AppleMultitouchTrackpad", "-d", "1"],
                capture_output=True, text=True, timeout=2
            )
            found = "AppleMultitouchTrackpad" in r.stdout
        except Exception:
            pass

        if found:
            self.tp_badge.configure(text="● Built-in Apple Multitouch Active", text_color=COLORS["success_light"])
        else:
            self.tp_badge.configure(text="● Mouse / External Pointer Active", text_color=COLORS["warning_light"])

    def _apply_profile(self, name: str):
        prof = PROFILE_PRESETS.get(name)
        if not prof: return

        self.engine.smoothing   = prof["smoothing"]
        self.engine.max_jump    = prof["max_jump"]
        self.engine.deadzone    = prof["deadzone"]
        self.engine.accel_mode  = prof["accel_mode"]
        self.engine.sensitivity = prof["sensitivity"]
        self._debounce_ms       = prof["tap_debounce"]
        self._max_contact_size  = prof["max_contact_size"]

        if "zone_preset" in prof:
            self.zone_mgr.apply_preset(prof["zone_preset"])
            self.zone_mgr.enabled = True
            self.surface_tab.enable_btn.configure(text="Enable: ON", fg_color=COLORS["success"], text_color=COLORS["white"])
            self.surface_tab.visualizer.draw_zone_overlay(self.zone_mgr.zones)
            self.surface_tab.zone_count_lbl.configure(text=f"{self.zone_mgr.zone_count()} cells blocked")

        self.precision_tab.smooth_val_lbl.configure(text=f"{self.engine.smoothing:.2f}")
        self.precision_tab.jump_val_lbl.configure(text=f"{self.engine.max_jump:.0f}")
        self.precision_tab.deadzone_val_lbl.configure(text=f"{self.engine.deadzone:.1f}")
        self.precision_tab.sens_slider.set(self.engine.sensitivity)
        self.precision_tab.sens_display.configure(text=f"{self.engine.sensitivity:.2f}×")

        mapping_rev = {"ballistic": "macOS Ballistic", "linear": "Linear 1:1", "cad": "Precision CAD", "hyper": "Hyper Dynamic"}
        self.precision_tab.curve_seg.set(mapping_rev.get(self.engine.accel_mode, "macOS Ballistic"))

        self.telemetry.log_event(f"Profile loaded: {prof['title']}")

    # ── Multitouch Pipeline Callback ─────────────────────────────────────────
    def _on_multitouch_frame(self, device, data_ptr, n_fingers, timestamp, frame):
        if not self._running:
            return

        fingers = {}
        zone_suppress = False
        ml_suppress = False
        ml_filt_count = 0
        zone_blk_count = 0
        now = time.time()

        for i in range(n_fingers):
            f = data_ptr[i]
            nx = max(0.0, min(1.0, f.normalized.position.x))
            ny = max(0.0, min(1.0, f.normalized.position.y))
            sz = max(0.0, f.size)

            # 1. Feed ML Model
            if f.state == 1:
                self.ml_guardian.on_contact_begin(f.identifier, nx, ny, sz, f.majorAxis, f.minorAxis, f.timestamp)
            elif f.state == 4:
                self.ml_guardian.on_contact_move(f.identifier, nx, ny, f.timestamp)
            elif f.state == 7:
                self.ml_guardian.on_contact_end(f.identifier, f.timestamp)

            # 2. Oversized contact rejection (palms/arms)
            if sz > self._max_contact_size:
                continue

            # 3. Debounce filter
            if f.state == 1:
                if (now - self._last_tap_time) < (self._debounce_ms / 1000.0):
                    continue
                self._last_tap_time = now

            # 4. Zone blocking
            zb = self.zone_mgr.on_touch(f.identifier, nx, ny, f.state)
            if zb:
                zone_blk_count += 1
                continue

            # 5. ML suppression
            if f.state == 1 and self.ml_guardian.should_suppress_initial(nx, ny):
                ml_filt_count += 1
                ml_suppress = True
                continue

            if f.state in (1, 4, 7):
                fingers[f.identifier] = (nx, ny, sz, f.state)

        self.engine.zone_suppressed = self.zone_mgr.any_suppressed()
        self.engine.ml_suppressed = ml_suppress

        self._ml_filt_total += ml_filt_count
        self._zone_blk_total += zone_blk_count

        self._fingers = fingers
        self.after_idle(lambda fd=dict(fingers): self.surface_tab.visualizer.update_contacts(fd, self.zone_mgr, self.ml_guardian))

    # ── Activation & Lifecycle ───────────────────────────────────────────────
    def _start(self):
        if self._running:
            return
        self._running = True
        self.engine.enabled = True
        self.engine.reset()
        self._session_start = time.time()
        self._ml_filt_total = 0
        self._zone_blk_total = 0

        backup_system_preferences()

        mt_ok = self.mt_manager.start_listening(self._on_multitouch_frame)

        def on_cursor_move(x, y):
            if not self._running or self.engine.zone_suppressed or self.engine.ml_suppressed:
                return
            sx, sy = self.engine.process(x, y)
            if sx is not None and sy is not None:
                self.engine.post_cursor(sx, sy)

        lst_ok = self.mouse_listener.start(on_cursor_move)

        if not mt_ok and not lst_ok:
            self._running = False
            self.engine.enabled = False
            self.status_text.configure(text="Error — Accessibility & Input Monitoring Required")
            self.status_dot.configure(text_color=COLORS["danger"])
            messagebox.showwarning(
                "Permission Required",
                "Please grant Accessibility & Input Monitoring permissions in macOS Settings:\n\n"
                "System Settings → Privacy & Security → Accessibility"
            )
            return

        mode = "Full Multitouch + Kinematic Ballistics" if mt_ok else "Cursor Smoothing Mode"
        self.status_text.configure(text=f"Active & Filtering  —  {mode}")
        self.status_dot.configure(text_color=COLORS["success_light"])

        # Button states & colors
        self.start_btn.configure(state="disabled", fg_color=COLORS["card_hover"], text_color=COLORS["text_muted"])
        self.stop_btn.configure(state="normal", fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"], text_color=COLORS["white"])
        self.reset_btn.configure(state="normal", fg_color=COLORS["info"], hover_color=COLORS["info_hover"], text_color=COLORS["white"])

        self.telemetry.log_event(f"Engine online in {mode}")
        self._schedule_telemetry()

    def _stop(self):
        if not self._running:
            return
        self._running = False
        self.engine.enabled = False
        self.engine.zone_suppressed = False
        self.engine.ml_suppressed = False

        self.mt_manager.stop_listening()
        self.mouse_listener.stop()
        restore_system_preferences()

        if self._stat_timer_id:
            self.after_cancel(self._stat_timer_id)
            self._stat_timer_id = None

        self.status_text.configure(text="System Idle  —  Hardware settings restored cleanly")
        self.status_dot.configure(text_color=COLORS["text_muted"])

        # Button states & colors
        self.start_btn.configure(state="normal", fg_color=COLORS["accent"], text_color=COLORS["white"])
        self.stop_btn.configure(state="disabled", fg_color=COLORS["card_hover"], text_color=COLORS["text_muted"])
        self.reset_btn.configure(state="disabled", fg_color=COLORS["card_hover"], text_color=COLORS["text_muted"])

        self.telemetry.log_event("Engine stopped. Baseline restored.")

    def _recalibrate(self):
        self.engine.reset()
        self.engine.enabled = True
        self.telemetry.log_event("Sensor recalibration event executed.")
        old_text = self.status_text.cget("text")
        self.status_text.configure(text="Recalibrated ✓  —  Kinematics Refreshed")
        self.after(2000, lambda: self.status_text.configure(text=old_text) if self._running else None)

    def _schedule_telemetry(self):
        if not self._running:
            return

        uptime = int(time.time() - self._session_start) if self._session_start else 0
        data = {
            "moves":    f"{self.engine.move_count:,}",
            "jumps":    str(self.engine.jump_count),
            "jitter":   str(self.engine.jitter_count),
            "ml_filt":  str(self._ml_filt_total),
            "zone_blk": str(self._zone_blk_total),
            "uptime":   f"{uptime}s",
        }
        self.telemetry.update_metrics(data)

        # Update ML samples & heatmap
        self.ml_tab.sample_lbl.configure(text=f"Training: {self.ml_guardian.total_samples:,} touches observed")
        if getattr(self.ml_tab, "_heatmap_active", True):
            self.surface_tab.visualizer.draw_ml_heatmap(self.ml_guardian.get_spatial_heatmap())
        else:
            self.surface_tab.visualizer.delete("ml_overlay")

        self._stat_timer_id = self.after(350, self._schedule_telemetry)

    def _on_close(self):
        if self._running:
            self._stop()
        self.destroy()
