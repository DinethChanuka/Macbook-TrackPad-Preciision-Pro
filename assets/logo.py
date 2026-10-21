"""
Vector Logo Generator for TrackPad Precision Pro.
Draws a high-DPI modern trackpad precision badge directly onto a Tkinter Canvas.
"""

import tkinter as tk

def draw_logo(canvas: tk.Canvas, cx: int, cy: int, size: int = 36):
    """Draws a sleek high-DPI cyber trackpad glyph."""
    r = size // 2
    canvas.delete("logo")

    # Trackpad outer rounded border
    x1, y1 = cx - r, cy - r + 3
    x2, y2 = cx + r, cy + r - 3
    canvas.create_rectangle(
        x1, y1, x2, y2,
        fill="#1e2538", outline="#6366f1", width=2, tags="logo"
    )

    # Top sensor notch
    canvas.create_line(
        cx - 6, y1 + 1, cx + 6, y1 + 1,
        fill="#818cf8", width=2, tags="logo"
    )

    # Precision target ring
    canvas.create_oval(
        cx - 5, cy - 5, cx + 5, cy + 5,
        fill="", outline="#0ea5e9", width=1.5, tags="logo"
    )

    # Center beam dot
    canvas.create_oval(
        cx - 2, cy - 2, cx + 2, cy + 2,
        fill="#34d399", outline="", tags="logo"
    )
