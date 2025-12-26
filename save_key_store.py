import base64
import ctypes
import ctypes.wintypes
import os
from pathlib import Path
from typing import Optional


_APP_DIR = Path(os.getenv("APPDATA") or str(Path.home())) / "growing-cat"
_KEY_FILE = _APP_DIR / "save_hmac_key.bin"


class _DATA_BLOB(ctypes.Structure):
    _fields_ = [
        ("cbData", ctypes.wintypes.DWORD),
        ("pbData", ctypes.POINTER(ctypes.c_byte)),
    ]


_CRYPTPROTECT_UI_FORBIDDEN = 0x1


def _bytes_to_blob(data: bytes) -> _DATA_BLOB:
    buf = ctypes.create_string_buffer(data)
    return _DATA_BLOB(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_byte)))


def _blob_to_bytes(blob: _DATA_BLOB) -> bytes:
    if not blob.pbData:
        return b""
    try:
        return ctypes.string_at(blob.pbData, blob.cbData)
    finally:
        ctypes.windll.kernel32.LocalFree(blob.pbData)


def _entropy() -> bytes:
    return b"growing-cat.save.hmac.v1"


def _dpapi_protect(data: bytes) -> bytes:
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
    raw = _dpapi_unprotect(blob)
    return raw


def get_or_create_hmac_key(*, num_bytes: int = 32) -> bytes:
    existing = load_hmac_key()
    if existing:
        return existing

    key = os.urandom(num_bytes)
    _APP_DIR.mkdir(parents=True, exist_ok=True)
    blob = _dpapi_protect(key)
    _KEY_FILE.write_bytes(blob)
    return key


def export_key_base64() -> str:
    return base64.b64encode(get_or_create_hmac_key()).decode("ascii")
