import state
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CAT_IMAGE_DIR = {
    "아기고양이": os.path.join(BASE_DIR, "assets", "cats", "baby"),
    "어른고양이": os.path.join(BASE_DIR, "assets", "cats", "adult"),
    "사자고양이": os.path.join(BASE_DIR, "assets", "cats", "lion"),
    "공룡고양이": os.path.join(BASE_DIR, "assets", "cats", "dino"),
}

class Cat:
    def __init__(self, name, stage, image_path=None):
        self.name = name
        self.stage = stage

        self.hunger = random.randint(25, 50)
        self.tiredness = random.randint(5, 25)
        self.happiness = random.randint(50, 75)
        self.cleanliness = random.randint(30, 80)

        self.alive = True
        self.runaway = False

        self.image_path = image_path or self.random_image()

    def random_image(self):
        folder = CAT_IMAGE_DIR.get(self.stage)
        if not folder:
            return None

        try:
            files = [f for f in os.listdir(folder) if not f.startswith(".")]
        except FileNotFoundError:
            return None

        if not files:
            return None

        return os.path.join(folder, random.choice(files))

    def evolve_to(self, new_stage):
        self.stage = new_stage
        self.image_path = self.random_image()

    def get_display_name(self):
        return f"{self.name} - {self.stage}"

    def on_night(self):
        if not self._can_act(): return
        self.hunger += state.rand_range(state.NIGHT_HUNGER_INC)
        self.tiredness += state.rand_range(state.NIGHT_TIREDNESS_INC)
        self.happiness -= state.rand_range(state.NIGHT_HAPPINESS_DEC)
        self.cleanliness -= state.rand_range(state.NIGHT_CLEANLINESS_DEC)
        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def on_morning(self):
        if not self._can_act(): return
        self.hunger += state.rand_range(state.MORNING_HUNGER_INC)
        self.tiredness -= state.rand_range(state.MORNING_TIREDNESS_DEC)
        self.happiness += state.rand_range(state.MORNING_HAPPINESS_INC)
        self.cleanliness -= state.rand_range(state.MORNING_CLEANLINESS_DEC)
        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def feed_free(self):
        if not self._can_act(): return
        self.hunger -= state.rand_range(state.FREE_FEED_HUNGER_DEC)
        self.happiness += state.rand_range(state.FREE_FEED_HAPPINESS_INC)
        self._clamp_all()

    def play_free(self):
        if not self._can_act(): return
        self.happiness += state.rand_range(state.FREE_PLAY_HAPPINESS_INC)
        self.tiredness += state.rand_range(state.FREE_PLAY_TIREDNESS_INC)
        self.hunger += state.rand_range(state.FREE_PLAY_HUNGER_DEC)
        self.cleanliness -= state.rand_range(state.FREE_PLAY_CLEANLINESS_DEC)
        self._clamp_all()

    def clean(self):
        if not self._can_act(): return
        self.cleanliness += state.rand_range(state.CLEAN_CLEANLINESS_INC)
        self.happiness -= state.rand_range(state.CLEAN_HAPPINESS_DEC)
        self._clamp_all()

    def _can_act(self):
        return self.alive and not self.runaway

    def _clamp_all(self):
        self.hunger = state.clamp(self.hunger)
        self.tiredness = state.clamp(self.tiredness)
        self.happiness = state.clamp(self.happiness)
        self.cleanliness = state.clamp(self.cleanliness)

    def _check_death(self):
        if self.hunger >= state.DEATH_HUNGER_THRESHOLD or self.tiredness >= state.DEATH_TIREDNESS_THRESHOLD:
            self.alive = False

    def _check_runaway(self):
        if self.happiness <= state.RUNAWAY_HAPPINESS_THRESHOLD or self.cleanliness <= state.RUNAWAY_CLEANLINESS_THRESHOLD:
            self.runaway = True

    def check_game_over(self):
        if self.hunger >= state.DEATH_HUNGER_THRESHOLD:
            return "DEAD"
        if self.tiredness >= state.DEATH_TIREDNESS_THRESHOLD:
            return "DEAD"
        if self.happiness <= state.RUNAWAY_HAPPINESS_THRESHOLD:
            return "RUNAWAY"
        if self.cleanliness <= state.RUNAWAY_CLEANLINESS_THRESHOLD:
            return "RUNAWAY"
        return None
