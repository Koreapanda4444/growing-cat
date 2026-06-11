import unittest

import state
from minigames.cat_run import CatRunGame


class CatRunGameTests(unittest.TestCase):
    def test_update_refreshes_difficulty_without_obstacles(self):
        game = CatRunGame.__new__(CatRunGame)
        game.bg_x1 = 0
        game.bg_x2 = 400
        game.bg_speed = 2
        game.base_obstacle_speed = 4.0
        game.obstacle_speed = 4.0
        game.distance = 200.0
        game.pixels_per_meter = 10
        game.cat_x = 60
        game.cat_y = 450
        game.cat_vel_y = 0
        game.gravity = 0
        game.on_ground = True
        game.jump_count = 0
        game.spawn_timer = 0
        game.next_spawn_frames = 999
        game.obstacles = []

        game.update()

        self.assertGreater(game.obstacle_speed, game.base_obstacle_speed)

    def test_obstacle_settings_follow_selected_difficulty_profile(self):
        easy = CatRunGame.__new__(CatRunGame)
        easy.balance = state.get_minigame_profile("easy", "jump")
        easy._init_obstacles()

        hard = CatRunGame.__new__(CatRunGame)
        hard.balance = state.get_minigame_profile("hard", "jump")
        hard._init_obstacles()

        self.assertLess(easy.base_obstacle_speed, hard.base_obstacle_speed)
        self.assertGreater(easy.min_spawn_meters, hard.min_spawn_meters)
        self.assertGreater(easy.spawn_delay, hard.spawn_delay)


if __name__ == "__main__":
    unittest.main()
