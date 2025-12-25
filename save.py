import json
import os

SAVE_FILE = "save.json"

def is_first_run():
    return not os.path.exists(SAVE_FILE)

def save_game(data):
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
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
        return data if isinstance(data, dict) else None
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
