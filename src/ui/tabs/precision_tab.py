"""
Precision Engine & Ballistics Acceleration Tab View.
"""

import customtkinter as ctk
import tkinter as tk
from src.config import COLORS
from src.ui.theme import get_font
from src.core.engine import CursorEngine

class PrecisionTab(ctk.CTkFrame):
    def __init__(self, parent, engine: CursorEngine, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.engine = engine
        self._build_ui()

    def _build_ui(self):
        # 1. Kinematics Card
        k_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        k_card.pack(fill="x", padx=10, pady=(6, 6))

        ctk.CTkLabel(
            k_card, text="KINEMATIC SMOOTHING & JITTER REJECTION",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        # Smoothing Slider
        self.smooth_val_lbl = self._create_slider_control(
            k_card, "Smoothing Coefficient", 0.05, 1.0, self.engine.smoothing,
            lambda v: self._on_smooth_change(v), fmt=".2f",
            hint="← Buttery Smooth (Low Delay)          Direct Raw Input →"
        )

        # Jump Rejection Slider
        self.jump_val_lbl = self._create_slider_control(
            k_card, "Hardware Coordinate Spike Filter", 15, 300, self.engine.max_jump,
            lambda v: self._on_jump_change(v), fmt=".0f",
            hint="← Strict Discontinuity Blocker              Permissive →"
        )

        # Anti-Jitter Deadzone Slider
        self.deadzone_val_lbl = self._create_slider_control(
            k_card, "Anti-Jitter Micro-Tremor Deadzone (px)", 0.0, 6.0, self.engine.deadzone,
            lambda v: self._on_deadzone_change(v), fmt=".1f",
            hint="Suppresses subtle finger shaking & desk vibrations when hand is stationary"
        )

        # Ballistics Curve Selector
        curve_box = ctk.CTkFrame(k_card, fg_color=COLORS["card_hover"], corner_radius=8)
        curve_box.pack(fill="x", padx=14, pady=(8, 12))

        ctk.CTkLabel(
            curve_box, text="Acceleration Ballistics Curve:",
            font=get_font(11, "bold"), text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(12, 10), pady=10)

        self.curve_seg = ctk.CTkSegmentedButton(
            curve_box, values=["macOS Ballistic", "Linear 1:1", "Precision CAD", "Hyper Dynamic"],
            selected_color=COLORS["accent"], selected_hover_color=COLORS["accent_hover"],
            font=get_font(10, "bold"), command=self._on_curve_change
        )
        self.curve_seg.set("macOS Ballistic")
        self.curve_seg.pack(side="right", padx=10, pady=8)

        # 2. Sensitivity & Gain Card
        sens_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        sens_card.pack(fill="x", padx=10, pady=4)

        sens_hdr = ctk.CTkFrame(sens_card, fg_color="transparent")
        sens_hdr.pack(fill="x", padx=14, pady=(10, 4))

        ctk.CTkLabel(
            sens_hdr, text="DYNAMIC HARDWARE SENSITIVITY MULTIPLIER",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(side="left")

        self.sens_preset_lbl = ctk.CTkLabel(
            sens_hdr, text="Normal (1.00×)",
            font=get_font(10, "bold", mono=True), text_color=COLORS["success_light"]
        )
        self.sens_preset_lbl.pack(side="right")

        # Multiplier Big Numeric Display
        self.sens_display = ctk.CTkLabel(
            sens_card, text=f"{self.engine.sensitivity:.2f}×",
            font=get_font(24, "bold", mono=True), text_color=COLORS["success_light"]
        )
        self.sens_display.pack(pady=(0, 2))

        self.sens_slider = ctk.CTkSlider(
            sens_card, from_=0.1, to=3.5, number_of_steps=68,
            progress_color=COLORS["success"], button_color=COLORS["success_light"],
            button_hover_color=COLORS["white"], command=self._on_sens_slide
        )
        self.sens_slider.set(self.engine.sensitivity)
        self.sens_slider.pack(fill="x", padx=14, pady=4)

        # LED Sensitivity Gauge Canvas
        self.led_canvas = tk.Canvas(sens_card, height=6, bg=COLORS["bg"], highlightthickness=0)
        self.led_canvas.pack(fill="x", padx=14, pady=(2, 8))
        self.after(100, self._draw_led_meter)

        # Quick Presets Row
        p_row = ctk.CTkFrame(sens_card, fg_color="transparent")
        p_row.pack(fill="x", padx=10, pady=(0, 10))

        presets = [
            ("Precise (0.4×)", 0.4, COLORS["info"]),
            ("Normal (1.0×)",  1.0, COLORS["success"]),
            ("Fast (1.8×)",    1.8, COLORS["warning"]),
            ("Turbo (3.0×)",   3.0, COLORS["danger"]),
        ]
        for title, val, col in presets:
            ctk.CTkButton(
                p_row, text=title, height=28,
                fg_color=COLORS["card_hover"], hover_color=col,
                font=get_font(10, "bold"), text_color=COLORS["text_primary"],
                command=lambda v=val, t=title: self._set_sens_preset(v, t)
            ).pack(side="left", padx=4, expand=True, fill="x")

    def _create_slider_control(self, parent, label: str, lo: float, hi: float, init: float, cb, fmt: str = ".2f", hint: str = ""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=4)

        top = ctk.CTkFrame(row, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=label, font=get_font(11, "bold"), text_color=COLORS["text_primary"]).pack(side="left")

        val_lbl = ctk.CTkLabel(top, text=f"{init:{fmt}}", font=get_font(11, "bold", mono=True), text_color=COLORS["accent_light"])
        val_lbl.pack(side="right")

        slider = ctk.CTkSlider(
            row, from_=lo, to=hi,
            progress_color=COLORS["accent"], button_color=COLORS["accent_light"],
            button_hover_color=COLORS["white"],
            command=lambda v: (val_lbl.configure(text=f"{float(v):{fmt}}"), cb(float(v)))
        )
        slider.set(init)
        slider.pack(fill="x", pady=(2, 0))

        if hint:
            ctk.CTkLabel(row, text=hint, font=get_font(8), text_color=COLORS["text_muted"]).pack(anchor="w")

        return val_lbl

    def _on_smooth_change(self, v: float):
        self.engine.smoothing = v

    def _on_jump_change(self, v: float):
        self.engine.max_jump = v

    def _on_deadzone_change(self, v: float):
        self.engine.deadzone = v

    def _on_curve_change(self, choice: str):
        mapping = {
            "macOS Ballistic": "ballistic",
            "Linear 1:1": "linear",
            "Precision CAD": "cad",
            "Hyper Dynamic": "hyper",
        }
        self.engine.accel_mode = mapping.get(choice, "ballistic")

    def _on_sens_slide(self, v: float):
        self.engine.sensitivity = float(v)
        self.sens_display.configure(text=f"{v:.2f}×")
        self.sens_preset_lbl.configure(text=f"Custom ({v:.2f}×)")
        self._draw_led_meter()

    def _set_sens_preset(self, v: float, label: str):
        self.engine.sensitivity = v
        self.sens_slider.set(v)
        self.sens_display.configure(text=f"{v:.2f}×")
        self.sens_preset_lbl.configure(text=label)
        self._draw_led_meter()

    def _draw_led_meter(self):
        try:
            w = self.led_canvas.winfo_width() or 400
            self.led_canvas.delete("all")
            zones = [
                (0.0, 0.33, "#38bdf8", "#34d399"),
                (0.33, 0.66, "#34d399", "#fbbf24"),
                (0.66, 1.0,  "#fbbf24", "#f87171"),
            ]
            for zs, ze, c1, c2 in zones:
                xs, xe = int(zs * w), int(ze * w)
                seg = xe - xs
                if seg <= 0: continue
                r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
                r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
                for px in range(seg):
                    t = px / max(1, seg - 1)
                    rv = int(r1 + (r2 - r1) * t)
                    gv = int(g1 + (g2 - g1) * t)
                    bv = int(b1 + (b2 - b1) * t)
                    self.led_canvas.create_line(xs + px, 0, xs + px, 6, fill=f"#{rv:02x}{gv:02x}{bv:02x}")

            needle_x = int(((self.engine.sensitivity - 0.1) / 3.4) * w)
            self.led_canvas.create_line(needle_x, 0, needle_x, 6, fill=COLORS["white"], width=2)
        except Exception:
            pass
