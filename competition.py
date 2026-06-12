from __future__ import annotations

import random
from copy import deepcopy

import evolution
import state as game_state


INTERVAL_DAYS = 3
HISTORY_LIMIT = 30
GRADE_ORDER = ("S", "A", "B", "C")
GRADE_RANK = {grade: index for index, grade in enumerate(GRADE_ORDER)}


COMPETITIONS = (
    {
        "id": "cute",
        "name": "귀여움 대회",
        "desc": "행복과 청결이 높을수록 유리합니다.",
        "fee": 30,
        "rewards": {"S": 180, "A": 120, "B": 70, "C": 25},
    },
    {
        "id": "clean",
        "name": "깔끔함 대회",
        "desc": "청결 관리가 핵심입니다.",
        "fee": 35,
        "rewards": {"S": 200, "A": 130, "B": 75, "C": 25},
    },
    {
        "id": "food",
        "name": "먹방 대회",
        "desc": "배고픔을 낮게 유지하고 음식 보유량이 있으면 유리합니다.",
        "fee": 40,
        "rewards": {"S": 220, "A": 145, "B": 85, "C": 30},
    },
    {
        "id": "hunt",
        "name": "사냥 대회",
        "desc": "미니게임과 놀기 컨디션이 중요합니다.",
        "fee": 45,
        "rewards": {"S": 250, "A": 165, "B": 95, "C": 35},
    },
    {
        "id": "stamina",
        "name": "체력 대회",
        "desc": "피로와 배고픔을 낮게 유지해야 합니다.",
        "fee": 45,
        "rewards": {"S": 240, "A": 160, "B": 95, "C": 35},
    },
    {
        "id": "luck",
        "name": "행운 대회",
        "desc": "기본 컨디션에 행운 점수가 더해집니다.",
        "fee": 25,
        "rewards": {"S": 210, "A": 140, "B": 80, "C": 30},
    },
)

COMPETITION_BY_ID = {comp["id"]: comp for comp in COMPETITIONS}

DIFFICULTY_THRESHOLDS = {
    game_state.DIFFICULTY_EASY: {"S": 78, "A": 62, "B": 45},
    game_state.DIFFICULTY_NORMAL: {"S": 86, "A": 70, "B": 52},
    game_state.DIFFICULTY_HARD: {"S": 94, "A": 78, "B": 60},
}


def new_competition_data() -> dict:
    return {
        "last_entered_day": 0,
        "trophies": {},
        "history": [],
    }


def normalize_competition_data(value) -> dict:
    data = new_competition_data()
    if not isinstance(value, dict):
        return data

    try:
        data["last_entered_day"] = max(0, int(value.get("last_entered_day", 0)))
    except (TypeError, ValueError):
        pass

    trophies = value.get("trophies", {})
    if isinstance(trophies, dict):
        for comp_id, trophy in trophies.items():
            if comp_id not in COMPETITION_BY_ID or not isinstance(trophy, dict):
                continue
            best_grade = str(trophy.get("best_grade", "")).upper()
            if best_grade not in GRADE_ORDER:
                best_grade = ""
            try:
                count = max(0, int(trophy.get("count", 0)))
            except (TypeError, ValueError):
                count = 0
            data["trophies"][comp_id] = {
                "best_grade": best_grade,
                "count": count,
            }

    history = value.get("history", [])
    if isinstance(history, list):
        for entry in history[-HISTORY_LIMIT:]:
            normalized = _normalize_history_entry(entry)
            if normalized is not None:
                data["history"].append(normalized)

    return data


def _normalize_history_entry(entry) -> dict | None:
    if not isinstance(entry, dict):
        return None
    comp_id = str(entry.get("id", ""))
    if comp_id not in COMPETITION_BY_ID:
        return None
    grade = str(entry.get("grade", "")).upper()
    if grade not in GRADE_ORDER:
        return None
    try:
        day = max(1, int(entry.get("day", 1)))
        score = max(0, int(entry.get("score", 0)))
        reward = max(0, int(entry.get("reward", 0)))
    except (TypeError, ValueError):
        return None
    return {
        "day": day,
        "id": comp_id,
        "name": COMPETITION_BY_ID[comp_id]["name"],
        "grade": grade,
        "score": score,
        "reward": reward,
    }


def copy_for_save(data) -> dict:
    return deepcopy(normalize_competition_data(data))


def days_until_event(day: int) -> int:
    try:
        day = max(1, int(day))
    except (TypeError, ValueError):
        day = 1
    remainder = day % INTERVAL_DAYS
    return 0 if remainder == 0 else INTERVAL_DAYS - remainder


def is_event_day(day: int) -> bool:
    return days_until_event(day) == 0


def event_day_for(day: int) -> int:
    try:
        day = max(1, int(day))
    except (TypeError, ValueError):
        day = 1
    return day + days_until_event(day)


def competition_for_day(day: int) -> dict:
    event_day = event_day_for(day)
    cycle = max(0, event_day // INTERVAL_DAYS - 1)
    return COMPETITIONS[cycle % len(COMPETITIONS)]


def entry_fee(comp: dict, difficulty: str | None) -> int:
    return game_state.get_shop_price(int(comp.get("fee", 0)), difficulty)


def reward_for_grade(comp: dict, grade: str, difficulty: str | None) -> int:
    rewards = comp.get("rewards", {})
    raw = int(rewards.get(grade, 0))
    return game_state.scale_coin(raw, difficulty, source="minigame")


def grade_for_score(score: int, difficulty: str | None) -> str:
    thresholds = DIFFICULTY_THRESHOLDS[game_state.normalize_difficulty(difficulty)]
    if score >= thresholds["S"]:
        return "S"
    if score >= thresholds["A"]:
        return "A"
    if score >= thresholds["B"]:
        return "B"
    return "C"


def estimate_score(comp_id: str, cat, state, inventory) -> int:
    return _score(comp_id, cat, state, inventory, random_bonus=0)


def roll_score(comp_id: str, cat, state, inventory) -> int:
    bonus = 0
    if comp_id == "luck":
        bonus = random.randint(0, 24)
    return _score(comp_id, cat, state, inventory, random_bonus=bonus)


def _score(comp_id: str, cat, state, inventory, random_bonus: int = 0) -> int:
    stats = _stats(cat)
    stage = getattr(cat, "stage", "")
    minigame_count = sum(1 for used in getattr(state, "minigame_used", {}).values() if used)
    food_count = _inventory_count(inventory, ("사료", "생선", "츄르", "고기"))
    toy_count = _inventory_count(inventory, ("강아지풀", "낚싯대", "실"))

    hunger_ok = 100 - stats["hunger"]
    rested = 100 - stats["tiredness"]
    clean = stats["cleanliness"]
    happy = stats["happiness"]

    stage_bonus = _stage_bonus(stage)

    if comp_id == "cute":
        score = happy * 0.45 + clean * 0.35 + hunger_ok * 0.10 + rested * 0.10 + stage_bonus
    elif comp_id == "clean":
        score = clean * 0.68 + happy * 0.14 + rested * 0.10 + hunger_ok * 0.08
    elif comp_id == "food":
        score = hunger_ok * 0.58 + happy * 0.16 + clean * 0.10 + min(food_count, 8) * 4.0
    elif comp_id == "hunt":
        score = happy * 0.26 + rested * 0.22 + hunger_ok * 0.14 + minigame_count * 12 + toy_count * 2.5 + stage_bonus
    elif comp_id == "stamina":
        score = rested * 0.46 + hunger_ok * 0.25 + clean * 0.14 + happy * 0.15 + stage_bonus * 0.5
    elif comp_id == "luck":
        avg = (happy + clean + hunger_ok + rested) / 4
        score = avg * 0.72 + min(food_count + toy_count, 10) * 2.0 + random_bonus
    else:
        score = (happy + clean + hunger_ok + rested) / 4

    return max(0, min(120, int(round(score))))


def _stats(cat) -> dict[str, float]:
    return {
        "hunger": _clamped_float(getattr(cat, "hunger", 50)),
        "tiredness": _clamped_float(getattr(cat, "tiredness", 50)),
        "happiness": _clamped_float(getattr(cat, "happiness", 50)),
        "cleanliness": _clamped_float(getattr(cat, "cleanliness", 50)),
    }


def _clamped_float(value) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        number = 50.0
    return max(0.0, min(100.0, number))


def _inventory_count(inventory, keys: tuple[str, ...]) -> int:
    if not isinstance(inventory, dict):
        return 0
    total = 0
    for key in keys:
        try:
            total += max(0, int(inventory.get(key, 0)))
        except (TypeError, ValueError):
            pass
    return total


def _stage_bonus(stage: str) -> int:
    if stage == evolution.DINO:
        return 12
    if stage == evolution.LION:
        return 10
    if stage == evolution.ADULT:
        return 5
    return 0


def entered_today(data, day: int) -> bool:
    normalized = normalize_competition_data(data)
    try:
        day = int(day)
    except (TypeError, ValueError):
        day = 1
    return normalized.get("last_entered_day") == day


def record_result(data, *, day: int, comp: dict, grade: str, score: int, reward: int) -> dict:
    normalized = normalize_competition_data(data)
    comp_id = comp["id"]
    normalized["last_entered_day"] = max(1, int(day))

    trophy = normalized["trophies"].get(comp_id, {"best_grade": "", "count": 0})
    trophy["count"] = max(0, int(trophy.get("count", 0))) + 1
    best_grade = str(trophy.get("best_grade", "")).upper()
    if best_grade not in GRADE_RANK or GRADE_RANK[grade] < GRADE_RANK[best_grade]:
        trophy["best_grade"] = grade
    normalized["trophies"][comp_id] = trophy

    normalized["history"].append({
        "day": max(1, int(day)),
        "id": comp_id,
        "name": comp["name"],
        "grade": grade,
        "score": max(0, int(score)),
        "reward": max(0, int(reward)),
    })
    normalized["history"] = normalized["history"][-HISTORY_LIMIT:]
    return normalized


def latest_today_result(data, day: int) -> dict | None:
    normalized = normalize_competition_data(data)
    for entry in reversed(normalized.get("history", [])):
        if entry.get("day") == day:
            return entry
    return None
