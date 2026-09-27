import math
import unittest

import state


class StateConversionTests(unittest.TestCase):
    def test_safe_int_uses_default_for_invalid_values(self):
        self.assertEqual(state.safe_int("12"), 12)
        self.assertEqual(state.safe_int(None, 7), 7)
        self.assertEqual(state.safe_int(float("inf"), 7), 7)

    def test_safe_stat_clamps_and_rejects_non_finite_values(self):
        self.assertEqual(state.safe_stat(-1), 0)
        self.assertEqual(state.safe_stat(101), state.MAX_STAT)
        self.assertEqual(state.safe_stat("42.5"), 42.5)
        self.assertEqual(state.safe_stat(float("nan"), 33), 33)
        self.assertTrue(math.isfinite(state.safe_stat(float("inf"), 25)))

    def test_game_state_advances_day_after_night(self):
        game = state.GameState()
        self.assertEqual(game.advance_time(), state.NIGHT)
        self.assertEqual(game.day, 1)
        self.assertEqual(game.advance_time(), state.MORNING)
        self.assertEqual(game.day, 2)

    def test_minigame_usage_normalizes_unknown_and_missing_keys(self):
        usage = state.normalize_minigame_usage({"jump": 1, "unknown": True})
        self.assertEqual(set(usage), set(state.MINIGAME_KEYS))
        self.assertTrue(usage["jump"])
        self.assertFalse(usage["memory"])


if __name__ == "__main__":
    unittest.main()
