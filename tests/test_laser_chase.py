import unittest

from minigames.laser_chase import _coins_from_score, _laser_settings, _update_particles


class LaserChaseHelpersTests(unittest.TestCase):
    def test_coin_reward_has_minimum_and_win_bonus(self):
        self.assertEqual(_coins_from_score(0, False), 8)
        self.assertEqual(_coins_from_score(450, False), 10)
        self.assertEqual(_coins_from_score(450, True), 35)

    def test_update_particles_moves_and_expires(self):
        particles = [[0.0, 0.0, 10.0, 5.0, 0.1]]

        _update_particles(particles, 0.05)
        self.assertEqual(len(particles), 1)
        self.assertAlmostEqual(particles[0][0], 0.5)
        self.assertAlmostEqual(particles[0][1], 0.25)

        _update_particles(particles, 0.06)
        self.assertEqual(particles, [])

    def test_laser_settings_follow_selected_difficulty(self):
        easy = _laser_settings("easy")
        normal = _laser_settings("normal")
        hard = _laser_settings("hard")

        self.assertGreater(easy["time_limit"], normal["time_limit"])
        self.assertGreater(normal["time_limit"], hard["time_limit"])
        self.assertLess(easy["target_score"], normal["target_score"])
        self.assertLess(normal["target_score"], hard["target_score"])
        self.assertLess(easy["base_speed"], normal["base_speed"])
        self.assertLess(normal["base_speed"], hard["base_speed"])


if __name__ == "__main__":
    unittest.main()
