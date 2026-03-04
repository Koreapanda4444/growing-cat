import state
import random
import os

from config import asset_path

CAT_IMAGE_DIR = {
    "아기고양이": asset_path("cats", "baby"),
    "어른고양이": asset_path("cats", "adult"),
    "사자고양이": asset_path("cats", "lion"),
    "공룡고양이": asset_path("cats", "dino"),
}

class Cat:
    def __init__(self, name, stage, image_path=None, difficulty="normal", personality="energetic"):
        self.name = name
        self.stage = stage
        self.difficulty = state.normalize_difficulty(difficulty)
        self.personality = state.normalize_personality(personality)

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

    def _get_personality_modifier(self, stat_type: str) -> float:
        """성격에 따른 스탯 변화 배율 반환"""
        prof = state.get_personality_profile(self.personality)
        
        # 프로필에서 해당 stat_type의 배율 가져오기
        if stat_type in prof:
            return prof[stat_type]
        return 1.0

    def on_night(self):
        if not self._can_act(): return
        hunger_inc = int(state.rand_range(state.scaled_range(state.NIGHT_HUNGER_INC, self.difficulty, "pressure")) * self._get_personality_modifier("hunger_increase"))
        tiredness_inc = int(state.rand_range(state.scaled_range(state.NIGHT_TIREDNESS_INC, self.difficulty, "pressure")) * self._get_personality_modifier("tiredness_increase"))
        happiness_dec = int(state.rand_range(state.scaled_range(state.NIGHT_HAPPINESS_DEC, self.difficulty, "pressure")) / self._get_personality_modifier("happiness_recovery"))
        cleanliness_dec = int(state.rand_range(state.scaled_range(state.NIGHT_CLEANLINESS_DEC, self.difficulty, "pressure")) * self._get_personality_modifier("cleanliness_decrease"))
        
        self.hunger += hunger_inc
        self.tiredness += tiredness_inc
        self.happiness -= happiness_dec
        self.cleanliness -= cleanliness_dec
        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def on_morning(self):
        if not self._can_act(): return
        hunger_inc = int(state.rand_range(state.scaled_range(state.MORNING_HUNGER_INC, self.difficulty, "pressure")) * self._get_personality_modifier("hunger_increase"))
        tiredness_dec = int(state.rand_range(state.scaled_range(state.MORNING_TIREDNESS_DEC, self.difficulty, "recovery")) * self._get_personality_modifier("tiredness_recovery"))
        happiness_inc = int(state.rand_range(state.scaled_range(state.MORNING_HAPPINESS_INC, self.difficulty, "recovery")) * self._get_personality_modifier("happiness_recovery"))
        cleanliness_dec = int(state.rand_range(state.scaled_range(state.MORNING_CLEANLINESS_DEC, self.difficulty, "pressure")) * self._get_personality_modifier("cleanliness_decrease"))
        
        self.hunger += hunger_inc
        self.tiredness -= tiredness_dec
        self.happiness += happiness_inc
        self.cleanliness -= cleanliness_dec
        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def feed_free(self):
        if not self._can_act(): return
        hunger_dec = int(state.rand_range(state.scaled_range(state.FREE_FEED_HUNGER_DEC, self.difficulty, "recovery")) / self._get_personality_modifier("hunger_increase"))
        happiness_inc = int(state.rand_range(state.scaled_range(state.FREE_FEED_HAPPINESS_INC, self.difficulty, "recovery")) * self._get_personality_modifier("happiness_recovery"))
        
        self.hunger -= hunger_dec
        self.happiness += happiness_inc
        self._clamp_all()

    def play_free(self):
        if not self._can_act(): return
        happiness_inc = int(state.rand_range(state.scaled_range(state.FREE_PLAY_HAPPINESS_INC, self.difficulty, "recovery")) * self._get_personality_modifier("happiness_recovery"))
        tiredness_inc = int(state.rand_range(state.scaled_range(state.FREE_PLAY_TIREDNESS_INC, self.difficulty, "pressure")) * self._get_personality_modifier("tiredness_increase"))
        hunger_inc = int(state.rand_range(state.scaled_range(state.FREE_PLAY_HUNGER_INC, self.difficulty, "pressure")) * self._get_personality_modifier("hunger_increase"))
        cleanliness_dec = int(state.rand_range(state.scaled_range(state.FREE_PLAY_CLEANLINESS_DEC, self.difficulty, "pressure")) * self._get_personality_modifier("cleanliness_decrease"))
        
        self.happiness += happiness_inc
        self.tiredness += tiredness_inc
        self.hunger += hunger_inc
        self.cleanliness -= cleanliness_dec
        self._clamp_all()

    def clean(self):
        if not self._can_act(): return
        cleanliness_inc = int(state.rand_range(state.scaled_range(state.CLEAN_CLEANLINESS_INC, self.difficulty, "recovery")) / self._get_personality_modifier("cleanliness_decrease"))
        happiness_dec = int(state.rand_range(state.scaled_range(state.CLEAN_HAPPINESS_DEC, self.difficulty, "pressure")) / self._get_personality_modifier("happiness_recovery"))
        
        self.cleanliness += cleanliness_inc
        self.happiness -= happiness_dec
        self._clamp_all()

    def sleep(self):
        if not self._can_act(): return
        tiredness_dec = int(state.rand_range(state.scaled_range(state.SLEEP_TIREDNESS_DEC, self.difficulty, "recovery")) * self._get_personality_modifier("tiredness_recovery"))
        happiness_inc = int(state.rand_range(state.scaled_range(state.SLEEP_HAPPINESS_INC, self.difficulty, "recovery")) * self._get_personality_modifier("happiness_recovery"))
        
        self.tiredness -= tiredness_dec
        self.happiness += happiness_inc
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
