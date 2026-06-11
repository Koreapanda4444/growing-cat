import unittest
from types import SimpleNamespace
from unittest.mock import patch

import evolution
import pygame
import state
from app import Game
from cat import Cat
from items import inventory_item_from_shop_id


class AchievementStub:
    def __init__(self):
        self.events = []

    def on_event(self, event, **payload):
        self.events.append((event, payload))


class AppLogicTests(unittest.TestCase):
    def make_game(self):
        game = object.__new__(Game)
        game.state = SimpleNamespace(day=1, money=0)
        game.inventory = {}
        game.difficulty = "normal"
        game.ach = AchievementStub()
        return game

    def test_buy_item_uses_shared_inventory_mapping(self):
        game = self.make_game()
        game.state.money = 100
        game.make_save_data = lambda: {"cat": {"name": "nabi", "stage": evolution.BABY}}

        with patch("app.save.save_game", return_value=True):
            self.assertTrue(game.on_buy_item({"id": "bab", "price": 25}))

        self.assertEqual(game.state.money, 75)
        self.assertEqual(game.inventory, {"사료": 1})
        self.assertEqual(game.ach.events[0][0], "item_bought")

    def test_start_new_game_applies_selected_difficulty_to_state_and_cat(self):
        game = object.__new__(Game)

        with patch("app.save.save_game", return_value=True):
            Game.start_new_game(game, "nabi", difficulty="hard", personality="calm")

        self.assertEqual(game.difficulty, "hard")
        self.assertEqual(game.personality, "calm")
        self.assertEqual(game.state.difficulty, "hard")
        self.assertEqual(game.state.personality, "calm")
        self.assertEqual(game.cat.difficulty, "hard")
        self.assertEqual(game.cat.personality, "calm")

    def test_unknown_shop_item_does_not_charge_or_unlock(self):
        game = self.make_game()
        game.state.money = 100
        game.make_save_data = lambda: {"cat": {"name": "nabi", "stage": evolution.BABY}}

        with patch("app.save.save_game", return_value=True) as save_mock:
            self.assertFalse(game.on_buy_item({"id": "unknown", "price": 25}))

        self.assertEqual(game.state.money, 100)
        self.assertEqual(game.inventory, {})
        self.assertEqual(game.ach.events, [])
        save_mock.assert_not_called()

    def test_load_saved_game_normalizes_bad_numeric_fields(self):
        game = self.make_game()
        game.personality = "energetic"
        payload = {
            "day": "bad",
            "time_phase": "late",
            "difficulty": "normal",
            "personality": "energetic",
            "money": "bad",
            "cat": {"name": "nabi", "stage": evolution.BABY},
        }

        with patch("app.save.load_game", return_value=payload):
            Game.load_saved_game(game)

        self.assertEqual(game.state.day, 1)
        self.assertEqual(game.state.time_phase, state.MORNING)
        self.assertEqual(game.state.money, 0)
        self.assertEqual(game.scene, "MAIN")

    def test_init_pygame_tolerates_missing_audio_device(self):
        game = object.__new__(Game)
        fake_screen = object()

        with patch("app.pygame.init"), \
                patch("app.pygame.mixer.init", side_effect=pygame.error("no audio")), \
                patch("app.pygame.display.set_caption"), \
                patch("app.pygame.key.start_text_input"), \
                patch("app.pygame.display.set_mode", return_value=fake_screen), \
                patch("app.pygame.display.set_icon"), \
                patch("app.pygame.time.Clock", return_value="clock"), \
                patch("app.load_image", return_value=None):
            Game._init_pygame(game)

        self.assertIs(game.screen, fake_screen)
        self.assertEqual(game.clock, "clock")

    def test_use_item_ignores_non_consumable_inventory_item(self):
        game = self.make_game()
        game.cat = Cat("nabi", evolution.ADULT, image_path="dummy.png")
        meat = inventory_item_from_shop_id("meat")
        game.inventory = {meat: 1}
        game.make_save_data = lambda: {"cat": {"name": "nabi", "stage": evolution.ADULT}}

        with patch("app.save.save_game", return_value=True) as save_mock:
            game.use_item("meat")

        self.assertEqual(game.inventory[meat], 1)
        save_mock.assert_not_called()

    def test_make_save_data_normalizes_bad_runtime_values(self):
        game = self.make_game()
        game.state = SimpleNamespace(
            day="bad",
            money="bad",
            time_phase="late",
            difficulty="bad",
            personality="bad",
            minigame_used=None,
        )
        game.cat = SimpleNamespace(
            name="nabi",
            stage=evolution.BABY,
            hunger="bad",
            tiredness="bad",
            happiness="bad",
            cleanliness="bad",
        )
        game.inventory = {"bab": 0, "fish": 2}

        data = Game.make_save_data(game)

        self.assertEqual(data["day"], 1)
        self.assertEqual(data["money"], 0)
        self.assertEqual(data["time_phase"], state.MORNING)
        self.assertEqual(data["cat"]["hunger"], 50)
        self.assertEqual(data["cat"]["tiredness"], 20)
        self.assertEqual(data["cat"]["happiness"], 70)
        self.assertEqual(data["cat"]["cleanliness"], 60)

    def test_photo_toast_reports_save_failure(self):
        game = self.make_game()
        game.screen = object()
        game.cat = None

        with patch("app.take_photo", side_effect=OSError("no folder")):
            Game._take_photo_toast(game)

        self.assertEqual(game.toast_text, "사진 저장 실패")
        self.assertEqual(game.toast_timer, 2.5)

    def test_save_if_game_active_persists_main_scene(self):
        game = self.make_game()
        game.app_mode = "GAME"
        game.scene = "MAIN"
        game.cat = Cat("nabi", evolution.BABY, image_path="dummy.png")
        game.make_save_data = lambda: {"cat": {"name": "nabi", "stage": evolution.BABY}}

        with patch("app.save.save_game", return_value=True) as save_mock:
            Game._save_if_game_active(game)

        save_mock.assert_called_once_with({"cat": {"name": "nabi", "stage": evolution.BABY}})

    def test_auto_evolve_uses_shared_cost_and_notification(self):
        game = self.make_game()
        game.state.day = 7
        game.state.money = 100
        game.cat = Cat("nabi", evolution.BABY, image_path="dummy.png")

        self.assertTrue(game._try_auto_evolve())

        self.assertEqual(game.cat.stage, evolution.ADULT)
        self.assertEqual(game.state.money, 0)
        self.assertIn(("evolved", {"stage": "adult"}), game.ach.events)


if __name__ == "__main__":
    unittest.main()
