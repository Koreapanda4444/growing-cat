import json
import os
import hmac
import hashlib
from pathlib import Path
import base64
import binascii
import zlib

from save_key_store import get_or_create_hmac_key, load_hmac_key

_LEGACY_SAVE_HMAC_KEY = b"growing-cat-save-file"
_SIG_FIELD = "_sig"
_PAYLOAD_FIELD = "p"
_VERSION_FIELD = "v"
_FORMAT_VERSION = 2


def _canonical_dumps(data):
    return json.dumps(
        data,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _compute_sig(payload):
    msg = _canonical_dumps(payload).encode("utf-8")
    key = get_or_create_hmac_key()
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def _compute_existing_sig(payload):
    key = load_hmac_key()
    if not key:
        return None
    return _compute_sig_with_key(payload, key)


def _compute_sig_with_key(payload, key: bytes):
    msg = _canonical_dumps(payload).encode("utf-8")
    return hmac.new(key, msg, hashlib.sha256).hexdigest()


def _strip_sig(data):
    if not isinstance(data, dict):
        return None
    return {k: v for k, v in data.items() if k != _SIG_FIELD}

_DATA_DIR = Path(os.getenv("APPDATA") or str(Path.home())) / "growing-cat"
SAVE_FILE = str(_DATA_DIR / "save.dat")
_LEGACY_APPDATA_JSON = str(_DATA_DIR / "save.json")
_LEGACY_CWD_JSON = "save.json"


def _ensure_data_dir():
    try:
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass


def _encode_payload(payload: dict) -> str:
    raw = _canonical_dumps(payload).encode("utf-8")
    comp = zlib.compress(raw, level=9)
    return base64.b64encode(comp).decode("ascii")


def _decode_payload(blob: str) -> dict | None:
    if not isinstance(blob, str) or not blob:
        return None
    try:
        comp = base64.b64decode(blob.encode("ascii"), validate=True)
        raw = zlib.decompress(comp)
        payload = json.loads(raw.decode("utf-8"))
        if isinstance(payload, dict):
            return payload
        return None
    except (binascii.Error, json.JSONDecodeError, UnicodeDecodeError, ValueError, zlib.error):
        return None


def _is_valid_payload(payload) -> bool:
    if not isinstance(payload, dict):
        return False

    cat = payload.get("cat")
    if not isinstance(cat, dict):
        return False
    if not isinstance(cat.get("name"), str) or not isinstance(cat.get("stage"), str):
        return False

    if "inventory" in payload and not isinstance(payload.get("inventory"), dict):
        return False
    if "minigame_used" in payload and not isinstance(payload.get("minigame_used"), dict):
        return False
    return True

def is_first_run():
    return (
        not os.path.exists(SAVE_FILE)
        and not os.path.exists(_LEGACY_APPDATA_JSON)
        and not os.path.exists(_LEGACY_CWD_JSON)
    )


def _select_save_path():
    if os.path.exists(SAVE_FILE):
        return SAVE_FILE
    if os.path.exists(_LEGACY_APPDATA_JSON):
        return _LEGACY_APPDATA_JSON
    if os.path.exists(_LEGACY_CWD_JSON):
        return _LEGACY_CWD_JSON
    return None


def _matches_existing_sig(payload, sig: str) -> bool:
    expected = _compute_existing_sig(payload)
    return expected is not None and hmac.compare_digest(sig, expected)


def _matches_legacy_sig(payload, sig: str) -> bool:
    legacy_expected = _compute_sig_with_key(payload, _LEGACY_SAVE_HMAC_KEY)
    return hmac.compare_digest(sig, legacy_expected)


def _migrate_payload(payload) -> None:
    save_game(payload)


def _write_json_atomic(path: str, data) -> None:
    target = Path(path)
    temp = target.with_name(f"{target.name}.tmp")
    try:
        with temp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp, target)
    except (OSError, TypeError, ValueError):
        try:
            temp.unlink()
        except OSError:
            pass
        raise


def save_game(data):
    try:
        _ensure_data_dir()
        if not isinstance(data, dict):
            return False

        payload = _strip_sig(data)
        if payload is None:
            return False
        signed = {
            _VERSION_FIELD: _FORMAT_VERSION,
            _PAYLOAD_FIELD: _encode_payload(payload),
            _SIG_FIELD: _compute_sig(payload),
        }

        _write_json_atomic(SAVE_FILE, signed)
        return True
    except (OSError, IOError, TypeError, ValueError) as e:
        print(f"저장 실패: {e}")
        return False


def _load_current_format(data):
    sig = data.get(_SIG_FIELD)
    if not isinstance(sig, str):
        return None

    payload = _decode_payload(data.get(_PAYLOAD_FIELD))
    if payload is None or not _is_valid_payload(payload):
        return None

    if _matches_existing_sig(payload, sig):
        return payload

    if _matches_legacy_sig(payload, sig):
        _migrate_payload(payload)
        return payload

    print("무결성 오류: save.dat이 수정되었거나 손상되었습니다.")
    return None


def _load_unsigned_legacy_format(data):
    if not _is_valid_payload(data):
        return None
    _migrate_payload(data)
    return data


def _load_signed_legacy_format(data):
    sig = data.get(_SIG_FIELD)
    if not isinstance(sig, str):
        return None

    payload = _strip_sig(data)
    if payload is None or not _is_valid_payload(payload):
        return None

    if _matches_existing_sig(payload, sig) or _matches_legacy_sig(payload, sig):
        _migrate_payload(payload)
        return payload

    print("무결성 오류: save.json이 수정되었거나 손상되었습니다.")
    return None


def load_game():
    path = _select_save_path()
    if path is None:
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None

        if _PAYLOAD_FIELD in data and _SIG_FIELD in data:
            return _load_current_format(data)

        if _SIG_FIELD not in data:
            return _load_unsigned_legacy_format(data)

        return _load_signed_legacy_format(data)
    except (OSError, IOError, json.JSONDecodeError) as e:
        print(f"로드 실패: {e}")
        return None

def reset_save():
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        if os.path.exists(_LEGACY_APPDATA_JSON):
            os.remove(_LEGACY_APPDATA_JSON)
        if os.path.exists(_LEGACY_CWD_JSON):
            os.remove(_LEGACY_CWD_JSON)
        return True
    except (OSError, IOError) as e:
        print(f"초기화 실패: {e}")
        return False
