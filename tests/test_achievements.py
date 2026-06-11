import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from achievements import AchievementsManager


class AchievementsManagerTests(unittest.TestCase):
    def test_invalid_numeric_event_payload_does_not_crash(self):
        with tempfile.TemporaryDirectory() as td:
            manager = AchievementsManager(str(Path(td) / "achievements.json"))

            manager.on_event("coins_earned", amount="not-a-number")
            manager.check_stats_on_day_end({
                "happiness": "bad",
                "cleanliness": None,
                "hunger": object(),
                "fatigue": "bad",
            })

            self.assertEqual(manager.counters["coins_total"], 0)

    def test_save_failure_does_not_crash_unlock_flow(self):
        with tempfile.TemporaryDirectory() as td:
            manager = AchievementsManager(str(Path(td) / "achievements.json"))

            with patch.object(Path, "write_text", side_effect=OSError("disk full")):
                manager.on_event("coins_earned", amount=1)

            self.assertTrue(manager.is_unlocked("A010"))

    def test_save_creates_parent_directory(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "nested" / "achievements.json"
            manager = AchievementsManager(str(path))

            manager.on_event("coins_earned", amount=1)

            self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
