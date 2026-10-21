# ⚡ TrackPad Precision Pro — macOS Edition

[![macOS](https://img.shields.io/badge/macOS-10.14_Mojave_→_26.x+-blue?logo=apple&logoColor=white)](https://apple.com)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?logo=python&logoColor=white)](https://python.org)
[![UI](https://img.shields.io/badge/UI-CustomTkinter_v6.0-6366f1)](https://github.com/TomSchimansky/CustomTkinter)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-3.2_Pro-purple.svg)]()

> **The ultimate trackpad precision engine and palm mitigation shield for MacBook and Apple Magic Trackpad.**  
> Combines private hardware-level Multitouch framework bindings, online machine learning anomaly detection, kinematic smoothing, and custom acceleration curves in a sleek, native dark macOS interface.

---

## 🌟 Highlights & Key Capabilities

- **🎛 Multitouch Surface & Zone Exclusion Studio**  
  Real-time normalized contact matrix visualization with pressure/size ellipses, velocity vectors, and one-click palm rejection masks (`Left Palm`, `Right Palm`, `Bottom Strip`, `Both Corners`). Includes an interactive brush mode to paint or erase exclusion zones.

- **⚡ Advanced Kinematic Smoothing & Anti-Jitter Deadzone**  
  Eliminates micro-tremors, handshakes, and desk vibrations when holding the cursor stationary (configurable `0.0` to `6.0 px`). Prevents sudden cursor teleports with hardware jump rejection filtering.

- **🎯 Switchable Ballistics & Acceleration Curves**  
  - **macOS Ballistic**: Standard Apple velocity curve.  
  - **Linear 1:1**: Raw, proportional movement for competitive gaming and 3D navigation.  
  - **Precision CAD**: Micro-dampened motion for sub-pixel accuracy in Figma, Blender, and CAD.  
  - **Hyper Dynamic**: Aggressive acceleration multiplier for ultra-wide and multi-display setups.

- **🧠 ML Touch Guardian (AI Palm & Accidental Tap Shield)**  
  An autonomous online statistical learning model that continuously evaluates contact duration, ellipse eccentricity ($major / minor$), contact surface area, path tortuosity (wandering ratio), and edge proximity. Highlights suspicious zones as a live 20×10 red heatmap and blocks accidental taps before they trigger mouse clicks.

- **🛠 Deep macOS System Integration**  
  Direct, safe integration with `defaults` for:
  - Momentum Inertia Scrolling toggle
  - Natural vs Traditional Scroll Direction toggle
  - Hardware Tap-to-Click gesture
  - Force Touch Haptic Click Force (`Light`, `Medium`, `Firm`)
  - Axis routing: Invert X/Y or lock either axis for straight horizontal/vertical drawing lines
  - Tap-to-click debounce filter (prevents phantom double-clicks)
  - Oversized contact rejection (instantly discards wrists and resting palms)

- **📊 Live Telemetry & Event Stream**  
  Six real-time metric tiles tracking smooth moves, blocked jumps, filtered jitters, ML tap mitigations, blocked zones, and session uptime alongside a live event ticker console.

- **🚀 1-Click Profile Presets**  
  Instantly switch between pre-tuned profiles:
  - **⚡ Everyday Balanced** (0.30 smoothing, 100px jump, 1.2px deadzone, 1.0× gain)
  - **🎯 Precision CAD & Art** (0.16 smoothing, 55px jump, 2.4px deadzone, 0.55× gain)
  - **🛡 Anti-Jitter Palm Shield** (0.35 smoothing, 85px jump, 3.0px deadzone, ML filter active, corner zones active)
  - **🏎 Hyper Speed & FPS** (0.50 smoothing, 260px jump, 0.8px deadzone, 1:1 linear curve, 1.8× gain)

---

## 🏗 Modular Architecture

```
mousefixer/
├── src/
│   ├── config.py             # Global themes, colors, and profile presets
│   ├── core/
│   │   ├── engine.py         # CursorEngine (smoothing, ballistics, deadzones, axis locks)
│   │   ├── multitouch.py     # MultitouchSupport private framework ctypes wrapper
│   │   ├── listener.py       # pynput & Quartz CGEvent bridge
│   │   └── preferences.py    # macOS system defaults backup & safe restoration
│   ├── ml/
│   │   ├── features.py       # Kinematic trajectory & contact geometry feature extraction
│   │   └── classifier.py     # Multi-variate Bayesian Anomaly Detector & ML Touch Guardian
│   ├── zones/
│   │   └── manager.py        # Spatial 20x10 exclusion grid, palm presets & routing
│   └── ui/
│       ├── theme.py          # CustomTkinter dark theme configuration & fonts
│       ├── components/
│       │   ├── visualizer.py # Interactive touch surface canvas & heatmap
│       │   └── telemetry.py  # Live stats tiles and event ticker
│       ├── tabs/
│       │   ├── surface_tab.py    # Touch Surface & Zone Exclusion Studio
│       │   ├── precision_tab.py  # Smoothing, deadzone, ballistics, sensitivity meter
│       │   ├── ml_tab.py         # Advanced ML Touch Guardian controls
│       │   └── advanced_tab.py   # macOS system tweaks, corner actions, axes
│       └── app.py            # Main Application Window with CTkTabview & layout
├── assets/
│   └── logo.py               # Vector-rendered high-DPI modern trackpad logo
├── main.py                   # Clean entry point with compatibility patch
├── requirements.txt
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- macOS 10.14 Mojave up to macOS 26.x+
- Python 3.12 or newer
- Built-in Apple Multitouch Trackpad, Magic Trackpad, or external mouse

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/DinethChanuka/Macbook-TrackPad-Preciision-Pro.git
   cd Macbook-TrackPad-Preciision-Pro
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the application:**
   ```bash
   python main.py
   ```

---

## 🔒 Required macOS Permissions

To monitor multitouch contacts and post smoothed cursor events, macOS requires two permissions:

1. **Accessibility**:
   - Open **System Settings** → **Privacy & Security** → **Accessibility**
   - Toggle **Terminal**, **iTerm**, or **Python** to **ON**.
2. **Input Monitoring**:
   - Open **System Settings** → **Privacy & Security** → **Input Monitoring**
   - Toggle **Terminal**, **iTerm**, or **Python** to **ON**.

*(The app includes a direct button in the footer to open Privacy Settings instantly).*

---

## ⌨️ Controls & Usage

| Action | Control |
|---|---|
| **Activate Engine** | Click `▶ Activate` in the top header bar |
| **Stop Engine** | Click `■ Stop` (Restores all original system preferences cleanly) |
| **Paint Exclusion Zone** | Go to **Surface & Zones** tab → Click `✏ Paint Zones` → Left-click & drag on the canvas |
| **Erase Exclusion Zone** | Right-click & drag or Option-click & drag on painted red cells |
| **1-Click Palm Presets** | Click `Left Palm`, `Right Palm`, `Bottom Strip`, or `Both Corners` |
| **Switch Ballistics** | Go to **Precision & Motion** tab → Select `macOS Ballistic`, `Linear 1:1`, `Precision CAD`, or `Hyper Dynamic` |
| **Adjust Anti-Jitter** | Move the `Anti-Jitter Micro-Tremor Deadzone` slider (recommended `1.0` - `2.5 px`) |
| **Export/Import ML Profile** | Go to **ML Guardian** tab → Click `Export Model (JSON)` or `Import Model (JSON)` |

---

## 🛡 Teardown Safety & Restoration

When the app is stopped or closed, all system modifications made to `com.apple.AppleMultitouchTrackpad` are automatically restored to their exact pre-launch backup state via `atexit` hooks.

---

## 📄 License

Distributed under the MIT License. Developed with precision by **[Dineth Chanuka](https://github.com/DinethChanuka)**.
