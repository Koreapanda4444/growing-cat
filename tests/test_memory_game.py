import unittest

from minigames.memory_game import MemoryGame


class MemoryGameTests(unittest.TestCase):
    def test_mismatch_timeout_is_safe_without_selected_cards(self):
        game = MemoryGame.__new__(MemoryGame)
        game.first = None
        game.second = None
        game.lock = True

        game.handle_mismatch_timeout()

        self.assertIsNone(game.first)
        self.assertIsNone(game.second)
        self.assertFalse(game.lock)


if __name__ == "__main__":
    unittest.main()
