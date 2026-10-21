"""
Low-Level Binding to Apple's Private MultitouchSupport.framework.
Captures raw normalized touch matrices, ellipse geometry, pressure, and velocities.
"""

import ctypes, ctypes.util
from typing import Optional, List, Callable

_MT_PATH = "/System/Library/PrivateFrameworks/MultitouchSupport.framework/MultitouchSupport"

class MTPoint(ctypes.Structure):
    _fields_ = [("x", ctypes.c_float), ("y", ctypes.c_float)]

class MTVector(ctypes.Structure):
    _fields_ = [("position", MTPoint), ("velocity", MTPoint)]

class MTFinger(ctypes.Structure):
    _fields_ = [
        ("frame",      ctypes.c_int),
        ("timestamp",  ctypes.c_double),
        ("identifier", ctypes.c_int),
        ("state",      ctypes.c_int),      # 1=begin, 2=hover, 4=move, 7=end
        ("unknown1",   ctypes.c_float),
        ("unknown2",   ctypes.c_float),
        ("normalized", MTVector),
        ("size",       ctypes.c_float),
        ("unknown3",   ctypes.c_int),
        ("angle",      ctypes.c_float),
        ("majorAxis",  ctypes.c_float),
        ("minorAxis",  ctypes.c_float),
        ("unknown4",   MTVector),
        ("unknown5",   ctypes.c_int),
        ("unknown6",   ctypes.c_float),
        ("zTotal",     ctypes.c_float),
    ]

MTCallbackType = ctypes.CFUNCTYPE(
    None,
    ctypes.c_void_p,
    ctypes.POINTER(MTFinger),
    ctypes.c_int,
    ctypes.c_double,
    ctypes.c_int,
)

class MultitouchDeviceManager:
    def __init__(self):
        self._mt_lib = self._load_mt()
        self._cf_lib = self._load_cf()
        self._active_devices: List[ctypes.c_void_p] = []
        self._cb_ref: Optional[MTCallbackType] = None

    def _load_mt(self):
        try:
            lib = ctypes.CDLL(_MT_PATH)
            lib.MTDeviceCreateList.restype = ctypes.c_void_p
            lib.MTDeviceStart.argtypes = [ctypes.c_void_p, ctypes.c_int]
            lib.MTDeviceStop.argtypes = [ctypes.c_void_p]
            lib.MTDeviceIsBuiltIn.argtypes = [ctypes.c_void_p]
            lib.MTDeviceIsBuiltIn.restype = ctypes.c_bool
            lib.MTRegisterContactFrameCallback.argtypes = [ctypes.c_void_p, MTCallbackType]
            lib.MTUnregisterContactFrameCallback.argtypes = [ctypes.c_void_p, MTCallbackType]
            return lib
        except Exception as e:
            print(f"[WARN] MultitouchSupport unavailable: {e}")
            return None

    def _load_cf(self):
        try:
            path = ctypes.util.find_library("CoreFoundation")
            lib = ctypes.CDLL(path)
            lib.CFArrayGetCount.restype = ctypes.c_long
            lib.CFArrayGetCount.argtypes = [ctypes.c_void_p]
            lib.CFArrayGetValueAtIndex.restype = ctypes.c_void_p
            lib.CFArrayGetValueAtIndex.argtypes = [ctypes.c_void_p, ctypes.c_long]
            return lib
        except Exception:
            return None

    @property
    def is_available(self) -> bool:
        return self._mt_lib is not None and self._cf_lib is not None

    def start_listening(self, python_callback: Callable) -> bool:
        if not self.is_available:
            return False

        try:
            dev_list = self._mt_lib.MTDeviceCreateList()
            if not dev_list:
                return False

            count = self._cf_lib.CFArrayGetCount(dev_list)
            if count == 0:
                return False

            self._cb_ref = MTCallbackType(python_callback)
            registered = 0

            for i in range(count):
                dev = self._cf_lib.CFArrayGetValueAtIndex(dev_list, i)
                if not dev:
                    continue
                try:
                    if not self._mt_lib.MTDeviceIsBuiltIn(dev):
                        continue
                except Exception:
                    pass

                self._mt_lib.MTRegisterContactFrameCallback(dev, self._cb_ref)
                self._mt_lib.MTDeviceStart(dev, 0)
                self._active_devices.append(dev)
                registered += 1

            return registered > 0
        except Exception as e:
            print(f"[Multitouch start error] {e}")
            return False

    def stop_listening(self):
        for dev in self._active_devices:
            try:
                self._mt_lib.MTDeviceStop(dev)
                if self._cb_ref:
                    self._mt_lib.MTUnregisterContactFrameCallback(dev, self._cb_ref)
            except Exception:
                pass
        self._active_devices.clear()
        self._cb_ref = None
