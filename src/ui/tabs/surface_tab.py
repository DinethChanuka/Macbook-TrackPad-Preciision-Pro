"""
Surface & Zone Exclusion Studio Tab View.
Provides visual canvas, 1-click palm rejection presets, and custom zone painting.
"""

import customtkinter as ctk
import tkinter as tk
from src.config import COLORS
from src.ui.theme import get_font
from src.ui.components.visualizer import TouchVisualizer
from src.zones.manager import ZoneManager
from src.ml.classifier import MLTouchGuardian

class SurfaceTab(ctk.CTkFrame):
    def __init__(self, parent, zone_mgr: ZoneManager, ml_guardian: MLTouchGuardian, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.zone_mgr = zone_mgr
        self.ml_guardian = ml_guardian
        self._edit_mode = False

        self._build_ui()

    def _build_ui(self):
        # 1. Main Visualizer Card
        card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        card.pack(fill="x", padx=10, pady=(6, 8))

        top_bar = ctk.CTkFrame(card, fg_color="transparent")
        top_bar.pack(fill="x", padx=14, pady=(10, 6))

        ctk.CTkLabel(
            top_bar, text="MULTITOUCH SURFACE MATRIX",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(side="left")

        self.contact_count_lbl = ctk.CTkLabel(
            top_bar, text="0 touches active",
            font=get_font(10, mono=True), text_color=COLORS["accent_light"]
        )
        self.contact_count_lbl.pack(side="right")

        # Interactive Canvas
        viz_wrap = ctk.CTkFrame(card, fg_color=COLORS["border"], corner_radius=6, border_width=1, border_color=COLORS["border"])
        viz_wrap.pack(fill="x", padx=14, pady=4)

        self.visualizer = TouchVisualizer(viz_wrap, width=540, height=180)
        self.visualizer.pack(fill="x", padx=1, pady=1)

        # Zone Studio Toolbar
        zt = ctk.CTkFrame(card, fg_color=COLORS["card_hover"], corner_radius=8)
        zt.pack(fill="x", padx=14, pady=(8, 10))

        ctk.CTkLabel(
            zt, text="ZONE EXCLUSION:",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_secondary"]
        ).pack(side="left", padx=(10, 8), pady=8)

        self.zone_count_lbl = ctk.CTkLabel(
            zt, text="0 cells blocked",
            font=get_font(10, mono=True), text_color=COLORS["danger_light"]
        )
        self.zone_count_lbl.pack(side="left")

        # True-color CustomTkinter Action Buttons
        self.enable_btn = ctk.CTkButton(
            zt, text="Enable: OFF", width=105, height=28,
            fg_color=COLORS["border_focus"], hover_color=COLORS["success_hover"],
            font=get_font(10, "bold"), text_color=COLORS["text_muted"],
            command=self._toggle_enable
        )
        self.enable_btn.pack(side="right", padx=(4, 10), pady=6)

        self.paint_btn = ctk.CTkButton(
            zt, text="✏ Paint Zones", width=115, height=28,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            font=get_font(10, "bold"), text_color=COLORS["white"],
            command=self._toggle_edit
        )
        self.paint_btn.pack(side="right", padx=4, pady=6)

        # 2. Preset Selection Card
        preset_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        preset_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            preset_card, text="ONE-CLICK EXCLUSION PRESETS",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 4))

        row = ctk.CTkFrame(preset_card, fg_color="transparent")
        row.pack(fill="x", padx=10, pady=(0, 10))

        presets = [
            ("Left Palm", "left_palm", COLORS["info"]),
            ("Right Palm", "right_palm", COLORS["info"]),
            ("Bottom Strip", "bottom_strip", COLORS["warning"]),
            ("Both Corners", "corners", COLORS["purple"]),
            ("Top Bar", "top_bar", COLORS["accent"]),
            ("Clear All", "clear", COLORS["danger"]),
        ]

        for title, key, col in presets:
            ctk.CTkButton(
                row, text=title, width=80, height=30,
                fg_color=COLORS["card_hover"], hover_color=col,
                font=get_font(10, "bold"), text_color=COLORS["text_primary"],
                command=lambda k=key: self._apply_preset(k)
            ).pack(side="left", padx=3, expand=True, fill="x")

        # Instruction banner
        self.instr_lbl = ctk.CTkLabel(
            self, text="  Left-Drag: Paint Red Exclusion  ·  Right-Drag / Option-Drag: Erase  ·  Click Done to finish",
            font=get_font(10, "bold", mono=True), fg_color=COLORS["warning"], text_color=COLORS["white"],
            corner_radius=6, height=28
        )

    def _toggle_enable(self):
        self.zone_mgr.enabled = not self.zone_mgr.enabled
        if self.zone_mgr.enabled:
            self.enable_btn.configure(
                text="Enable: ON", fg_color=COLORS["success"], text_color=COLORS["white"]
            )
        else:
            self.enable_btn.configure(
                text="Enable: OFF", fg_color=COLORS["border_focus"], text_color=COLORS["text_muted"]
            )

    def _toggle_edit(self):
        if not self._edit_mode:
            self._edit_mode = True
            self.paint_btn.configure(
                text="✓ Done Painting", fg_color=COLORS["success"], text_color=COLORS["white"]
            )
            self.visualizer.configure(cursor="pencil")
            self.instr_lbl.pack(fill="x", padx=10, pady=(0, 6))
            self.visualizer.draw_edit_grid()
            self.visualizer.bind("<Button-1>", self._on_paint)
            self.visualizer.bind("<B1-Motion>", self._on_paint)
            self.visualizer.bind("<Button-2>", self._on_erase)
            self.visualizer.bind("<Button-3>", self._on_erase)
            self.visualizer.bind("<B3-Motion>", self._on_erase)
        else:
            self._edit_mode = False
            self.paint_btn.configure(
                text="✏ Paint Zones", fg_color=COLORS["accent"], text_color=COLORS["white"]
            )
            self.visualizer.configure(cursor="crosshair")
            self.instr_lbl.pack_forget()
            self.visualizer.delete("edit_grid")
            self.visualizer.unbind("<Button-1>")
            self.visualizer.unbind("<B1-Motion>")
            self.visualizer.unbind("<Button-2>")
            self.visualizer.unbind("<Button-3>")
            self.visualizer.unbind("<B3-Motion>")
            self.visualizer.draw_zone_overlay(self.zone_mgr.zones)

    def _on_paint(self, event):
        nx, ny = self.visualizer.canvas_to_normalized(event.x, event.y)
        cell = self.zone_mgr.cell_of(nx, ny)
        self.zone_mgr.zones.add(cell)
        self.visualizer.draw_zone_overlay(self.zone_mgr.zones)
        self.zone_count_lbl.configure(text=f"{self.zone_mgr.zone_count()} cells blocked")

    def _on_erase(self, event):
        nx, ny = self.visualizer.canvas_to_normalized(event.x, event.y)
        cell = self.zone_mgr.cell_of(nx, ny)
        self.zone_mgr.zones.discard(cell)
        self.visualizer.draw_zone_overlay(self.zone_mgr.zones)
        self.zone_count_lbl.configure(text=f"{self.zone_mgr.zone_count()} cells blocked")

    def _apply_preset(self, key: str):
        if key == "clear":
            self.zone_mgr.clear()
        else:
            self.zone_mgr.apply_preset(key)
        self.visualizer.draw_zone_overlay(self.zone_mgr.zones)
        self.zone_count_lbl.configure(text=f"{self.zone_mgr.zone_count()} cells blocked")
