import state
import random
import os

from config import asset_path

IMAGE_EXTENSIONS = (".png", ".jpg", ".jpeg", ".webp")

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
        self.friendship = 0

        self.image_path = image_path or self.random_image()

    def available_images(self):
        folder = CAT_IMAGE_DIR.get(self.stage)
        if not folder:
            return []

        try:
            files = [
                f for f in os.listdir(folder)
                if (
                    not f.startswith(".")
                    and f.lower().endswith(IMAGE_EXTENSIONS)
                    and os.path.isfile(os.path.join(folder, f))
                )
            ]
        except OSError:
            return []

        return [os.path.join(folder, f) for f in sorted(files)]

    def random_image(self):
        files = self.available_images()
        if not files:
            return None
        return random.choice(files)

    def rotate_image(self):
        files = self.available_images()
        if len(files) <= 1:
            return False

        current = os.path.normcase(os.path.abspath(self.image_path or ""))
        candidates = [
            path for path in files
            if os.path.normcase(os.path.abspath(path)) != current
        ]
        if not candidates:
            return False

        self.image_path = random.choice(candidates)
        return True

    def evolve_to(self, new_stage):
        self.stage = new_stage
        self.image_path = self.random_image()

    def get_display_name(self):
        return f"{self.name} - {self.stage}"

    @property
    def mood(self):
        needs = (
            ("hungry", (self.hunger - 70) / 30),
            ("tired", (self.tiredness - 70) / 30),
            ("uncomfortable", (30 - self.cleanliness) / 30),
            ("lonely", (30 - self.happiness) / 30),
        )
        mood, urgency = max(needs, key=lambda need: need[1])
        if urgency >= 0:
            return mood
        if (self.happiness >= 75 and self.cleanliness >= 65
                and self.hunger <= 35 and self.tiredness <= 35):
            return "happy"
        return "calm"

    def care_reaction(self, action, previous_mood=None, recent=()):
        mood = previous_mood or self.mood
        relief = {
            ("hungry", "feed"): "밥을 챙겨줘서 힘이 난다냥!",
            ("tired", "sleep"): "푹 쉬면 다시 놀 수 있다냥.",
            ("uncomfortable", "clean"): "털이 보송보송해졌다냥.",
            ("lonely", "play"): "같이 놀아줘서 고맙다냥!",
        }
        if (mood, action) in relief and relief[mood, action] not in recent:
            preferred = state.get_personality_profile(self.personality)["preferred_action"]
            if action != preferred or random.random() < 0.6:
                return relief[mood, action]
        if action == "play" and mood in ("hungry", "tired"):
            return "재밌지만 밥이나 휴식도 필요하다냥."
        profile = state.get_personality_profile(self.personality)
        lines = profile["care_lines"].get(action, state.MOOD_PROFILE[self.mood]["lines"])
        choices = [line for line in lines if line not in recent]
        if not choices:
            choices = [line for line in state.MOOD_PROFILE[self.mood]["lines"] if line not in recent]
        return random.choice(choices or lines)

    def change_friendship(self, amount):
        before = self.friendship
        self.friendship = state.normalize_friendship(before + amount)
        return self.friendship - before

    def care_friendship_change(self, action, before):
        stat = {"feed": "hunger", "play": "happiness", "clean": "cleanliness", "sleep": "tiredness"}[action]
        if self.check_game_over():
            return -3
        if action == "play" and (self.hunger >= 80 or self.tiredness >= 80):
            return -2
        recovery = before - getattr(self, stat) if action in ("feed", "sleep") else getattr(self, stat) - before
        if recovery <= 0:
            return 0
        needed = before >= 60 if action in ("feed", "sleep") else before <= 40
        preferred = state.get_personality_profile(self.personality)["preferred_action"] == action
        return 2 + int(needed) + int(preferred)

    def _get_personality_modifier(self, stat_type: str, action=None) -> float:
        profile = state.get_personality_profile(self.personality)
        overrides = profile.get("care_modifiers", {}).get(action, {})
        return overrides.get(stat_type, profile.get(stat_type, 1.0))

    def _roll_stat_change(self, rng, difficulty_kind: str, modifier_key: str, *, inverse_modifier: bool = False, action=None) -> int:
        value = state.rand_range(state.scaled_range(rng, self.difficulty, difficulty_kind))
        modifier = self._get_personality_modifier(modifier_key, action)
        if inverse_modifier:
            return int(value / modifier)
        return int(value * modifier)

    def on_night(self):
        if not self._can_act():
            return
        hunger_inc = self._roll_stat_change(state.NIGHT_HUNGER_INC, "pressure", "hunger_increase")
        tiredness_inc = self._roll_stat_change(state.NIGHT_TIREDNESS_INC, "pressure", "tiredness_increase")
        happiness_dec = self._roll_stat_change(
            state.NIGHT_HAPPINESS_DEC,
            "pressure",
            "happiness_recovery",
            inverse_modifier=True,
        )
        cleanliness_dec = self._roll_stat_change(state.NIGHT_CLEANLINESS_DEC, "pressure", "cleanliness_decrease")
        
        self.hunger += hunger_inc
        self.tiredness += tiredness_inc
        self.happiness -= happiness_dec
        self.cleanliness -= cleanliness_dec
        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def on_morning(self):
        if not self._can_act():
            return
        hunger_inc = self._roll_stat_change(state.MORNING_HUNGER_INC, "pressure", "hunger_increase")
        tiredness_dec = self._roll_stat_change(state.MORNING_TIREDNESS_DEC, "recovery", "tiredness_recovery")
        happiness_inc = self._roll_stat_change(state.MORNING_HAPPINESS_INC, "recovery", "happiness_recovery")
        cleanliness_dec = self._roll_stat_change(state.MORNING_CLEANLINESS_DEC, "pressure", "cleanliness_decrease")
        
        self.hunger += hunger_inc
        self.tiredness -= tiredness_dec
        self.happiness += happiness_inc
        self.cleanliness -= cleanliness_dec
        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def feed_free(self):
        if not self._can_act():
            return
        hunger_dec = self._roll_stat_change(
            state.FREE_FEED_HUNGER_DEC,
            "recovery",
            "hunger_increase",
            inverse_modifier=True,
        )
        happiness_inc = self._roll_stat_change(state.FREE_FEED_HAPPINESS_INC, "recovery", "happiness_recovery")
        
        self.hunger -= hunger_dec
        self.happiness += happiness_inc
        self._clamp_all()

    def play_free(self):
        if not self._can_act():
            return
        happiness_inc = self._roll_stat_change(
            state.FREE_PLAY_HAPPINESS_INC, "recovery", "happiness_recovery", action="play"
        )
        tiredness_inc = self._roll_stat_change(state.FREE_PLAY_TIREDNESS_INC, "pressure", "tiredness_increase")
        hunger_inc = self._roll_stat_change(state.FREE_PLAY_HUNGER_INC, "pressure", "hunger_increase")
        cleanliness_dec = self._roll_stat_change(state.FREE_PLAY_CLEANLINESS_DEC, "pressure", "cleanliness_decrease")
        
        self.happiness += happiness_inc
        self.tiredness += tiredness_inc
        self.hunger += hunger_inc
        self.cleanliness -= cleanliness_dec
        self._clamp_all()

    def clean(self):
        if not self._can_act():
            return
        cleanliness_inc = self._roll_stat_change(
            state.CLEAN_CLEANLINESS_INC,
            "recovery",
            "cleanliness_decrease",
            inverse_modifier=True,
            action="clean",
        )
        happiness_dec = self._roll_stat_change(
            state.CLEAN_HAPPINESS_DEC,
            "pressure",
            "happiness_recovery",
            inverse_modifier=True,
        )
        
        self.cleanliness += cleanliness_inc
        self.happiness -= happiness_dec
        self._clamp_all()

    def sleep(self):
        if not self._can_act():
            return
        tiredness_dec = self._roll_stat_change(
            state.SLEEP_TIREDNESS_DEC, "recovery", "tiredness_recovery", action="sleep"
        )
        happiness_inc = self._roll_stat_change(state.SLEEP_HAPPINESS_INC, "recovery", "happiness_recovery")
        
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
        if (
            self.happiness <= state.RUNAWAY_HAPPINESS_THRESHOLD
            or self.cleanliness <= state.RUNAWAY_CLEANLINESS_THRESHOLD
        ):
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
