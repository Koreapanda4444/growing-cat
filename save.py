import json
import os
import hmac
import hashlib

from save_key_store import get_or_create_hmac_key

_LEGACY_SAVE_HMAC_KEY = b"growing-cat-save-file"
_SIG_FIELD = "_sig"


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

SAVE_FILE = "save.json"

def is_first_run():
    return not os.path.exists(SAVE_FILE)

def save_game(data):
    try:
        if isinstance(data, dict):
            payload = _strip_sig(data)
            signed = dict(payload)
            signed[_SIG_FIELD] = _compute_sig(payload)
        else:
            signed = data

        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(signed, f, ensure_ascii=False, indent=2)
        return True
    except (OSError, IOError, TypeError, ValueError) as e:
        print(f"저장 실패: {e}")
        return False

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            return None

        if _SIG_FIELD not in data:
            return data

        sig = data.get(_SIG_FIELD)
        if not isinstance(sig, str):
            return None

        payload = _strip_sig(data)
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

        print("무결성 오류: save.json이 수정되었거나 손상되었습니다.")
        return None
    except (OSError, IOError, json.JSONDecodeError) as e:
        print(f"로드 실패: {e}")
        return None

def reset_save():
    try:
        if os.path.exists(SAVE_FILE):
            os.remove(SAVE_FILE)
        return True
    except (OSError, IOError) as e:
        print(f"초기화 실패: {e}")
        return False
