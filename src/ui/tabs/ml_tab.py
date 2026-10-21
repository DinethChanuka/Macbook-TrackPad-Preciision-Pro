"""
Advanced ML Touch Guardian Tab View.
Controls the online multi-variate statistical learning and palm anomaly detector.
"""

import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
from src.config import COLORS
from src.ui.theme import get_font
from src.ml.classifier import MLTouchGuardian

class MLTab(ctk.CTkFrame):
    def __init__(self, parent, ml_guardian: MLTouchGuardian, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.ml_guardian = ml_guardian
        self._build_ui()

    def _build_ui(self):
        # 1. Status Banner Card
        stat_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        stat_card.pack(fill="x", padx=10, pady=(6, 6))

        hdr = ctk.CTkFrame(stat_card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            hdr, text="ONLINE ANOMALY DETECTOR & GAUSSIAN LEARNING",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(side="left")

        self.sample_lbl = ctk.CTkLabel(
            hdr, text="Training: 0 touches observed",
            font=get_font(10, mono=True), text_color=COLORS["warning_light"]
        )
        self.sample_lbl.pack(side="right")

        desc = (
            "The ML Touch Guardian continuously analyzes contact duration, ellipse eccentricity, "
            "surface area, trajectory wander, and border proximity to identify accidental touches and resting palms."
        )
        ctk.CTkLabel(
            stat_card, text=desc, font=get_font(10), text_color=COLORS["text_secondary"],
            wraplength=520, justify="left"
        ).pack(anchor="w", padx=14, pady=(0, 10))

        # 2. Controls & Switches Card
        ctrl_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        ctrl_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            ctrl_card, text="ACTIVE CLASSIFICATION & MITIGATION CONTROLS",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        # Switches Row
        s_row = ctk.CTkFrame(ctrl_card, fg_color="transparent")
        s_row.pack(fill="x", padx=14, pady=4)

        self.filter_switch = ctk.CTkSwitch(
            s_row, text="Active Accidental Tap Suppression", font=get_font(11, "bold"),
            progress_color=COLORS["warning"], button_color=COLORS["white"],
            command=self._on_toggle_filter
        )
        self.filter_switch.pack(side="left", padx=(0, 20))

        self.heatmap_switch = ctk.CTkSwitch(
            s_row, text="Render Heatmap on Surface", font=get_font(11, "bold"),
            progress_color=COLORS["danger"], button_color=COLORS["white"],
            command=self._on_toggle_heatmap
        )
        self.heatmap_switch.select()
        self.heatmap_switch.pack(side="left", padx=(0, 20))

        self.freeze_switch = ctk.CTkSwitch(
            s_row, text="Freeze Learning (Lock Weights)", font=get_font(11, "bold"),
            progress_color=COLORS["purple"], button_color=COLORS["white"],
            command=self._on_toggle_freeze
        )
        self.freeze_switch.pack(side="left")

        # Threshold Slider
        self.thresh_val_lbl = self._create_slider_control(
            ctrl_card, "Suspicion Threshold (Sensitivity)", 0.1, 0.95, self.ml_guardian.threshold,
            lambda v: setattr(self.ml_guardian, "threshold", v), fmt=".2f",
            hint="← Aggressive Suppression (Blocks more touches)          Permissive (Light Filtering) →"
        )

        # Decay Rate Slider
        self.decay_val_lbl = self._create_slider_control(
            ctrl_card, "Spatial Memory Retention (Decay)", 0.980, 0.999, self.ml_guardian.decay_factor,
            lambda v: setattr(self.ml_guardian, "decay_factor", v), fmt=".4f",
            hint="← Rapid Adaptation / Forgets Fast          Permanent Memory Lock →"
        )

        # 3. Model Weights & Profile Actions
        act_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        act_card.pack(fill="x", padx=10, pady=(4, 8))

        ctk.CTkLabel(
            act_card, text="MODEL PROFILE MANAGEMENT & CALIBRATION",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        btn_row = ctk.CTkFrame(act_card, fg_color="transparent")
        btn_row.pack(fill="x", padx=14, pady=(0, 10))

        ctk.CTkButton(
            btn_row, text="Export Model (JSON)", width=130, height=30,
            fg_color=COLORS["card_hover"], hover_color=COLORS["accent"],
            font=get_font(10, "bold"), text_color=COLORS["text_primary"],
            command=self._export_model
        ).pack(side="left", padx=(0, 6))

        ctk.CTkButton(
            btn_row, text="Import Model (JSON)", width=130, height=30,
            fg_color=COLORS["card_hover"], hover_color=COLORS["info"],
            font=get_font(10, "bold"), text_color=COLORS["text_primary"],
            command=self._import_model
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="⟲ Reset Model Data", width=130, height=30,
            fg_color=COLORS["card_hover"], hover_color=COLORS["danger"],
            font=get_font(10, "bold"), text_color=COLORS["danger_light"],
            command=self._reset_model
        ).pack(side="right")

    def _create_slider_control(self, parent, label: str, lo: float, hi: float, init: float, cb, fmt: str = ".2f", hint: str = ""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=4)

        top = ctk.CTkFrame(row, fg_color="transparent")
        top.pack(fill="x")

        ctk.CTkLabel(top, text=label, font=get_font(11, "bold"), text_color=COLORS["text_primary"]).pack(side="left")

        val_lbl = ctk.CTkLabel(top, text=f"{init:{fmt}}", font=get_font(11, "bold", mono=True), text_color=COLORS["warning_light"])
        val_lbl.pack(side="right")

        slider = ctk.CTkSlider(
            row, from_=lo, to=hi,
            progress_color=COLORS["warning"], button_color=COLORS["warning_light"],
            button_hover_color=COLORS["white"],
            command=lambda v: (val_lbl.configure(text=f"{float(v):{fmt}}"), cb(float(v)))
        )
        slider.set(init)
        slider.pack(fill="x", pady=(2, 0))

        if hint:
            ctk.CTkLabel(row, text=hint, font=get_font(8), text_color=COLORS["text_muted"]).pack(anchor="w")

        return val_lbl

    def _on_toggle_filter(self):
        self.ml_guardian.filtering = bool(self.filter_switch.get())

    def _on_toggle_heatmap(self):
        self._heatmap_active = bool(self.heatmap_switch.get())

    def _on_toggle_freeze(self):
        self.ml_guardian.freeze_learning = bool(self.freeze_switch.get())

    def _reset_model(self):
        self.ml_guardian.reset()
        self.sample_lbl.configure(text="Training: 0 touches observed")
        messagebox.showinfo("ML Model Reset", "All touch suspicion matrices and spatial weights have been reset to baseline.")

    def _export_model(self):
        data = self.ml_guardian.export_weights_json()
        path = filedialog.asksaveasfilename(
            defaultextension=".json", filetypes=[("JSON Files", "*.json")], title="Export ML Model Calibration"
        )
        if path:
            with open(path, "w") as f:
                f.write(data)
            messagebox.showinfo("Export Successful", f"ML Guardian calibration saved to {path}")

    def _import_model(self):
        path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json")], title="Import ML Model Calibration"
        )
        if path:
            with open(path, "r") as f:
                content = f.read()
            if self.ml_guardian.import_weights_json(content):
                messagebox.showinfo("Import Successful", "ML Guardian weights loaded successfully.")
            else:
                messagebox.showerror("Import Error", "Failed to parse calibration JSON file.")
