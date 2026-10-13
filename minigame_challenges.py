import state
import minigame_records


SKILLS = {
    "jump": ("장거리 달리기", {"easy": 150, "normal": 250, "hard": 350}, "강아지풀"),
    "memory": ("차분한 기억력", {"easy": 2, "normal": 1, "hard": 0}, "사료"),
    "footsteps": ("정확한 순서 기억", {"easy": 4, "normal": 7, "hard": 9}, "강아지풀"),
    "laser": ("정확한 연속 적중", {"easy": 3, "normal": 5, "hard": 7}, "사료"),
    "timing": ("완벽한 타이밍", {"easy": 2, "normal": 3, "hard": 4}, "실"),
}


def definitions(game_id, difficulty):
    difficulty = state.normalize_difficulty(difficulty)
    title, targets, item = SKILLS[game_id]
    target = targets[difficulty]
    description = {
        "jump": f"정상 종료한 플레이에서 {target}m 이상 달리기",
        "memory": f"실수 {target}회 이하로 메모리 게임 성공",
        "footsteps": f"실수 없이 길이 {target} 이상 기억하고 성공",
        "laser": f"콤보 {target} · 적중 {dict(easy=5, normal=7, hard=9)[difficulty]} · 정확도 {dict(easy=60, normal=70, hard=80)[difficulty]}%로 성공",
        "timing": f"완벽 판정 {target}회 이상으로 타이밍 게임 성공",
    }[game_id]
    return (
        {"id": game_id + "_first", "title": "첫 성공", "description": "게임을 한 번 성공하고 정상 종료하기", "coins": 10, "items": {}},
        {"id": game_id + "_skill", "title": title, "description": description, "coins": 15, "items": {item: 1}},
        {"id": game_id + "_challenge", "title": "도전 모드 완주", "description": "현재 난이도의 도전 목표를 모두 달성하기", "coins": 20, "items": {}},
    )


def new_data():
    return {goal["id"]: {"unlocked": False, "claimed": False, "day": 0}
            for key in minigame_records.GAME_NAMES for goal in definitions(key, "normal")}


def normalize(value):
    data = new_data()
    if not isinstance(value, dict):
        return data
    for key, entry in data.items():
        saved = value.get(key)
        if isinstance(saved, dict):
            entry["unlocked"] = bool(saved.get("unlocked"))
            entry["claimed"] = entry["unlocked"] and bool(saved.get("claimed"))
            entry["day"] = minigame_records._int(saved.get("day"))
    return data


def _skill_met(key, entry, difficulty):
    _, targets, _ = SKILLS[key]
    target = targets[difficulty]
    last = entry["last"]
    if key == "jump":
        return entry["best"].get("distance", 0) >= target
    if not last.get("won"):
        return False
    if key == "memory":
        return "errors" in last and last["errors"] <= target
    if key == "footsteps":
        return "errors" in last and last["errors"] == 0 and last.get("sequence_length", 0) >= target
    if key == "laser":
        hits, misses = last.get("hits", 0), last.get("misses", 0)
        min_hits = {"easy": 5, "normal": 7, "hard": 9}[difficulty]
        accuracy = {"easy": 60, "normal": 70, "hard": 80}[difficulty]
        return last.get("best_combo", 0) >= target and hits >= min_hits and hits * 100 >= accuracy * (hits + misses)
    return last.get("perfects", 0) >= target


def sync(value, records, difficulty, day):
    data = normalize(value)
    records = minigame_records.normalize(records)
    difficulty = state.normalize_difficulty(difficulty)
    for key, entry in records.items():
        conditions = (entry["wins"] > 0, _skill_met(key, entry, difficulty), entry["challenge_clears"].get(difficulty, False))
        for goal, met in zip(definitions(key, difficulty), conditions):
            if met and not data[goal["id"]]["unlocked"]:
                data[goal["id"]].update(unlocked=True, day=day)
    return data


def claim(value, goal_id, game_state, inventory):
    data = normalize(value)
    entry = data.get(goal_id)
    if entry is None or not entry["unlocked"] or entry["claimed"]:
        return data, None
    goal = next(goal for key in minigame_records.GAME_NAMES for goal in definitions(key, game_state.difficulty) if goal["id"] == goal_id)
    entry["claimed"] = True
    game_state.money += goal["coins"]
    for item, count in goal["items"].items():
        inventory[item] = inventory.get(item, 0) + count
    return data, {"coins": goal["coins"], "items": dict(goal["items"])}
