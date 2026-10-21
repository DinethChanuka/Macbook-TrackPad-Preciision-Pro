"""
Theme initialization and font management for CustomTkinter.
"""

import customtkinter as ctk
from src.config import COLORS

def init_theme():
    """Initializes the CustomTkinter dark theme and appearance mode."""
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

def get_font(size: int = 12, weight: str = "normal", mono: bool = False) -> ctk.CTkFont:
    family = "Menlo" if mono else "Helvetica Neue"
    return ctk.CTkFont(family=family, size=size, weight=weight)
