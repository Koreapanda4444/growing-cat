GAME_NAMES = {"jump": "장애물 피하기", "memory": "메모리 게임", "footsteps": "고양이 따라가기", "laser": "레이저 포인터"}
BEST_METRICS = {"jump": ("distance", "obstacles"), "memory": ("score", "pairs"),
                "footsteps": ("score", "rounds", "sequence_length"), "laser": ("score", "best_combo", "accuracy")}
METRICS = ("distance", "obstacles", "score", "pairs", "errors", "elapsed_ms", "rounds", "sequence_length", "best_combo", "hits", "misses", "accuracy")


def _int(value):
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def new_records():
    return {key: {"plays": 0, "wins": 0, "best": {}, "last": {}, "last_difficulty": "normal"} for key in GAME_NAMES}


def normalize(value):
    data = new_records()
    if not isinstance(value, dict):
        return data
    for key, entry in data.items():
        saved = value.get(key)
        if not isinstance(saved, dict):
            continue
        entry["plays"] = _int(saved.get("plays"))
        entry["wins"] = min(entry["plays"], _int(saved.get("wins")))
        for field in ("best", "last"):
            source = saved.get(field)
            if isinstance(source, dict):
                entry[field] = {metric: _int(source[metric]) for metric in METRICS if metric in source}
        if isinstance(saved.get("last"), dict):
            entry["last"]["won"] = bool(saved["last"].get("won"))
        difficulty = saved.get("last_difficulty")
        entry["last_difficulty"] = difficulty if difficulty in ("easy", "normal", "hard") else "normal"
    return data


def record_result(value, game_id, result, won, difficulty="normal"):
    data = normalize(value)
    if game_id not in GAME_NAMES or not isinstance(result, dict) or result.get("cancelled"):
        return data
    entry = data[game_id]
    entry["plays"] += 1
    entry["wins"] += int(bool(won))
    entry["last"] = {key: _int(result[key]) for key in METRICS if key in result}
    entry["last"]["won"] = bool(won)
    entry["last_difficulty"] = difficulty
    for metric in BEST_METRICS[game_id]:
        if metric in result:
            entry["best"][metric] = max(entry["best"].get(metric, 0), _int(result[metric]))
    elapsed = _int(result.get("elapsed_ms"))
    if game_id == "memory" and won and elapsed:
        previous = entry["best"].get("elapsed_ms")
        entry["best"]["elapsed_ms"] = min(previous, elapsed) if previous else elapsed
    return data


def best_summary(game_id, entry):
    best = entry["best"]
    if game_id == "jump":
        return f"최고 거리 {best.get('distance', 0)}m / 장애물 {best.get('obstacles', 0)}개"
    if game_id == "memory":
        seconds = best.get("elapsed_ms", 0) / 1000
        return f"최고 {best.get('score', 0)}점 / 최단 {seconds:g}초" if seconds else f"최고 {best.get('score', 0)}점 / 완주 기록 없음"
    if game_id == "footsteps":
        return f"최고 {best.get('rounds', 0)}라운드 / 기억 길이 {best.get('sequence_length', 0)}"
    return f"최고 {best.get('score', 0)}점 / 콤보 {best.get('best_combo', 0)}"
