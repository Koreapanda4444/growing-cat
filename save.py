import json
import os

SAVE_FILE = "save.json"

def is_first_run():
    return not os.path.exists(SAVE_FILE)

def save_game(data):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_game():
    if not os.path.exists(SAVE_FILE):
        return None
    with open(SAVE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def reset_save():
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
