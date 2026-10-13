import random
from copy import deepcopy

import state


EVENT_CHANCE = 0.35
EVENTS = {
    "sunbeam": {"title": "따뜻한 햇살", "text": ("창가에 따뜻한 햇살이 내려앉았습니다.", "고양이가 조용히 창가를 바라봅니다."), "choices": (
        {"label": "함께 햇살 쬐기", "stats": {"tiredness": -3, "happiness": 2}, "friendship": 2, "message": "따뜻한 자리에서 함께 쉬었습니다."},
        {"label": "햇살 속에서 가볍게 놀기", "stats": {"happiness": 5, "tiredness": 3}, "friendship": 3, "message": "고양이가 햇살을 따라 뛰었습니다."},
        {"label": "창가의 작은 동전 줍기", "coins": 4, "stats": {"tiredness": 2}, "message": "창가에서 잊었던 동전을 찾았습니다."},
    )},
    "box": {"title": "익숙한 상자", "text": ("고양이가 빈 상자에 관심을 보입니다.", "작은 공간이 마음에 드는 것 같습니다."), "choices": (
        {"label": "상자 안에서 놀아주기", "stats": {"happiness": 4, "tiredness": 1}, "friendship": 2, "message": "상자가 작은 놀이터가 되었습니다."},
        {"label": "상자에 남은 사료 챙기기", "items": {"사료": 1}, "friendship": 1, "message": "남겨둔 사료 한 봉지를 찾았습니다."},
        {"label": "상자를 깨끗하게 정리하기", "stats": {"cleanliness": 3}, "friendship": 1, "message": "주변을 깔끔하게 정리했습니다."},
    )},
    "window": {"title": "창밖 구경", "text": ("창밖에서 새가 가볍게 날아갑니다.", "고양이의 귀가 쫑긋해졌습니다."), "choices": (
        {"label": "함께 새 구경하기", "stats": {"happiness": 3}, "friendship": 2, "message": "함께 창밖을 바라보았습니다."},
        {"label": "창턱을 정돈하기", "stats": {"cleanliness": 3}, "friendship": 1, "message": "편히 앉을 자리를 마련했습니다."},
    )},
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


def preview_choice(event_id, choice, cat, game_state, inventory):
    event = EVENTS.get(event_id)
    if event is None or type(choice) is not int or not 0 <= choice < len(event["choices"]):
        return None
    effect = event["choices"][choice]
    changes = {}
    for stat, delta in effect.get("stats", {}).items():
        before = getattr(cat, stat)
        after = state.clamp(before + delta)
        if stat in ("hunger", "tiredness") and delta > 0:
            after = min(99, after)
        elif stat in ("happiness", "cleanliness") and delta < 0:
            after = max(1, after)
        changes[stat] = after - before
    coins = max(0, game_state.money + effect.get("coins", 0)) - game_state.money
    friendship = state.normalize_friendship(cat.friendship + effect.get("friendship", 0)) - cat.friendship
    return {"stats": changes, "coins": coins, "friendship": friendship,
            "items": dict(effect.get("items", {})), "message": effect["message"]}


def resolve(data, cat, game_state, inventory, choice=0):
    data = normalize(data)
    if data["status"] != "pending" or data["day"] != game_state.day or cat.check_game_over():
        return data, False
    result = preview_choice(data["event"], choice, cat, game_state, inventory)
    if result is None:
        return data, False
    for stat, delta in result["stats"].items():
        setattr(cat, stat, getattr(cat, stat) + delta)
    game_state.money += result["coins"]
    cat.change_friendship(result["friendship"])
    for item, count in result["items"].items():
        inventory[item] = inventory.get(item, 0) + count
    data.update(status="resolved", choice=choice, result=result)
    return data, True
