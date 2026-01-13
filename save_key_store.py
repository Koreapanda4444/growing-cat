import base64
import os
from pathlib import Path
from typing import Optional


_APP_DIR = Path(os.getenv("APPDATA") or str(Path.home())) / "growing-cat"
_KEY_FILE = _APP_DIR / "save_hmac_key.bin"


def _is_windows() -> bool:
    return os.name == "nt"


_CRYPTPROTECT_UI_FORBIDDEN = 0x1


def _entropy() -> bytes:
    return b"growing-cat.save.hmac.v1"


def _dpapi_protect(data: bytes) -> bytes:
    if not _is_windows():
        raise OSError("DPAPI is only available on Windows")

    import ctypes
    import ctypes.wintypes

    class _DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", ctypes.wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_byte)),
        ]

    def _bytes_to_blob(buf_bytes: bytes) -> _DATA_BLOB:
        buf = ctypes.create_string_buffer(buf_bytes)
        return _DATA_BLOB(len(buf_bytes), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))

    def _blob_to_bytes(blob: _DATA_BLOB) -> bytes:
        if not blob.pbData:
            return b""
        try:
            return ctypes.string_at(blob.pbData, blob.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(blob.pbData)

    in_blob = _bytes_to_blob(data)
    out_blob = _DATA_BLOB()
    entropy_blob = _bytes_to_blob(_entropy())

    ok = ctypes.windll.crypt32.CryptProtectData(
        ctypes.byref(in_blob),
        None,
        ctypes.byref(entropy_blob),
        None,
        None,
        _CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise OSError("CryptProtectData failed")

    return _blob_to_bytes(out_blob)


def _dpapi_unprotect(data: bytes) -> bytes:
    if not _is_windows():
        raise OSError("DPAPI is only available on Windows")

    import ctypes
    import ctypes.wintypes

    class _DATA_BLOB(ctypes.Structure):
        _fields_ = [
            ("cbData", ctypes.wintypes.DWORD),
            ("pbData", ctypes.POINTER(ctypes.c_byte)),
        ]

    def _bytes_to_blob(buf_bytes: bytes) -> _DATA_BLOB:
        buf = ctypes.create_string_buffer(buf_bytes)
        return _DATA_BLOB(len(buf_bytes), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))

    def _blob_to_bytes(blob: _DATA_BLOB) -> bytes:
        if not blob.pbData:
            return b""
        try:
            return ctypes.string_at(blob.pbData, blob.cbData)
        finally:
            ctypes.windll.kernel32.LocalFree(blob.pbData)

    in_blob = _bytes_to_blob(data)
    out_blob = _DATA_BLOB()
    entropy_blob = _bytes_to_blob(_entropy())

    ok = ctypes.windll.crypt32.CryptUnprotectData(
        ctypes.byref(in_blob),
        None,
        ctypes.byref(entropy_blob),
        None,
        None,
        _CRYPTPROTECT_UI_FORBIDDEN,
        ctypes.byref(out_blob),
    )
    if not ok:
        raise OSError("CryptUnprotectData failed")

    return _blob_to_bytes(out_blob)


def _env_key() -> Optional[bytes]:
    v = os.getenv("GROWING_CAT_SAVE_KEY")
    if not v:
        return None
    v = v.strip()
    if not v:
        return None
    return v.encode("utf-8")


def load_hmac_key() -> Optional[bytes]:
    env = _env_key()
    if env:
        return env

    if not _KEY_FILE.exists():
        return None

    blob = _KEY_FILE.read_bytes()
    if _is_windows():
        return _dpapi_unprotect(blob)
    return blob


def get_or_create_hmac_key(*, num_bytes: int = 32) -> bytes:
    existing = load_hmac_key()
    if existing:
        return existing

    key = os.urandom(num_bytes)
    _APP_DIR.mkdir(parents=True, exist_ok=True)
    if _is_windows():
        blob = _dpapi_protect(key)
    else:
        blob = key
        try:
            os.chmod(_KEY_FILE, 0o600)
        except Exception:
            pass

    _KEY_FILE.write_bytes(blob)
    return key


def export_key_base64() -> str:
    return base64.b64encode(get_or_create_hmac_key()).decode("ascii")
