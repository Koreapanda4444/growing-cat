import random

import state


LABELS = {"care": "돌봄 활동", "minigame": "미니게임 완료", "feed": "먹이 주기",
          "play": "놀아주기", "clean": "씻기", "sleep": "잠자기", "pet": "고양이와 인사", "buy": "상점 구매"}
CARE_ACTIVITIES = ("feed", "play", "clean", "sleep", "special")


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def new_data():
    return {"day": 0, "goals": []}


def normalize(value):
    data = new_data()
    if not isinstance(value, dict):
        return data
    data["day"] = max(0, _int(value.get("day")))
    goals = value.get("goals")
    if isinstance(goals, list):
        seen = set()
        for goal in goals[:3]:
            if not isinstance(goal, dict):
                continue
            key = goal.get("id")
            if not isinstance(key, str) or key not in LABELS or key in seen:
                continue
            target = max(1, min(8, _int(goal.get("target"), 1)))
            progress = max(0, min(target, _int(goal.get("progress"))))
            data["goals"].append({"id": key, "target": target, "progress": progress})
            seen.add(key)
    return data


def for_day(value, game_state):
    data = normalize(value)
    if data["day"] == game_state.day and len(data["goals"]) == 3:
        return data
    candidates = ["feed", "play", "clean", "sleep", "pet"]
    if game_state.money >= state.get_shop_price(25, game_state.difficulty) * 2:
        candidates.append("buy")
    extra = random.choice(candidates)
    return {"day": game_state.day, "goals": [
        {"id": "care", "target": 4, "progress": 0},
        {"id": "minigame", "target": 2 if game_state.day % 3 == 0 else 1, "progress": 0},
        {"id": extra, "target": 2 if extra == "pet" else 1, "progress": 0},
    ]}


def record(value, activity):
    data = normalize(value)
    changed = False
    for goal in data["goals"]:
        if goal["id"] == activity or (goal["id"] == "care" and activity in CARE_ACTIVITIES):
            before = goal["progress"]
            goal["progress"] = min(goal["target"], before + 1)
            changed |= goal["progress"] != before
    return data, changed


def completed(value):
    data = normalize(value)
    return len(data["goals"]) == 3 and all(goal["progress"] >= goal["target"] for goal in data["goals"])
