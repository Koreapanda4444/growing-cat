import random
from copy import deepcopy

import state
from items import ITEM_INFO


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

EVENTS.update({
    "rain": {"title": "갑작스러운 빗소리", "kind": "negative", "text": ("갑작스러운 빗소리에 고양이가 놀랐습니다.", "어떻게 안심시켜 줄까요?"), "choices": (
        {"label": "창문을 닫고 곁에 있기", "stats": {"happiness": -2}, "friendship": 2, "message": "빗소리는 잦아들고 고양이도 진정했습니다."},
        {"label": "젖은 발을 정돈해 주기", "stats": {"cleanliness": -3, "tiredness": 2}, "friendship": 1, "message": "젖은 발을 닦으며 함께 시간을 보냈습니다."},
        {"label": "조용히 기다려 보기", "stats": {"happiness": -4, "tiredness": -2}, "message": "잠시 놀랐지만 조용히 쉬었습니다."},
    )},
    "spill": {"title": "기울어진 물컵", "kind": "negative", "text": ("고양이가 물컵을 살짝 건드렸습니다.", "바닥에 작은 물웅덩이가 생겼습니다."), "choices": (
        {"label": "직접 닦고 달래 주기", "stats": {"cleanliness": -3, "tiredness": 3}, "friendship": 2, "message": "고양이를 달래고 물기를 닦았습니다."},
        {"label": "청소용품으로 빠르게 정리", "coins": -4, "stats": {"cleanliness": -1}, "message": "작은 비용을 들여 금방 정리했습니다."},
        {"label": "고양이가 진정할 때까지 기다리기", "stats": {"cleanliness": -5, "happiness": -2}, "message": "잠시 기다린 뒤 조심히 정리했습니다."},
    )},
    "stretch": {"title": "나른한 오후", "kind": "neutral", "text": ("고양이가 길게 기지개를 켰습니다.", "오늘은 서두를 일이 없어 보입니다."), "choices": (
        {"label": "가볍게 몸 풀기", "stats": {"happiness": 2, "tiredness": 1}, "message": "가볍게 움직이며 시간을 보냈습니다."},
        {"label": "그 자리에서 조금 쉬기", "stats": {"tiredness": -2, "hunger": 1}, "message": "편안하게 쉬니 조금 출출해졌습니다."},
        {"label": "평소처럼 하루 보내기", "message": "별일 없이 평온한 시간을 보냈습니다."},
    )},
})
for event_id, kind in (("sunbeam", "positive"), ("box", "positive"), ("window", "neutral")):
    EVENTS[event_id]["kind"] = kind
KIND_LABELS = {"positive": "좋은 일", "negative": "작은 소동", "neutral": "평범한 일"}
HISTORY_LIMIT = 12
STAT_KEYS = ("hunger", "tiredness", "happiness", "cleanliness")


def _int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError, OverflowError):
        return default


def new_data():
    return {"day": 0, "event": None, "status": "none", "choice": None, "result": None, "completed": 0, "history": []}


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
            data["choice"] = max(0, min(len(EVENTS[event_id]["choices"]) - 1, _int(value.get("choice", 0))))
            result = value.get("result")
            data["result"] = deepcopy(result) if isinstance(result, dict) else {}
    history = value.get("history")
    if isinstance(history, list):
        for entry in history[-HISTORY_LIMIT:]:
            if not isinstance(entry, dict) or not isinstance(entry.get("event"), str) or entry["event"] not in EVENTS:
                continue
            if _int(entry.get("day")) > 0 and isinstance(entry.get("result"), dict):
                data["history"].append(deepcopy(entry))
    data["completed"] = max(len(data["history"]), _int(value.get("completed", 0)))
    if data["status"] == "resolved" and not any(entry["day"] == data["day"] and entry["event"] == event_id for entry in data["history"]):
        data["history"].append({"day": data["day"], "event": event_id, "choice": data["choice"], "result": deepcopy(data["result"])})
        data["history"] = data["history"][-HISTORY_LIMIT:]
        data["completed"] += 1
    return data


def roll_for_day(data, day, cat):
    data = normalize(data)
    if data["day"] >= day:
        return data
    weights = [2 if event["kind"] == "negative" else 3 for event in EVENTS.values()]
    event_id = random.choices(list(EVENTS), weights=weights, k=1)[0] if random.random() < EVENT_CHANCE else None
    return {**data, "day": day, "event": event_id, "status": "pending" if event_id else "none", "choice": None, "result": None}


def preview_choice(event_id, choice, cat, game_state, inventory):
    event = EVENTS.get(event_id)
    if event is None or type(choice) is not int or not 0 <= choice < len(event["choices"]):
        return None
    effect = event["choices"][choice]
    changes = {}
    profile = state.get_difficulty_profile(game_state.difficulty)
    for stat, delta in effect.get("stats", {}).items():
        before = getattr(cat, stat)
        beneficial = delta < 0 if stat in ("hunger", "tiredness") else delta > 0
        factor = max(0.90, min(1.10, profile["stat_recovery"])) if beneficial else max(0.85, min(1.10, profile["stat_pressure"]))
        magnitude = min(8 if beneficial else 5, max(1, round(abs(delta) * factor))) if delta else 0
        delta = magnitude * (1 if delta > 0 else -1)
        after = state.clamp(before + delta)
        if stat in ("hunger", "tiredness") and delta > 0:
            after = min(max(before, 95), after)
        elif stat in ("happiness", "cleanliness") and delta < 0:
            after = max(min(before, 5), after)
        changes[stat] = after - before
    raw_coins = effect.get("coins", 0)
    coin_factor = max(0.90, min(1.10, profile["minigame_coin"]))
    amount = min(8 if raw_coins > 0 else 5, round(abs(raw_coins) * coin_factor)) * (1 if raw_coins > 0 else -1)
    coins = max(0, game_state.money + amount) - game_state.money
    friendship = state.normalize_friendship(cat.friendship + max(-4, min(4, effect.get("friendship", 0)))) - cat.friendship
    return {"stats": changes, "coins": coins, "friendship": friendship,
            "items": {item: 1 for item, count in effect.get("items", {}).items() if item in ITEM_INFO and count > 0}, "message": effect["message"],
            "available": raw_coins >= 0 or game_state.money >= abs(amount)}


def resolve(data, cat, game_state, inventory, choice=0):
    data = normalize(data)
    if data["status"] != "pending" or data["day"] != game_state.day or cat.check_game_over():
        return data, False
    result = preview_choice(data["event"], choice, cat, game_state, inventory)
    if result is None or not result["available"]:
        return data, False
    for stat, delta in result["stats"].items():
        setattr(cat, stat, getattr(cat, stat) + delta)
    game_state.money += result["coins"]
    cat.change_friendship(result["friendship"])
    for item, count in result["items"].items():
        inventory[item] = inventory.get(item, 0) + count
    data.update(status="resolved", choice=choice, result=result)
    return normalize(data), True
