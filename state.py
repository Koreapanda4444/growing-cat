import random

MORNING = "morning"
NIGHT = "night"

DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"

DIFFICULTY_PROFILE = {
    DIFFICULTY_EASY: {
        "label": "쉬움",
        "stat_pressure": 0.80,
        "stat_recovery": 1.20,
        "day_coin": 8,
        "minigame_coin": 1.20,
        "shop_price": 0.90,
        "evolution_cost": 0.90,
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
        "stat_pressure": 1.25,
        "stat_recovery": 0.90,
        "day_coin": 4,
        "minigame_coin": 0.85,
        "shop_price": 1.10,
        "evolution_cost": 1.15,
    },
}


def normalize_difficulty(difficulty: str | None) -> str:
    value = str(difficulty or DIFFICULTY_NORMAL).strip().lower()
    if value not in DIFFICULTY_PROFILE:
        return DIFFICULTY_NORMAL
    return value


def get_difficulty_profile(difficulty: str | None) -> dict:
    return DIFFICULTY_PROFILE[normalize_difficulty(difficulty)]


def get_difficulty_label(difficulty: str | None) -> str:
    return get_difficulty_profile(difficulty)["label"]


class GameState:
    def __init__(self, difficulty: str = DIFFICULTY_NORMAL):
        self.difficulty = normalize_difficulty(difficulty)
        self.day = 1
        self.time_phase = MORNING
        self.money = 0
        self.minigame_used = {"jump": False, "memory": False, "footsteps": False, "laser": False}

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

def rand_range(rng):

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
