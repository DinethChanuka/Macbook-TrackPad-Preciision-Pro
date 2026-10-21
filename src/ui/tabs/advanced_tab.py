"""
Advanced Hardware Settings & macOS System Integration Tab View.
"""

import customtkinter as ctk
from src.config import COLORS
from src.ui.theme import get_font
from src.core.engine import CursorEngine
from src.core.preferences import write_pref, write_bool_pref, PREF_DOMAIN_TOUCH, PREF_DOMAIN_GLOBAL

class AdvancedTab(ctk.CTkFrame):
    def __init__(self, parent, engine: CursorEngine, app_ref, **kwargs):
        super().__init__(parent, fg_color="transparent", **kwargs)
        self.engine = engine
        self.app = app_ref
        self._build_ui()

    def _build_ui(self):
        # 1. Coordinate Routing & Axis Locks Card
        axis_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        axis_card.pack(fill="x", padx=10, pady=(6, 6))

        ctk.CTkLabel(
            axis_card, text="COORDINATE ROUTING & AXIS LOCKS",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        grid = ctk.CTkFrame(axis_card, fg_color="transparent")
        grid.pack(fill="x", padx=14, pady=(0, 10))

        self.inv_x_switch = ctk.CTkSwitch(
            grid, text="Invert X (Horizontal)", font=get_font(10, "bold"),
            progress_color=COLORS["accent"], command=self._on_update_axes
        )
        self.inv_x_switch.grid(row=0, column=0, sticky="w", padx=10, pady=6)

        self.inv_y_switch = ctk.CTkSwitch(
            grid, text="Invert Y (Vertical)", font=get_font(10, "bold"),
            progress_color=COLORS["accent"], command=self._on_update_axes
        )
        self.inv_y_switch.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        self.lock_x_switch = ctk.CTkSwitch(
            grid, text="Lock X (Pure Vertical Only)", font=get_font(10, "bold"),
            progress_color=COLORS["info"], command=self._on_update_axes
        )
        self.lock_x_switch.grid(row=1, column=0, sticky="w", padx=10, pady=6)

        self.lock_y_switch = ctk.CTkSwitch(
            grid, text="Lock Y (Pure Horizontal Only)", font=get_font(10, "bold"),
            progress_color=COLORS["info"], command=self._on_update_axes
        )
        self.lock_y_switch.grid(row=1, column=1, sticky="w", padx=10, pady=6)

        # 2. Hardware Touch Rejection Card
        filt_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        filt_card.pack(fill="x", padx=10, pady=4)

        ctk.CTkLabel(
            filt_card, text="TOUCH DISCRIMINATION & DEBOUNCE",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        # Tap Debounce Slider
        self._create_slider_control(
            filt_card, "Tap-to-Click Debounce Window (ms)", 0.0, 200.0, self.app._debounce_ms,
            lambda v: setattr(self.app, "_debounce_ms", v), fmt=".0f",
            hint="Rejects micro-taps occurring in immediate succession (phantom double-clicks)"
        )

        # Max Contact Size Slider
        self._create_slider_control(
            filt_card, "Max Contact Size Filter (Oversized Rejection)", 0.2, 1.0, self.app._max_contact_size,
            lambda v: setattr(self.app, "_max_contact_size", v), fmt=".2f",
            hint="Instantly discards large touch patches (palms, wrists) before processing movement"
        )

        # 3. macOS Native System Trackpad Settings
        sys_card = ctk.CTkFrame(self, fg_color=COLORS["card"], corner_radius=10)
        sys_card.pack(fill="x", padx=10, pady=(4, 6))

        ctk.CTkLabel(
            sys_card, text="MACOS SYSTEM PREFERENCES INTEGRATION",
            font=get_font(10, "bold", mono=True), text_color=COLORS["text_muted"]
        ).pack(anchor="w", padx=14, pady=(10, 6))

        s_grid = ctk.CTkFrame(sys_card, fg_color="transparent")
        s_grid.pack(fill="x", padx=14, pady=(0, 6))

        self.momentum_switch = ctk.CTkSwitch(
            s_grid, text="Momentum Inertia Scroll", font=get_font(10, "bold"),
            progress_color=COLORS["success"], command=self._on_momentum
        )
        self.momentum_switch.select()
        self.momentum_switch.grid(row=0, column=0, sticky="w", padx=10, pady=6)

        self.natural_switch = ctk.CTkSwitch(
            s_grid, text="Natural Scroll Direction", font=get_font(10, "bold"),
            progress_color=COLORS["success"], command=self._on_natural
        )
        self.natural_switch.select()
        self.natural_switch.grid(row=0, column=1, sticky="w", padx=10, pady=6)

        self.tap_click_switch = ctk.CTkSwitch(
            s_grid, text="Tap-to-Click Hardware Gesture", font=get_font(10, "bold"),
            progress_color=COLORS["success"], command=self._on_tap_click
        )
        self.tap_click_switch.select()
        self.tap_click_switch.grid(row=1, column=0, sticky="w", padx=10, pady=6)

        # Haptic Click Force Segmented Button
        haptic_row = ctk.CTkFrame(sys_card, fg_color=COLORS["card_hover"], corner_radius=8)
        haptic_row.pack(fill="x", padx=14, pady=(4, 10))

        ctk.CTkLabel(
            haptic_row, text="Force Touch Haptic Click Force:",
            font=get_font(11, "bold"), text_color=COLORS["text_primary"]
        ).pack(side="left", padx=(12, 10), pady=8)

        self.haptic_seg = ctk.CTkSegmentedButton(
            haptic_row, values=["Light", "Medium", "Firm"],
            selected_color=COLORS["info"], selected_hover_color=COLORS["info_hover"],
            font=get_font(10, "bold"), command=self._on_haptic_change
        )
        self.haptic_seg.set("Medium")
        self.haptic_seg.pack(side="right", padx=10, pady=6)

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

    def _on_update_axes(self):
        self.engine.invert_x = bool(self.inv_x_switch.get())
        self.engine.invert_y = bool(self.inv_y_switch.get())
        self.engine.lock_x = bool(self.lock_x_switch.get())
        self.engine.lock_y = bool(self.lock_y_switch.get())

    def _on_momentum(self):
        val = "1" if self.momentum_switch.get() else "0"
        write_pref(PREF_DOMAIN_TOUCH, "TrackpadMomentumScroll", val)

    def _on_natural(self):
        write_bool_pref(PREF_DOMAIN_GLOBAL, "com.apple.swipescrolldirection", bool(self.natural_switch.get()))

    def _on_tap_click(self):
        val = "1" if self.tap_click_switch.get() else "0"
        write_pref(PREF_DOMAIN_TOUCH, "Clicking", val)

    def _on_haptic_change(self, choice: str):
        mapping = {"Light": "0", "Medium": "1", "Firm": "2"}
        write_pref(PREF_DOMAIN_TOUCH, "FirstClickThreshold", mapping.get(choice, "1"))
