import unittest
from types import SimpleNamespace

from game import MiniGameScreen


class AchievementStub:
    def __init__(self):
        self.events = []

    def on_event(self, event, **payload):
        self.events.append((event, payload))


class MiniGameScreenTests(unittest.TestCase):
    def test_start_selected_game_applies_reward_and_usage_once(self):
        screen = object.__new__(MiniGameScreen)
        screen.selected = "footsteps"
        screen.state = SimpleNamespace(
            difficulty="normal",
            minigame_used={},
            money=3,
        )
        screen.ach = AchievementStub()
        screen.running = True
        screen._run_minigame = lambda selected: {"won": True, "coins": 7}

        MiniGameScreen.start_selected_game(screen)

        self.assertFalse(screen.running)
        self.assertTrue(screen.state.minigame_used["footsteps"])
        self.assertEqual(screen.state.money, 10)
        self.assertEqual(
            [event for event, _ in screen.ach.events],
            ["minigame_played", "coins_earned", "minigame_won"],
        )

    def test_used_minigame_does_not_run_again(self):
        screen = object.__new__(MiniGameScreen)
        screen.selected = "memory"
        screen.state = SimpleNamespace(
            difficulty="normal",
            minigame_used={"memory": True},
            money=0,
        )
        screen.ach = AchievementStub()
        screen.running = True
        screen._run_minigame = lambda selected: self.fail("minigame should not run")

        MiniGameScreen.start_selected_game(screen)

        self.assertTrue(screen.running)
        self.assertEqual(screen.state.money, 0)
        self.assertEqual(screen.ach.events, [])


if __name__ == "__main__":
    unittest.main()
