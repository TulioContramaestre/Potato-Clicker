import ctypes
import sys
from ctypes import wintypes

_MUTEX_NAME = "PotatoClicker-SingleInstance"
_WINDOW_TITLE = "PotatoClicker"
_SW_RESTORE = 9
_ERROR_ALREADY_EXISTS = 183

_mutex_handle = None


def acquire_or_focus_existing() -> bool:
    """Return True if this is the only instance, False if another is running."""
    global _mutex_handle
    if sys.platform != "win32":
        return True

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    user32 = ctypes.WinDLL("user32", use_last_error=True)

    kernel32.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel32.CreateMutexW.restype = wintypes.HANDLE
    kernel32.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel32.CloseHandle.restype = wintypes.BOOL
    user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
    user32.FindWindowW.restype = wintypes.HWND
    user32.ShowWindow.argtypes = [wintypes.HWND, ctypes.c_int]
    user32.ShowWindow.restype = wintypes.BOOL
    user32.SetForegroundWindow.argtypes = [wintypes.HWND]
    user32.SetForegroundWindow.restype = wintypes.BOOL

    handle = kernel32.CreateMutexW(None, False, _MUTEX_NAME)
    if ctypes.get_last_error() == _ERROR_ALREADY_EXISTS:
        kernel32.CloseHandle(handle)
        hwnd = user32.FindWindowW(None, _WINDOW_TITLE)
        if hwnd:
            user32.ShowWindow(hwnd, _SW_RESTORE)
            user32.SetForegroundWindow(hwnd)
        return False

    _mutex_handle = handle
    return True
