import ctypes


def fake_error(message: str) -> None:
    ctypes.windll.user32.MessageBoxW(0, message, "Fatal Error", 0x00001000)
