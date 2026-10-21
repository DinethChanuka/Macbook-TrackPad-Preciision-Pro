"""
Zone Manager for Spatial Exclusion and Palm Rest Mitigation.
Blocks accidental taps initiated within defined grid regions while allowing deliberate gestures.
"""

import math, threading
from typing import Set, Tuple, Dict, Any

class ZoneManager:
    GRID_W = 20
    GRID_H = 10
    DRAG_THRESHOLD = 0.045  # Normalized distance required to transition to drag

    def __init__(self):
        self.zones: Set[Tuple[int, int]] = set()
        self.enabled: bool = False
        self._lock = threading.Lock()
        self._touches: Dict[int, Dict[str, Any]] = {}

    def cell_of(self, nx: float, ny: float) -> Tuple[int, int]:
        gx = min(int(nx * self.GRID_W), self.GRID_W - 1)
        gy = min(int(ny * self.GRID_H), self.GRID_H - 1)
        return (max(0, gx), max(0, gy))

    def in_zone(self, nx: float, ny: float) -> bool:
        return self.cell_of(nx, ny) in self.zones

    def on_touch(self, tid: int, nx: float, ny: float, state: int) -> bool:
        """
        Returns True if the touch should be suppressed/blocked.
        state: 1=begin, 4=move, 7=end
        """
        if not self.enabled or not self.zones:
            return False

        with self._lock:
            if state == 1:
                in_z = self.in_zone(nx, ny)
                self._touches[tid] = {
                    "in_zone": in_z,
                    "sx": nx,
                    "sy": ny,
                    "is_drag": False,
                }
                return in_z

            rec = self._touches.get(tid)
            if rec is None or not rec["in_zone"]:
                return False

            if state == 7:
                self._touches.pop(tid, None)
                # Suppress if touch never converted into a deliberate drag
                return not rec["is_drag"]

            # state == 4: moving
            dist = math.hypot(nx - rec["sx"], ny - rec["sy"])
            if dist > self.DRAG_THRESHOLD:
                rec["is_drag"] = True
            return not rec["is_drag"]

    def any_suppressed(self) -> bool:
        with self._lock:
            return any(r["in_zone"] and not r["is_drag"] for r in self._touches.values())

    def clear(self):
        with self._lock:
            self.zones.clear()
            self._touches.clear()

    def apply_preset(self, preset_name: str):
        with self._lock:
            self.zones.clear()
            if preset_name == "left_palm":
                for gx in range(5):
                    for gy in range(7):
                        self.zones.add((gx, gy))
            elif preset_name == "right_palm":
                for gx in range(15, 20):
                    for gy in range(7):
                        self.zones.add((gx, gy))
            elif preset_name == "bottom_strip":
                for gx in range(20):
                    for gy in range(2):
                        self.zones.add((gx, gy))
            elif preset_name == "corners":
                for gx in list(range(4)) + list(range(16, 20)):
                    for gy in range(4):
                        self.zones.add((gx, gy))
            elif preset_name == "top_bar":
                for gx in range(20):
                    for gy in range(8, 10):
                        self.zones.add((gx, gy))

    def zone_count(self) -> int:
        return len(self.zones)
