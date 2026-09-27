import unittest

import competition
import items


class InventoryNormalizationTests(unittest.TestCase):
    def test_aliases_merge_and_invalid_counts_are_discarded(self):
        normalized = items.normalize_inventory({
            "bab": "2",
            "밥": 3,
            "생선": -1,
            "츄르": "invalid",
        })
        self.assertEqual(normalized, {"사료": 5})


class CompetitionTests(unittest.TestCase):
    def test_schedule_repeats_every_three_days(self):
        self.assertFalse(competition.is_event_day(2))
        self.assertTrue(competition.is_event_day(3))
        self.assertEqual(competition.event_day_for(4), 6)

    def test_normalization_filters_invalid_history(self):
        normalized = competition.normalize_competition_data({
            "last_entered_day": "6",
            "history": [
                {"day": 3, "id": "cute", "grade": "a", "score": 70, "reward": 120},
                {"day": 6, "id": "unknown", "grade": "S", "score": 99, "reward": 1},
            ],
        })
        self.assertEqual(normalized["last_entered_day"], 6)
        self.assertEqual(len(normalized["history"]), 1)
        self.assertEqual(normalized["history"][0]["grade"], "A")


if __name__ == "__main__":
    unittest.main()
