import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch

import cat as cat_module
import evolution
import state
from cat import Cat


class StateTests(unittest.TestCase):
    def test_rand_range_returns_inclusive_value(self):
        values = {state.rand_range((2, 3)) for _ in range(100)}

        self.assertTrue(values <= {2, 3})
        self.assertTrue(values)

    def test_normalize_minigame_usage_fills_missing_keys(self):
        usage = state.normalize_minigame_usage({"jump": 1, "memory": 0})

        self.assertEqual(set(usage), set(state.MINIGAME_KEYS))
        self.assertTrue(usage["jump"])
        self.assertFalse(usage["memory"])
        self.assertFalse(usage["footsteps"])
        self.assertFalse(usage["laser"])

    def test_difficulty_profiles_are_ordered_by_pressure_and_economy(self):
        easy = state.get_difficulty_profile("easy")
        normal = state.get_difficulty_profile("normal")
        hard = state.get_difficulty_profile("hard")

        self.assertLess(easy["stat_pressure"], normal["stat_pressure"])
        self.assertLess(normal["stat_pressure"], hard["stat_pressure"])
        self.assertGreater(easy["stat_recovery"], normal["stat_recovery"])
        self.assertGreater(normal["stat_recovery"], hard["stat_recovery"])
        self.assertGreater(easy["day_coin"], normal["day_coin"])
        self.assertGreater(normal["day_coin"], hard["day_coin"])
        self.assertLess(state.get_shop_price(100, "easy"), state.get_shop_price(100, "normal"))
        self.assertLess(state.get_shop_price(100, "normal"), state.get_shop_price(100, "hard"))
        self.assertLess(state.get_evolution_cost(100, "easy"), state.get_evolution_cost(100, "normal"))
        self.assertLess(state.get_evolution_cost(100, "normal"), state.get_evolution_cost(100, "hard"))

    def test_minigame_profiles_are_ordered_by_difficulty(self):
        easy_jump = state.get_minigame_profile("easy", "jump")
        normal_jump = state.get_minigame_profile("normal", "jump")
        hard_jump = state.get_minigame_profile("hard", "jump")
        self.assertLess(easy_jump["base_speed"], normal_jump["base_speed"])
        self.assertLess(normal_jump["base_speed"], hard_jump["base_speed"])
        self.assertGreater(easy_jump["min_spawn_meters"], normal_jump["min_spawn_meters"])
        self.assertGreater(normal_jump["min_spawn_meters"], hard_jump["min_spawn_meters"])

        easy_memory = state.get_minigame_profile("easy", "memory")
        normal_memory = state.get_minigame_profile("normal", "memory")
        hard_memory = state.get_minigame_profile("hard", "memory")
        self.assertGreater(easy_memory["time_limit_ms"], normal_memory["time_limit_ms"])
        self.assertGreater(normal_memory["time_limit_ms"], hard_memory["time_limit_ms"])

        easy_follow = state.get_minigame_profile("easy", "footsteps")
        normal_follow = state.get_minigame_profile("normal", "footsteps")
        hard_follow = state.get_minigame_profile("hard", "footsteps")
        self.assertLess(easy_follow["start_len"], normal_follow["start_len"])
        self.assertLess(normal_follow["start_len"], hard_follow["start_len"])
        self.assertGreater(easy_follow["max_fails"], normal_follow["max_fails"])
        self.assertGreater(normal_follow["max_fails"], hard_follow["max_fails"])

        easy_laser = state.get_minigame_profile("easy", "laser")
        normal_laser = state.get_minigame_profile("normal", "laser")
        hard_laser = state.get_minigame_profile("hard", "laser")
        self.assertGreater(easy_laser["time_limit"], normal_laser["time_limit"])
        self.assertGreater(normal_laser["time_limit"], hard_laser["time_limit"])
        self.assertLess(easy_laser["target_score"], normal_laser["target_score"])
        self.assertLess(normal_laser["target_score"], hard_laser["target_score"])

    def test_minigame_coin_scaling_uses_difficulty(self):
        self.assertEqual(state.scale_coin(20, "easy", source="minigame"), 25)
        self.assertEqual(state.scale_coin(20, "normal", source="minigame"), 20)
        self.assertEqual(state.scale_coin(20, "hard", source="minigame"), 16)

    def test_cat_actions_can_use_state_random_range(self):
        cat = Cat("test", evolution.BABY, image_path="dummy.png")
        cat.hunger = 50
        cat.tiredness = 20
        cat.happiness = 50
        cat.cleanliness = 50

        cat.feed_free()

        self.assertLess(cat.hunger, 50)
        self.assertGreaterEqual(cat.hunger, 0)
        self.assertLessEqual(cat.hunger, state.MAX_STAT)

    def test_cat_random_image_uses_image_files_only(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / "valid.png").write_bytes(b"not-really-an-image")
            (root / "folder.png").mkdir()
            (root / ".hidden.png").write_bytes(b"hidden")
            (root / "notes.txt").write_text("skip", encoding="utf-8")

            with patch.dict(cat_module.CAT_IMAGE_DIR, {"stage": str(root)}):
                chosen = Cat("nabi", "stage").random_image()

        self.assertTrue(chosen.endswith("valid.png"))


if __name__ == "__main__":
    unittest.main()
