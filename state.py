import random

MORNING = "morning"
NIGHT = "night"

DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"

PERSONALITY_ENERGETIC = "energetic"
PERSONALITY_CALM = "calm"
PERSONALITY_LAZY = "lazy"

MINIGAME_KEYS = ("jump", "memory", "footsteps", "laser")

DIFFICULTY_PROFILE = {
    DIFFICULTY_EASY: {
        "label": "쉬움",
        "stat_pressure": 0.70,
        "stat_recovery": 1.30,
        "day_coin": 9,
        "minigame_coin": 1.25,
        "shop_price": 0.85,
        "evolution_cost": 0.85,
    },
    DIFFICULTY_NORMAL: {
        "label": "보통",
        "stat_pressure": 1.00,
        "stat_recovery": 1.00,
        "day_coin": 6,
        "minigame_coin": 1.00,
        "shop_price": 1.00,
        "evolution_cost": 1.00,
    },
    DIFFICULTY_HARD: {
        "label": "어려움",
        "stat_pressure": 1.35,
        "stat_recovery": 0.80,
        "day_coin": 4,
        "minigame_coin": 0.80,
        "shop_price": 1.20,
        "evolution_cost": 1.25,
    },
}

MINIGAME_DIFFICULTY_PROFILE = {
    DIFFICULTY_EASY: {
        "jump": {
            "base_speed": 3.4,
            "speed_step": 0.7,
            "spawn_delay": 110,
            "spawn_delay_floor": 65,
            "spawn_delay_step": 4,
            "min_spawn_meters": 26,
            "max_spawn_meters": 50,
            "spawn_meter_floor": 18,
            "spawn_meter_step": 1,
        },
        "memory": {
            "preview_ms": 4200,
            "time_limit_ms": 40000,
            "mismatch_ms": 850,
            "reward_base": 90,
            "fail_penalty": 8,
        },
        "footsteps": {
            "start_len": 4,
            "target_round": 3,
            "sequence_growth": 0,
            "show_on_s": 0.65,
            "show_off_s": 0.22,
            "max_fails": 3,
        },
        "laser": {
            "time_limit": 38.0,
            "target_score": 410,
            "base_radius": 34,
            "min_radius": 20,
            "base_speed": 260.0,
            "max_speed": 650.0,
            "combo_grace": 1.8,
            "miss_penalty": 2,
        },
    },
    DIFFICULTY_NORMAL: {
        "jump": {
            "base_speed": 4.0,
            "speed_step": 1.0,
            "spawn_delay": 90,
            "spawn_delay_floor": 50,
            "spawn_delay_step": 5,
            "min_spawn_meters": 20,
            "max_spawn_meters": 40,
            "spawn_meter_floor": 14,
            "spawn_meter_step": 1,
        },
        "memory": {
            "preview_ms": 3000,
            "time_limit_ms": 30000,
            "mismatch_ms": 700,
            "reward_base": 80,
            "fail_penalty": 10,
        },
        "footsteps": {
            "start_len": 5,
            "target_round": 3,
            "sequence_growth": 1,
            "show_on_s": 0.50,
            "show_off_s": 0.15,
            "max_fails": 2,
        },
        "laser": {
            "time_limit": 32.0,
            "target_score": 480,
            "base_radius": 30,
            "min_radius": 18,
            "base_speed": 320.0,
            "max_speed": 720.0,
            "combo_grace": 1.5,
            "miss_penalty": 4,
        },
    },
    DIFFICULTY_HARD: {
        "jump": {
            "base_speed": 4.7,
            "speed_step": 1.25,
            "spawn_delay": 76,
            "spawn_delay_floor": 40,
            "spawn_delay_step": 6,
            "min_spawn_meters": 16,
            "max_spawn_meters": 32,
            "spawn_meter_floor": 10,
            "spawn_meter_step": 2,
        },
        "memory": {
            "preview_ms": 2400,
            "time_limit_ms": 24000,
            "mismatch_ms": 550,
            "reward_base": 75,
            "fail_penalty": 12,
        },
        "footsteps": {
            "start_len": 6,
            "target_round": 4,
            "sequence_growth": 1,
            "show_on_s": 0.38,
            "show_off_s": 0.10,
            "max_fails": 1,
        },
        "laser": {
            "time_limit": 27.0,
            "target_score": 580,
            "base_radius": 26,
            "min_radius": 16,
            "base_speed": 380.0,
            "max_speed": 820.0,
            "combo_grace": 1.15,
            "miss_penalty": 8,
        },
    },
}

PERSONALITY_PROFILE = {
    PERSONALITY_ENERGETIC: {
        "label": "활발함",
        "description": "항상 밝고 행복해해!",
        "happiness_recovery": 1.20,
        "tiredness_increase": 1.15,
        "coin_bonus": 1.10,
    },
    PERSONALITY_CALM: {
        "label": "차분함",
        "description": "천천히 생각하는 냥이",
        "hunger_increase": 0.80,
        "tiredness_recovery": 1.20,
        "coin_bonus": 1.00,
    },
    PERSONALITY_LAZY: {
        "label": "냥냥함",
        "description": "쉬고 싶어하는 냥이",
        "cleanliness_decrease": 0.80,
        "tiredness_increase": 0.85,
        "coin_bonus": 1.00,
    },
}


def normalize_difficulty(difficulty: str | None) -> str:
    value = str(difficulty or DIFFICULTY_NORMAL).strip().lower()
    if value not in DIFFICULTY_PROFILE:
        return DIFFICULTY_NORMAL
    return value


def normalize_personality(personality: str | None) -> str:
    value = str(personality or PERSONALITY_ENERGETIC).strip().lower()
    if value not in PERSONALITY_PROFILE:
        return PERSONALITY_ENERGETIC
    return value


def get_difficulty_profile(difficulty: str | None) -> dict:
    return DIFFICULTY_PROFILE[normalize_difficulty(difficulty)]


def get_minigame_profile(difficulty: str | None, minigame_id: str | None = None) -> dict:
    profile = MINIGAME_DIFFICULTY_PROFILE[normalize_difficulty(difficulty)]
    if minigame_id is None:
        return profile
    if minigame_id in profile:
        return profile[minigame_id]
    normal_profile = MINIGAME_DIFFICULTY_PROFILE[DIFFICULTY_NORMAL]
    return normal_profile[minigame_id] if minigame_id in normal_profile else {}


def get_difficulty_label(difficulty: str | None) -> str:
    return get_difficulty_profile(difficulty)["label"]


def get_personality_profile(personality: str | None) -> dict:
    return PERSONALITY_PROFILE[normalize_personality(personality)]


def get_personality_label(personality: str | None) -> str:
    return get_personality_profile(personality)["label"]


def new_minigame_usage() -> dict[str, bool]:
    return {key: False for key in MINIGAME_KEYS}


def normalize_minigame_usage(value) -> dict[str, bool]:
    usage = new_minigame_usage()
    if isinstance(value, dict):
        for key in MINIGAME_KEYS:
            usage[key] = bool(value.get(key, False))
    return usage


class GameState:
    def __init__(self, difficulty: str = DIFFICULTY_NORMAL, personality: str = PERSONALITY_ENERGETIC):
        self.difficulty = normalize_difficulty(difficulty)
        self.personality = normalize_personality(personality)
        self.day = 1
        self.time_phase = MORNING
        self.money = 0
        self.minigame_used = new_minigame_usage()

    def advance_time(self):
        if self.time_phase == MORNING:
            self.time_phase = NIGHT
            return NIGHT
        else:
            self.time_phase = MORNING
            self.day += 1
            return MORNING

MAX_STAT = 100


def clamp(value):
    return max(0, min(value, MAX_STAT))


def rand_range(rng: tuple[int, int]) -> int:
    return random.randint(rng[0], rng[1])


def scaled_range(rng, difficulty: str | None, kind: str) -> tuple[int, int]:
    profile = get_difficulty_profile(difficulty)
    multiplier = profile["stat_pressure"] if kind == "pressure" else profile["stat_recovery"]
    low = int(round(rng[0] * multiplier))
    high = int(round(rng[1] * multiplier))
    low = max(1, low)
    high = max(low, high)
    return (low, high)


def scale_coin(amount: int, difficulty: str | None, source: str = "minigame") -> int:
    try:
        amount_int = int(amount)
    except (TypeError, ValueError):
        amount_int = 0
    amount_int = max(0, amount_int)

    profile = get_difficulty_profile(difficulty)
    key = "day_coin" if source == "day" else "minigame_coin"
    factor = profile[key]

    if source == "day":
        return amount_int if amount_int else int(profile["day_coin"])
    return max(0, int(round(amount_int * factor)))


def get_day_coin_reward(difficulty: str | None) -> int:
    return int(get_difficulty_profile(difficulty)["day_coin"])


def get_shop_price(base_price: int, difficulty: str | None) -> int:
    profile = get_difficulty_profile(difficulty)
    return max(1, int(round(int(base_price) * profile["shop_price"])))


def get_evolution_cost(base_cost: int, difficulty: str | None) -> int:
    profile = get_difficulty_profile(difficulty)
    return max(1, int(round(int(base_cost) * profile["evolution_cost"])))

NIGHT_HUNGER_INC = (16, 24)
NIGHT_TIREDNESS_INC = (8, 16)
NIGHT_HAPPINESS_DEC = (8, 15)
NIGHT_CLEANLINESS_DEC = (8, 18)

MORNING_HUNGER_INC = (10, 16)
MORNING_TIREDNESS_DEC = (10, 16)
MORNING_HAPPINESS_INC = (8, 16)
MORNING_CLEANLINESS_DEC = (6, 14)

FREE_FEED_HUNGER_DEC = (18, 28)
FREE_FEED_HAPPINESS_INC = (6, 12)

FREE_PLAY_HAPPINESS_INC = (16, 24)
FREE_PLAY_TIREDNESS_INC = (10, 16)
FREE_PLAY_HUNGER_INC = (8, 14)
FREE_PLAY_CLEANLINESS_DEC = (8, 14)

CLEAN_CLEANLINESS_INC = (20, 32)
CLEAN_HAPPINESS_DEC = (12, 20)

SLEEP_TIREDNESS_DEC = (22, 34)
SLEEP_HAPPINESS_INC = (8, 16)

DEATH_HUNGER_THRESHOLD = 100
DEATH_TIREDNESS_THRESHOLD = 100

RUNAWAY_HAPPINESS_THRESHOLD = 0
RUNAWAY_CLEANLINESS_THRESHOLD = 0
