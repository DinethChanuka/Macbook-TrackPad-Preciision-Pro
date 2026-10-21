"""
Advanced Online Learning Classifier & Anomaly Detector: ML Touch Guardian.
Combines spatial decay heatmaps with a multi-variate online logistic classifier.
"""

import math, threading, json
from typing import Dict, List, Optional, Tuple
from src.ml.features import ContactTrajectory

class MLTouchGuardian:
    GRID_W = 20
    GRID_H = 10

    def __init__(self):
        self._lock = threading.Lock()
        n = self.GRID_W * self.GRID_H

        # Spatial Heatmap matrices
        self._counts: List[float] = [0.0] * n
        self._sus_sum: List[float] = [0.0] * n
        self._scores: List[float] = [0.0] * n

        # Active trajectories
        self._trajectories: Dict[int, ContactTrajectory] = {}

        # Multi-variate model weights:
        # bias, duration_weight, size_weight, aspect_weight, wander_weight, edge_weight
        self.weights = {
            "bias": -1.2,
            "brief_stationary": 2.5,   # Short duration with low displacement
            "oversized": 2.2,          # Large contact area (palms)
            "elongated": 1.6,          # High aspect ratio (edge of hand)
            "wandering": 1.4,          # High tortuosity / micro-shakes
            "edge_proximity": 1.8,     # Touches very close to bottom/side borders
        }

        # Runtime controls
        self.filtering: bool = False
        self.freeze_learning: bool = False
        self.threshold: float = 0.55
        self.decay_factor: float = 0.994
        self.total_samples: int = 0
        self.blocked_samples: int = 0
        self.learning_rate: float = 0.05

    def _idx(self, nx: float, ny: float) -> int:
        gx = min(int(nx * self.GRID_W), self.GRID_W - 1)
        gy = min(int(ny * self.GRID_H), self.GRID_H - 1)
        return max(0, gy) * self.GRID_W + max(0, gx)

    def on_contact_begin(self, tid: int, x: float, y: float, size: float, major: float, minor: float, ts: float):
        with self._lock:
            self._trajectories[tid] = ContactTrajectory(tid, x, y, size, major, minor, ts)

    def on_contact_move(self, tid: int, x: float, y: float, ts: float):
        with self._lock:
            traj = self._trajectories.get(tid)
            if traj:
                traj.add_point(x, y, ts)

    def on_contact_end(self, tid: int, ts: float) -> Tuple[str, float]:
        with self._lock:
            traj = self._trajectories.pop(tid, None)

        if not traj:
            return "UNKNOWN", 0.0

        traj.add_point(traj.current_x, traj.current_y, ts)
        feats = traj.extract_features()

        # Compute multi-feature suspicion index
        suspicion = self._evaluate_features(feats)

        # Classify touch intent
        classification = self._classify_intent(feats, suspicion)

        # Online learning update
        if not self.freeze_learning:
            self._update_online_model(feats, suspicion)

        return classification, suspicion

    def _evaluate_features(self, f: Dict[str, float]) -> float:
        z = self.weights["bias"]

        # Feature 1: Brief stationary tap (accidental resting contact)
        if f["duration"] < 0.12 and f["net_displacement"] < 0.018:
            z += self.weights["brief_stationary"] * (1.0 - (f["duration"] / 0.12))
        elif f["duration"] < 0.20 and f["net_displacement"] < 0.025:
            z += self.weights["brief_stationary"] * 0.5

        # Feature 2: Oversized contact
        if f["size"] > 0.45:
            z += self.weights["oversized"] * min(2.0, (f["size"] - 0.45) / 0.25)

        # Feature 3: Elongated ellipse
        if f["aspect_ratio"] > 1.8:
            z += self.weights["elongated"] * min(1.5, (f["aspect_ratio"] - 1.8) / 1.5)

        # Feature 4: Wandering tremor / high tortuosity without net travel
        if f["tortuosity"] > 3.0 and f["net_displacement"] < 0.03:
            z += self.weights["wandering"] * min(1.5, f["tortuosity"] / 4.0)

        # Feature 5: Edge proximity (resting thumbs near bottom or sides)
        if f["edge_distance"] < 0.08:
            z += self.weights["edge_proximity"] * (1.0 - (f["edge_distance"] / 0.08))

        # Sigmoid probability
        prob = 1.0 / (1.0 + math.exp(-max(-8.0, min(8.0, z))))
        return prob

    def _classify_intent(self, f: Dict[str, float], sus: float) -> str:
        if sus > 0.75:
            if f["size"] > 0.50:
                return "RESTING_PALM"
            elif f["edge_distance"] < 0.08:
                return "THUMB_EDGE_TAP"
            else:
                return "ACCIDENTAL_TAP"
        elif sus > self.threshold:
            return "SUSPICIOUS_TOUCH"
        else:
            if f["net_displacement"] > 0.04:
                return "INTENDED_POINTER"
            else:
                return "INTENDED_TAP"

    def _update_online_model(self, f: Dict[str, float], sus: float):
        with self._lock:
            idx = self._idx(f["x"], f["y"])

            # Spatial decay
            for i in range(len(self._counts)):
                self._counts[i] *= self.decay_factor
                self._sus_sum[i] *= self.decay_factor

            self._counts[idx] += 1.0
            self._sus_sum[idx] += sus

            c = self._counts[idx]
            if c > 0.2:
                self._scores[idx] = min(1.0, self._sus_sum[idx] / c)

            self.total_samples += 1
            if sus > self.threshold:
                self.blocked_samples += 1

    def should_suppress_initial(self, nx: float, ny: float) -> bool:
        """Instant query on touch contact begin."""
        if not self.filtering:
            return False
        with self._lock:
            return self._scores[self._idx(nx, ny)] > self.threshold

    def get_spatial_heatmap(self) -> List[float]:
        with self._lock:
            return list(self._scores)

    def reset(self):
        with self._lock:
            n = self.GRID_W * self.GRID_H
            self._counts = [0.0] * n
            self._sus_sum = [0.0] * n
            self._scores = [0.0] * n
            self._trajectories.clear()
            self.total_samples = 0
            self.blocked_samples = 0

    def export_weights_json(self) -> str:
        with self._lock:
            data = {
                "weights": self.weights,
                "threshold": self.threshold,
                "decay_factor": self.decay_factor,
                "total_samples": self.total_samples,
                "spatial_scores": self._scores,
            }
            return json.dumps(data, indent=2)

    def import_weights_json(self, json_str: str) -> bool:
        try:
            data = json.loads(json_str)
            with self._lock:
                self.weights.update(data.get("weights", {}))
                self.threshold = data.get("threshold", self.threshold)
                self.decay_factor = data.get("decay_factor", self.decay_factor)
                if "spatial_scores" in data and len(data["spatial_scores"]) == len(self._scores):
                    self._scores = list(data["spatial_scores"])
            return True
        except Exception:
            return False
