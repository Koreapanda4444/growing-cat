import random

import state


LABELS = {"care": "돌봄 활동", "minigame": "미니게임 완료", "feed": "먹이 주기",
          "play": "놀아주기", "clean": "씻기", "sleep": "잠자기", "pet": "고양이와 인사", "buy": "상점 구매"}
REWARDS = {key: 2 if key in ("care", "minigame") else 1 for key in LABELS}

CARE_ACTIVITIES = ("feed", "play", "clean", "sleep", "special")


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def new_data():
    return {"day": 0, "goals": [], "streak": 0, "best_streak": 0, "last_completed_day": 0,
            "total_completed": 0, "bonus_claimed": False}


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
            data["goals"].append({"id": key, "target": target, "progress": progress,
                                  "reward": max(1, min(2, _int(goal.get("reward"), REWARDS[key]))),
                                  "claimed": progress >= target and bool(goal.get("claimed", False))})
            seen.add(key)
    data["streak"] = max(0, _int(value.get("streak")))
    data["best_streak"] = max(data["streak"], _int(value.get("best_streak")))
    data["last_completed_day"] = max(0, min(data["day"], _int(value.get("last_completed_day"))))
    data["total_completed"] = max(0, _int(value.get("total_completed")))
    data["bonus_claimed"] = (len(data["goals"]) == 3 and all(goal["claimed"] for goal in data["goals"])
                             and bool(value.get("bonus_claimed", False)))
    if data["last_completed_day"] == 0 or data["last_completed_day"] < data["day"] - 1:
        data["streak"] = 0
    return data


def for_day(value, game_state):
    data = normalize(value)
    if data["day"] == game_state.day and len(data["goals"]) == 3:
        return data
    candidates = ["feed", "play", "clean", "sleep", "pet"]
    if game_state.money >= state.get_shop_price(25, game_state.difficulty) * 2:
        candidates.append("buy")
    extra = random.choice(candidates)
    if data["last_completed_day"] < game_state.day - 1:
        data["streak"] = 0
    return normalize({**data, "day": game_state.day, "bonus_claimed": False, "goals": [
        {"id": "care", "target": 4, "progress": 0},
        {"id": "minigame", "target": 2 if game_state.day % 3 == 0 else 1, "progress": 0},
        {"id": extra, "target": 2 if extra == "pet" else 1, "progress": 0},
    ]})


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



def claim(value, index, game_state, inventory):
    data = normalize(value)
    if data["day"] != game_state.day or type(index) is not int or not 0 <= index < len(data["goals"]):
        return data, None
    goal = data["goals"][index]
    if goal["progress"] < goal["target"] or goal["claimed"]:
        return data, None
    goal["claimed"] = True
    coins = goal["reward"]
    bonus = 0
    items = {}
    finished = all(entry["claimed"] for entry in data["goals"])
    if finished and not data["bonus_claimed"]:
        if data["last_completed_day"] != game_state.day:
            data["streak"] = data["streak"] + 1 if data["last_completed_day"] == game_state.day - 1 else 1
            data["best_streak"] = max(data["best_streak"], data["streak"])
            data["last_completed_day"] = game_state.day
            data["total_completed"] += 1
            bonus = 1 + min(2, data["streak"] // 3)
            if data["streak"] % 7 == 0:
                items["사료"] = 1
        data["bonus_claimed"] = True
    game_state.money += coins + bonus
    for item, count in items.items():
        inventory[item] = inventory.get(item, 0) + count
    return data, {"coins": coins + bonus, "bonus": bonus, "items": items, "completed_today": finished}
