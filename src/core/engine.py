"""
Advanced Cursor Smoothing, Anti-Jitter Deadzone, and Ballistics Engine.
"""

import math, threading
from collections import deque
from typing import Optional, Tuple

try:
    import Quartz
    _QUARTZ_AVAILABLE = True
except ImportError:
    _QUARTZ_AVAILABLE = False

class CursorEngine:
    def __init__(self):
        self.smoothing: float = 0.30
        self.max_jump: float = 100.0
        self.history_len: int = 4
        self.sensitivity: float = 1.0
        self.deadzone: float = 1.2          # Micro-jitter suppression in pixels
        self.accel_mode: str = "ballistic"  # "linear", "cad", "ballistic", "hyper"

        # Coordinate routing and locks
        self.invert_x: bool = False
        self.invert_y: bool = False
        self.lock_x: bool = False
        self.lock_y: bool = False

        # State suppression flags
        self.zone_suppressed: bool = False
        self.ml_suppressed: bool = False
        self.enabled: bool = False

        # Telemetry metrics
        self.move_count: int = 0
        self.jump_count: int = 0
        self.jitter_count: int = 0

        self._lock = threading.Lock()
        self._last_x: Optional[float] = None
        self._last_y: Optional[float] = None
        self._history: deque = deque(maxlen=self.history_len)

    def reset(self):
        with self._lock:
            self._last_x = None
            self._last_y = None
            self._history.clear()
            self.move_count = 0
            self.jump_count = 0
            self.jitter_count = 0

    def process(self, raw_x: float, raw_y: float) -> Tuple[Optional[float], Optional[float]]:
        with self._lock:
            if not self.enabled or self.zone_suppressed or self.ml_suppressed:
                return None, None

            if self._last_x is None:
                self._last_x, self._last_y = raw_x, raw_y
                return None, None

            dx = raw_x - self._last_x
            dy = raw_y - self._last_y
            dist = math.hypot(dx, dy)

            # 1. Anti-jitter micro-tremor deadzone filter
            if dist < self.deadzone:
                self.jitter_count += 1
                return None, None

            # 2. Jump rejection filter (hardware coordinate spikes)
            if dist > self.max_jump:
                self.jump_count += 1
                return None, None

            # 3. Ballistics & Acceleration Curves
            if self.accel_mode == "linear":
                accel = 1.0
            elif self.accel_mode == "cad":
                # Dampen micro-movements for pixel art and CAD precision
                accel = 0.55 + 0.45 * min(1.0, dist / 18.0)
            elif self.accel_mode == "hyper":
                # Dynamic boost for high-speed multi-monitor travel
                accel = 1.0 + min(2.8, (dist / 16.0) ** 1.3)
            else:  # "ballistic" (macOS trackpad standard)
                accel = 1.0 + min(1.3, (dist / 28.0) ** 0.85)

            dx = dx * self.sensitivity * accel
            dy = dy * self.sensitivity * accel

            # 4. Inversion and Axis Locks
            if self.invert_x: dx = -dx
            if self.invert_y: dy = -dy
            if self.lock_x:   dx = 0.0
            if self.lock_y:   dy = 0.0

            # 5. Weighted Moving Average Smoothing
            self._history.append((dx, dy))
            n = len(self._history)
            weights = [i + 1 for i in range(n)]
            total_w = sum(weights)
            avg_dx = sum(w * h[0] for w, h in zip(weights, self._history)) / total_w
            avg_dy = sum(w * h[1] for w, h in zip(weights, self._history)) / total_w

            sx = self._last_x + avg_dx * self.smoothing
            sy = self._last_y + avg_dy * self.smoothing

            self._last_x, self._last_y = sx, sy
            self.move_count += 1
            return sx, sy

    def post_cursor(self, x: float, y: float):
        if not _QUARTZ_AVAILABLE:
            return
        try:
            evt = Quartz.CGEventCreateMouseEvent(
                None, Quartz.kCGEventMouseMoved,
                (x, y), Quartz.kCGMouseButtonLeft
            )
            Quartz.CGEventPost(Quartz.kCGHIDEventTap, evt)
        except Exception:
            pass
