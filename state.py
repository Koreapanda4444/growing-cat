import random

MORNING = "morning"
NIGHT = "night"

DIFFICULTY_EASY = "easy"
DIFFICULTY_NORMAL = "normal"
DIFFICULTY_HARD = "hard"

PERSONALITY_ENERGETIC = "energetic"
PERSONALITY_CALM = "calm"
PERSONALITY_LAZY = "lazy"

CARE_LABELS = {"feed": "밥", "play": "놀기", "clean": "씻기", "sleep": "잠자기"}

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
        "preferred_action": "play",
        "care_modifiers": {"play": {"happiness_recovery": 1.30}},
        "care_lines": {
            "feed": ("밥 먹고 신나게 뛰겠다냥!", "에너지가 채워진다냥!"),
            "play": ("이 놀이가 제일 좋다냥!", "함께 뛰니까 더 신난다냥!"),
            "clean": ("깨끗한 발로 또 뛰겠다냥!", "씻을 때는 잠깐 얌전히 있겠다냥."),
            "sleep": ("꿈에서도 달릴 거다냥!", "잘 쉬고 다시 놀자냥!"),
        },
        "happiness_recovery": 1.20,
        "tiredness_increase": 1.15,
        "coin_bonus": 1.10,
    },
    PERSONALITY_CALM: {
        "label": "차분함",
        "description": "천천히 생각하는 냥이",
        "preferred_action": "clean",
        "care_modifiers": {"clean": {"cleanliness_decrease": 0.90}},
        "care_lines": {
            "feed": ("천천히 꼭꼭 먹겠다냥.", "조용한 식사 시간이 좋다냥."),
            "play": ("천천히 따라가도 재밌다냥.", "차분히 눈으로 쫓는 중이다냥."),
            "clean": ("털을 정돈하니 마음도 편하다냥.", "보송한 털이 제일 좋다냥."),
            "sleep": ("곁에서 조용히 쉬겠다냥.", "따뜻한 낮잠을 준비한다냥."),
        },
        "hunger_increase": 0.80,
        "tiredness_recovery": 1.20,
        "coin_bonus": 1.00,
    },
    PERSONALITY_LAZY: {
        "label": "냥냥함",
        "description": "쉬고 싶어하는 냥이",
        "preferred_action": "sleep",
        "care_modifiers": {"sleep": {"tiredness_recovery": 1.15}},
        "care_lines": {
            "feed": ("밥 먹고 누우면 딱 좋다냥.", "간식 시간에는 일어나겠다냥."),
            "play": ("누워서 잡아도 되냥?", "살짝만 움직여도 재밌다냥."),
            "clean": ("포근한 털로 눕겠다냥.", "씻었으니 이제 쉬고 싶다냥."),
            "sleep": ("이 시간이 제일 좋다냥.", "포근한 꿈을 꾸겠다냥."),
        },
        "cleanliness_decrease": 0.80,
        "tiredness_increase": 0.85,
        "coin_bonus": 1.00,
    },
}


MOOD_PROFILE = {
    "happy": {"label": "행복함", "color": (40, 130, 70), "lines": (
        "오늘은 모든 게 좋다냥!", "골골송을 불러주겠다냥.")},
    "calm": {"label": "평온함", "color": (70, 110, 150), "lines": (
        "편안하게 곁에 있겠다냥.", "지금처럼 천천히 지내자냥.")},
    "tired": {"label": "피곤함", "color": (100, 90, 160), "lines": (
        "눈꺼풀이 무겁다냥...", "잠깐 쉬었다 놀자냥.")},
    "hungry": {"label": "배고픔", "color": (170, 100, 40), "lines": (
        "밥그릇이 비어 있다냥.", "배고파서 힘이 안 난다냥.")},
    "uncomfortable": {"label": "불편함", "color": (160, 65, 65), "lines": (
        "털과 발바닥이 찝찝하다냥.", "깨끗하게 씻고 싶다냥.")},
    "lonely": {"label": "심심함", "color": (140, 85, 105), "lines": (
        "같이 놀아줄 수 있냥?", "오늘은 관심이 필요하다냥.")},
}


FRIENDSHIP_MAX = 1000
FRIENDSHIP_LEVELS = (
    (0, "낯선 사이"), (100, "익숙한 사이"), (300, "친구"), (600, "단짝"), (1000, "가족"),
)


def normalize_friendship(value):
    try:
        return max(0, min(FRIENDSHIP_MAX, int(value)))
    except (TypeError, ValueError, OverflowError):
        return 0


def friendship_progress(value):
    value = normalize_friendship(value)
    for index in range(len(FRIENDSHIP_LEVELS) - 1, -1, -1):
        start, label = FRIENDSHIP_LEVELS[index]
        if value < start:
            continue
        if index == len(FRIENDSHIP_LEVELS) - 1:
            return label, FRIENDSHIP_MAX, 1.0
        target = FRIENDSHIP_LEVELS[index + 1][0]
        return label, target, (value - start) / (target - start)


SPECIAL_CARE = {
    "quiet": {"label": "조용히 곁에 있기", "preferred": "calm", "moods": ("lonely",),
              "effects": {"happiness": 4, "tiredness": -3},
              "lines": ("말없이 있어도 마음이 편하다냥.", "함께 있는 것만으로 좋다냥.")},
    "groom": {"label": "부드럽게 빗질하기", "preferred": "calm", "moods": ("uncomfortable",),
              "effects": {"cleanliness": 8, "happiness": 2, "tiredness": 1},
              "lines": ("엉킨 털이 풀렸다냥.", "빗질하는 손길이 부드럽다냥.")},
    "hide": {"label": "숨바꼭질하기", "preferred": "energetic", "moods": ("lonely", "happy"),
             "effects": {"happiness": 9, "tiredness": 5, "hunger": 3, "cleanliness": -2},
             "lines": ("찾았다냥! 다음에는 내가 숨겠다냥.", "숨어도 네 발소리는 안다냥!")},
    "cuddle": {"label": "포근하게 기대 쉬기", "preferred": "lazy", "moods": ("tired",),
               "effects": {"tiredness": -7, "happiness": 3, "hunger": 2},
               "lines": ("포근한 자리에서 쉬겠다냥.", "네 옆이 가장 따뜻하다냥.")},
}
SPECIAL_REPEAT_FACTORS = (1.0, 0.85, 0.70, 0.55)


def normalize_special_care(value, day):
    data = {"day": day, "used": False, "last_action": "", "last_used_day": 0, "repeat_count": 0}
    if not isinstance(value, dict):
        return data
    action = value.get("last_action")
    if not isinstance(action, str) or action not in SPECIAL_CARE:
        return data
    try:
        last_day = int(value.get("last_used_day", 0))
        count = max(0, min(4, int(value.get("repeat_count", 0))))
    except (TypeError, ValueError, OverflowError):
        return data
    if not 1 <= last_day <= day or not count:
        return data
    data.update(last_action=action, last_used_day=last_day, repeat_count=count)
    data["used"] = last_day == day
    return data


def special_care_repetition(data, action, day):
    if data["last_action"] == action and data["last_used_day"] == day - 1:
        return min(4, data["repeat_count"] + 1)
    return 1


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
        self.minigame_records = {}

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
