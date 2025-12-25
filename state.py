import random

MORNING = "morning"
NIGHT = "night"


class GameState:
    def __init__(self):
        self.day = 1
        self.time_phase = MORNING
        self.money = 0
        self.minigame_used = {"jump": False, "memory": False}

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

NIGHT_HUNGER_INC = (20, 30)
NIGHT_TIREDNESS_INC = (10, 20)
NIGHT_HAPPINESS_DEC = (10, 20)
NIGHT_CLEANLINESS_DEC = (10, 25)

MORNING_HUNGER_INC = (15, 20)
MORNING_TIREDNESS_DEC = (15, 20)
MORNING_HAPPINESS_INC = (10, 25)
MORNING_CLEANLINESS_DEC = (10, 20)

FREE_FEED_HUNGER_DEC = (10, 25)
FREE_FEED_HAPPINESS_INC = (5, 10)

FREE_PLAY_HAPPINESS_INC = (20, 25)
FREE_PLAY_TIREDNESS_INC = (15, 20)
FREE_PLAY_HUNGER_INC = (10, 15) 
FREE_PLAY_CLEANLINESS_DEC = (10, 20)

CLEAN_CLEANLINESS_INC = (15, 30)
CLEAN_HAPPINESS_DEC = (20, 30)

SLEEP_TIREDNESS_DEC = (25, 30)
SLEEP_HAPPINESS_INC = (10, 20)

DEATH_HUNGER_THRESHOLD = 100
DEATH_TIREDNESS_THRESHOLD = 100

RUNAWAY_HAPPINESS_THRESHOLD = 0
RUNAWAY_CLEANLINESS_THRESHOLD = 0
