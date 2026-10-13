import random
from copy import deepcopy

import state


EVENT_CHANCE = 0.35
EVENTS = {
    "sunbeam": {"title": "따뜻한 햇살", "text": ("창가에 따뜻한 햇살이 내려앉았습니다.", "고양이가 조용히 창가를 바라봅니다."),
                "effects": {"tiredness": -3, "happiness": 2}},
    "box": {"title": "익숙한 상자", "text": ("고양이가 빈 상자에 관심을 보입니다.", "작은 공간이 마음에 드는 것 같습니다."),
            "effects": {"happiness": 4, "tiredness": 1}},
    "window": {"title": "창밖 구경", "text": ("창밖에서 새가 가볍게 날아갑니다.", "고양이의 귀가 쫑긋해졌습니다."),
               "effects": {"happiness": 3}},
}


def new_data():
    return {"day": 0, "event": None, "status": "none", "choice": None, "result": None}


def normalize(value):
    data = new_data()
    if not isinstance(value, dict):
        return data
    try:
        data["day"] = max(0, int(value.get("day", 0)))
    except (TypeError, ValueError, OverflowError):
        pass
    event_id = value.get("event")
    if isinstance(event_id, str) and event_id in EVENTS:
        data["event"] = event_id
        data["status"] = "resolved" if value.get("status") == "resolved" else "pending"
        if data["status"] == "resolved":
            data["choice"] = value.get("choice", 0)
            result = value.get("result")
            data["result"] = deepcopy(result) if isinstance(result, dict) else {}
    return data


def roll_for_day(data, day, cat):
    data = normalize(data)
    if data["day"] >= day:
        return data
    event_id = random.choice(list(EVENTS)) if random.random() < EVENT_CHANCE else None
    return {**new_data(), "day": day, "event": event_id, "status": "pending" if event_id else "none"}


def resolve(data, cat, game_state, inventory, choice=0):
    data = normalize(data)
    if data["status"] != "pending" or data["day"] != game_state.day or cat.check_game_over() or choice != 0:
        return data, False
    changes = {}
    for stat, delta in EVENTS[data["event"]]["effects"].items():
        before = getattr(cat, stat)
        after = state.clamp(before + delta)
        if stat in ("hunger", "tiredness") and delta > 0:
            after = min(99, after)
        elif stat in ("happiness", "cleanliness") and delta < 0:
            after = max(1, after)
        setattr(cat, stat, after)
        changes[stat] = getattr(cat, stat) - before
    data.update(status="resolved", choice=0, result={"stats": changes, "coins": 0, "friendship": 0, "items": {}})
    return data, True
