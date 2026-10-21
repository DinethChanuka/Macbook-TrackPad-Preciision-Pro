"""
Interactive Touch Surface Canvas Visualizer.
Renders real-time multitouch contact points, pressure ellipses, zone masks, and ML heatmaps.
"""

import tkinter as tk
from typing import Dict, List, Tuple, Callable
from src.config import COLORS
from src.zones.manager import ZoneManager
from src.ml.classifier import MLTouchGuardian

class TouchVisualizer(tk.Canvas):
    def __init__(self, parent, width: int = 480, height: int = 175, **kwargs):
        super().__init__(
            parent, width=width, height=height,
            bg=COLORS["bg"], highlightthickness=1,
            highlightbackground=COLORS["border"],
            cursor="crosshair", **kwargs
        )
        self.viz_w = width
        self.viz_h = height
        self.draw_grid()

    def draw_grid(self):
        self.delete("grid")
        W, H = self.viz_w, self.viz_h
        for i in range(1, 6):
            x = i * (W // 6)
            self.create_line(x, 0, x, H, fill=COLORS["border"], dash=(2, 6), tags="grid")
        for i in range(1, 4):
            y = i * (H // 4)
            self.create_line(0, y, W, y, fill=COLORS["border"], dash=(2, 6), tags="grid")

    def draw_zone_overlay(self, zones: set):
        self.delete("zone_overlay")
        if not zones:
            return
        W, H = self.viz_w, self.viz_h
        GW, GH = ZoneManager.GRID_W, ZoneManager.GRID_H
        cw, ch = W / GW, H / GH

        for (gx, gy) in zones:
            x1 = int(gx * cw)
            x2 = int(x1 + cw) + 1
            y2 = int((1.0 - gy / GH) * H)
            y1 = int((1.0 - (gy + 1) / GH) * H)

            self.create_rectangle(
                x1, y1, x2, y2,
                fill=COLORS["danger"], outline=COLORS["danger_light"],
                stipple="gray25", tags="zone_overlay"
            )
            self.create_rectangle(
                x1, y1, x2, y2,
                fill="", outline=COLORS["danger_light"], width=1, tags="zone_overlay"
            )

    def draw_ml_heatmap(self, scores: List[float]):
        self.delete("ml_overlay")
        W, H = self.viz_w, self.viz_h
        GW, GH = MLTouchGuardian.GRID_W, MLTouchGuardian.GRID_H
        cw, ch = W / GW, H / GH

        bg_r, bg_g, bg_b = 0x0a, 0x0d, 0x14
        hi_r, hi_g, hi_b = 0xef, 0x44, 0x44

        for idx, score in enumerate(scores):
            if score < 0.08:
                continue
            gy = idx // GW
            gx = idx % GW
            x1 = int(gx * cw)
            x2 = int(x1 + cw) + 1
            y2 = int((1.0 - gy / GH) * H)
            y1 = int((1.0 - (gy + 1) / GH) * H)

            r = int(bg_r + (hi_r - bg_r) * score)
            g = int(bg_g + (hi_g - bg_g) * score)
            b = int(bg_b + (hi_b - bg_b) * score)
            col = f"#{r:02x}{g:02x}{b:02x}"

            self.create_rectangle(x1, y1, x2, y2, fill=col, outline="", tags="ml_overlay")
            if score > 0.65:
                self.create_rectangle(x1, y1, x2, y2, fill="", outline=COLORS["danger_light"], width=1, tags="ml_overlay")

    def draw_edit_grid(self):
        self.delete("edit_grid")
        W, H = self.viz_w, self.viz_h
        GW, GH = ZoneManager.GRID_W, ZoneManager.GRID_H
        cw, ch = W / GW, H / GH
        for gx in range(GW + 1):
            x = int(gx * cw)
            self.create_line(x, 0, x, H, fill=COLORS["border_focus"], tags="edit_grid")
        for gy in range(GH + 1):
            y = int(gy * ch)
            self.create_line(0, y, W, y, fill=COLORS["border_focus"], tags="edit_grid")

    def update_contacts(self, fingers: Dict, zone_mgr: ZoneManager, ml_guardian: MLTouchGuardian):
        self.delete("finger")
        self.delete("hint")

        if not fingers:
            self.create_text(
                self.viz_w // 2, self.viz_h // 2,
                text="Trackpad Multitouch Surface Active  ·  Touch surface to inspect real-time contacts",
                font=("Helvetica Neue", 10), fill=COLORS["text_muted"], tags="hint"
            )
            return

        W, H = self.viz_w, self.viz_h
        palette = [COLORS["accent_light"], COLORS["info_light"], COLORS["success_light"], COLORS["warning_light"], COLORS["danger_light"]]

        for idx, (fid, data) in enumerate(fingers.items()):
            nx, ny, size, state = data
            cx = max(14, min(W - 14, int(nx * W)))
            cy = max(14, min(H - 14, int((1.0 - ny) * H)))
            r = max(10, min(34, int(size * 48 + 8)))
            base_col = palette[idx % len(palette)]

            is_zone = zone_mgr.enabled and zone_mgr.in_zone(nx, ny)
            is_ml = ml_guardian.should_suppress_initial(nx, ny)

            dot_col = COLORS["danger_light"] if is_zone else (COLORS["warning_light"] if is_ml else base_col)

            # Outer ring & glow
            self.create_oval(cx - r - 6, cy - r - 6, cx + r + 6, cy + r + 6, fill="", outline=COLORS["border_focus"], width=1, tags="finger")
            self.create_oval(cx - r, cy - r, cx + r, cy + r, fill=dot_col, outline=COLORS["white"], width=1, tags="finger")
            self.create_text(cx, cy, text=str(idx + 1), font=("Menlo", 9, "bold"), fill=COLORS["white"], tags="finger")

            indicator = " ⛔ BLOCKED" if is_zone else (" ⚠ SUSPICIOUS" if is_ml else "")
            self.create_text(
                cx, cy + r + 11,
                text=f"{nx:.2f},{ny:.2f}{indicator}",
                font=("Menlo", 8), fill=dot_col, tags="finger"
            )

    def canvas_to_normalized(self, cx: int, cy: int) -> Tuple[float, float]:
        nx = max(0.0, min(1.0, cx / self.viz_w))
        ny = max(0.0, min(1.0, 1.0 - cy / self.viz_h))
        return nx, ny
