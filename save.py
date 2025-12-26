import json
import os
import hmac
import hashlib
from pathlib import Path
import base64
import zlib

from save_key_store import get_or_create_hmac_key

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
    except Exception:
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
    except Exception:
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

def save_game(data):
    try:
        _ensure_data_dir()
        if isinstance(data, dict):
            payload = _strip_sig(data)
            if payload is None:
                return False
            signed = {
                _VERSION_FIELD: _FORMAT_VERSION,
                _PAYLOAD_FIELD: _encode_payload(payload),
                _SIG_FIELD: _compute_sig(payload),
            }
        else:
            signed = data

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(signed, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, IOError, TypeError, ValueError) as e:
        print(f"저장 실패: {e}")
        return False

def load_game():
    path = SAVE_FILE
    if not os.path.exists(path):
        if os.path.exists(_LEGACY_APPDATA_JSON):
            path = _LEGACY_APPDATA_JSON
        elif os.path.exists(_LEGACY_CWD_JSON):
            path = _LEGACY_CWD_JSON
        else:
            return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None

        if _PAYLOAD_FIELD in data and _SIG_FIELD in data:
            sig = data.get(_SIG_FIELD)
            if not isinstance(sig, str):
                return None
            payload = _decode_payload(data.get(_PAYLOAD_FIELD))
            if payload is None or not _is_valid_payload(payload):
                return None

            expected = _compute_sig(payload)
            if hmac.compare_digest(sig, expected):
                return payload

            legacy_expected = _compute_sig_with_key(payload, _LEGACY_SAVE_HMAC_KEY)
            if hmac.compare_digest(sig, legacy_expected):
                try:
                    save_game(payload)
                except Exception:
                    pass
                return payload

            print("무결성 오류: save.dat이 수정되었거나 손상되었습니다.")
            return None

        if _SIG_FIELD not in data:
            if not _is_valid_payload(data):
                return None
            try:
                save_game(data)
            except Exception:
                pass
            return data

        sig = data.get(_SIG_FIELD)
        if not isinstance(sig, str):
            return None

        payload = _strip_sig(data)
        if payload is None:
            return None
        expected = _compute_sig(payload)
        if hmac.compare_digest(sig, expected):
            if not _is_valid_payload(payload):
                return None
            try:
                save_game(payload)
            except Exception:
                pass
            return payload

        legacy_expected = _compute_sig_with_key(payload, _LEGACY_SAVE_HMAC_KEY)
        if hmac.compare_digest(sig, legacy_expected):
            try:
                save_game(payload)
            except Exception:
                pass
            if not _is_valid_payload(payload):
                return None
            return payload

        print("무결성 오류: save.json이 수정되었거나 손상되었습니다.")
        return None
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
