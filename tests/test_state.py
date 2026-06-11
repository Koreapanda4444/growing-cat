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
