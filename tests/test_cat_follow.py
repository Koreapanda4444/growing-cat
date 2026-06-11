import unittest

from minigames.cat_follow import CatFollowGame


class CatFollowLogicTests(unittest.TestCase):
    def make_game(self):
        game = object.__new__(CatFollowGame)
        game.phase = "INPUT"
        game.sequence = [(0, 0), (1, 1)]
        game.seq_len = 2
        game.input_index = 0
        game.fails = 0
        game.max_fails = 2
        game.show_timer = 1.0
        game.show_step = 1
        game.show_on = False
        return game

    def test_wrong_input_replays_same_sequence(self):
        game = self.make_game()
        original_sequence = list(game.sequence)

        game._handle_wrong_input()

        self.assertEqual(game.sequence, original_sequence)
        self.assertEqual(game.phase, "SHOW")
        self.assertEqual(game.input_index, 0)

    def test_completed_round_generates_next_sequence(self):
        game = self.make_game()
        game.rounds_cleared = 0
        game.round_idx = 1
        game.target_round = 3
        game._new_sequence = lambda length: [(2, 2), (3, 3)]
        game.input_index = len(game.sequence) - 1
        game.cats_correct = 0

        game._handle_correct_input()

        self.assertEqual(game.sequence, [(2, 2), (3, 3)])
        self.assertEqual(game.rounds_cleared, 1)
        self.assertEqual(game.round_idx, 2)

    def test_sequence_length_can_grow_by_round(self):
        game = object.__new__(CatFollowGame)
        game.start_len = 4
        game.sequence_growth = 2

        self.assertEqual(game._sequence_length_for_round(1), 4)
        self.assertEqual(game._sequence_length_for_round(2), 6)
        self.assertEqual(game._sequence_length_for_round(3), 8)


if __name__ == "__main__":
    unittest.main()
