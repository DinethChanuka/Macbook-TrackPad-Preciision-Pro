"""
Feature Extraction for Trackpad Multitouch Contact Telemetry.
Extracts kinematic, geometric, and spatial metrics from live touch contact streams.
"""

import math
from typing import List, Tuple, Dict, Any

class ContactTrajectory:
    def __init__(self, tid: int, start_x: float, start_y: float, size: float, major: float, minor: float, ts: float):
        self.tid = tid
        self.start_x = start_x
        self.start_y = start_y
        self.current_x = start_x
        self.current_y = start_y
        self.size = size
        self.major = major
        self.minor = minor
        self.start_time = ts
        self.last_time = ts
        self.points: List[Tuple[float, float, float]] = [(start_x, start_y, ts)]
        self.total_path: float = 0.0
        self.peak_velocity: float = 0.0

    def add_point(self, x: float, y: float, ts: float):
        dt = max(0.0001, ts - self.last_time)
        dx = x - self.current_x
        dy = y - self.current_y
        dist = math.hypot(dx, dy)
        vel = dist / dt
        if vel > self.peak_velocity:
            self.peak_velocity = vel

        self.total_path += dist
        self.current_x = x
        self.current_y = y
        self.last_time = ts
        self.points.append((x, y, ts))

    def extract_features(self) -> Dict[str, float]:
        duration = max(0.001, self.last_time - self.start_time)
        net_disp = math.hypot(self.current_x - self.start_x, self.current_y - self.start_y)
        tortuosity = self.total_path / max(0.0005, net_disp)

        # Ellipse aspect ratio (palms and resting edges tend to be elongated)
        aspect_ratio = self.major / max(0.01, self.minor)

        # Proximity to edges (normalized trackpad coords 0.0 to 1.0)
        d_left = self.start_x
        d_right = 1.0 - self.start_x
        d_bottom = self.start_y
        d_top = 1.0 - self.start_y
        min_edge_dist = min(d_left, d_right, d_bottom, d_top)

        mean_velocity = self.total_path / duration

        return {
            "duration": duration,
            "net_displacement": net_disp,
            "total_path": self.total_path,
            "tortuosity": min(10.0, tortuosity),
            "size": self.size,
            "aspect_ratio": min(10.0, aspect_ratio),
            "peak_velocity": self.peak_velocity,
            "mean_velocity": mean_velocity,
            "edge_distance": min_edge_dist,
            "x": self.start_x,
            "y": self.start_y,
        }
