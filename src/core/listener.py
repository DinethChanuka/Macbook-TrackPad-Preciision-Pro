"""
Global Mouse Event Listener via pynput.
Intercepts hardware mouse events and routes coordinates through CursorEngine.
"""

from typing import Optional, Callable

try:
    from pynput import mouse as _pynput_mouse
    _PYNPUT_AVAILABLE = True
except ImportError:
    _PYNPUT_AVAILABLE = False

class GlobalMouseListener:
    def __init__(self):
        self._listener: Optional[_pynput_mouse.Listener] = None

    @property
    def is_available(self) -> bool:
        return _PYNPUT_AVAILABLE

    def start(self, on_move_callback: Callable[[float, float], None]) -> bool:
        if not self.is_available:
            return False

        try:
            self._listener = _pynput_mouse.Listener(on_move=on_move_callback)
            self._listener.start()
            return True
        except Exception as e:
            print(f"[GlobalMouseListener error] {e}")
            return False

    def stop(self):
        if self._listener:
            try:
                self._listener.stop()
            except Exception:
                pass
            self._listener = None
