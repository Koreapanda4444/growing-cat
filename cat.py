import state


class Cat:
    def __init__(self):
        self.hunger = 0
        self.tiredness = 0
        self.happiness = 75
        self.cleanliness = 75

        self.alive = True
        self.runaway = False

        self._death_days = 0
        self._runaway_days = 0

    def on_night(self):
        if not self._can_act():
            return

        self.hunger -= state.rand_range(state.NIGHT_HUNGER_DEC)
        self.tiredness += state.rand_range(state.NIGHT_TIREDNESS_INC)
        self.happiness -= state.rand_range(state.NIGHT_HAPPINESS_DEC)
        self.cleanliness -= state.rand_range(state.NIGHT_CLEANLINESS_DEC)

        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def on_morning(self):
        if not self._can_act():
            return

        self.hunger -= state.rand_range(state.MORNING_HUNGER_DEC)
        self.tiredness -= state.rand_range(state.MORNING_TIREDNESS_DEC)
        self.happiness += state.rand_range(state.MORNING_HAPPINESS_INC)
        self.cleanliness -= state.rand_range(state.MORNING_CLEANLINESS_DEC)

        self._clamp_all()
        self._check_death()
        self._check_runaway()

    def feed_free(self):
        if not self._can_act():
            return

        self.hunger -= state.rand_range(state.FREE_FEED_HUNGER_DEC)
        self.happiness += state.rand_range(state.FREE_FEED_HAPPINESS_INC)
        self._clamp_all()

    def play_free(self):
        if not self._can_act():
            return

        self.happiness += state.rand_range(state.FREE_PLAY_HAPPINESS_INC)
        self.tiredness += state.rand_range(state.FREE_PLAY_TIREDNESS_INC)
        self.hunger += state.rand_range(state.FREE_PLAY_HUNGER_DEC)
        self.cleanliness -= state.rand_range(state.FREE_PLAY_CLEANLINESS_DEC)
        self._clamp_all()

    def clean(self):
        if not self._can_act():
            return

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
        if (
            self.hunger <= state.DEATH_HUNGER_THRESHOLD
            or self.tiredness >= state.DEATH_TIREDNESS_THRESHOLD
        ):
            self._death_days += 1
            if self._death_days >= 1:
                self.alive = False
        else:
            self._death_days = 0

    def _check_runaway(self):
        if (
            self.happiness <= state.RUNAWAY_HAPPINESS_THRESHOLD
            and self.cleanliness <= state.RUNAWAY_CLEANLINESS_THRESHOLD
        ):
            self._runaway_days += 1
            if self._runaway_days >= 1:
                self.runaway = True
        else:
            self._runaway_days = 0
