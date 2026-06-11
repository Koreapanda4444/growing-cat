import pygame
import random
import sys

from config import asset_path
from pg_utils import load_font, load_image, solid_surface
import state as game_state

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")

WIDTH, HEIGHT = 400, 600
FPS = 60
GROUND_Y = 450


class CatRunGame:
    def __init__(self, screen, state=None, on_game_end=None):
        self.screen = screen
        self.state = state
        self.difficulty = game_state.normalize_difficulty(getattr(state, "difficulty", None))
        self.balance = game_state.get_minigame_profile(self.difficulty, "jump")
        self.on_game_end = on_game_end
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = load_font(FONT_PATH, 18)
        self._load_assets()
        self._init_world()
        self._init_player()
        self._init_obstacles()

        self.distance = 0.0
        self.score = 0

    def _load_assets(self):
        self.bg = load_image(
            asset_path("minigames", "cat_run", "grass.png"),
            size=(WIDTH, HEIGHT),
            smooth=False,
            alpha=False,
        ) or solid_surface((WIDTH, HEIGHT), (100, 150, 100))

        self.cat_img = load_image(
            asset_path("minigames", "cat_run", "cat.png"),
            size=(48, 48),
            smooth=False,
            alpha=True,
        ) or solid_surface((48, 48), (255, 200, 100), alpha=True)

        self.obstacle_imgs = [
            load_image(
                asset_path("minigames", "cat_run", "orange.png"),
                size=(25, 25),
                smooth=False,
                alpha=True,
            )
            or solid_surface((25, 25), (255, 150, 0), alpha=True),
            load_image(
                asset_path("minigames", "cat_run", "lemon.png"),
                size=(40, 35),
                smooth=False,
                alpha=True,
            )
            or solid_surface((40, 35), (255, 200, 0), alpha=True),
            load_image(
                asset_path("minigames", "cat_run", "water.png"),
                size=(60, 30),
                smooth=False,
                alpha=True,
            )
            or solid_surface((60, 30), (0, 150, 255), alpha=True),
        ]

    def _init_world(self):
        self.bg_x1 = 0
        self.bg_x2 = WIDTH
        self.bg_speed = 2

    def _init_player(self):
        self.cat_x = 60
        self.cat_y = GROUND_Y
        self.cat_vel_y = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.on_ground = True
        self.jump_count = 0
        self.max_jumps = 2

    def _init_obstacles(self):
        self.obstacles = []
        self.base_obstacle_speed = float(self.balance["base_speed"])
        self.obstacle_speed_step = float(self.balance["speed_step"])
        self.obstacle_speed = self.base_obstacle_speed
        self.spawn_timer = 0
        self.spawn_base_delay = int(self.balance["spawn_delay"])
        self.spawn_delay_floor = int(self.balance["spawn_delay_floor"])
        self.spawn_delay_step = int(self.balance["spawn_delay_step"])
        self.spawn_delay = self.spawn_base_delay
        self.base_min_spawn_meters = int(self.balance["min_spawn_meters"])
        self.base_max_spawn_meters = int(self.balance["max_spawn_meters"])
        self.spawn_meter_floor = int(self.balance["spawn_meter_floor"])
        self.spawn_meter_step = int(self.balance["spawn_meter_step"])
        self.min_spawn_meters = self.base_min_spawn_meters
        self.max_spawn_meters = self.base_max_spawn_meters
        self.pixels_per_meter = 10
        self.next_spawn_frames = self._compute_next_spawn_frames()

    def update_difficulty(self):
        difficulty_level = int(self.distance) // 100
        speed_step = getattr(self, "obstacle_speed_step", 1.0)
        spawn_delay_floor = getattr(self, "spawn_delay_floor", 50)
        spawn_delay_step = getattr(self, "spawn_delay_step", 5)
        spawn_base_delay = getattr(self, "spawn_base_delay", 90)
        self.obstacle_speed = self.base_obstacle_speed + (difficulty_level * speed_step)
        self.spawn_delay = max(spawn_delay_floor, spawn_base_delay - (difficulty_level * spawn_delay_step))

        if not hasattr(self, "base_min_spawn_meters") or not hasattr(self, "base_max_spawn_meters"):
            return

        meter_drop = difficulty_level * getattr(self, "spawn_meter_step", 1)
        floor = getattr(self, "spawn_meter_floor", 14)
        self.min_spawn_meters = max(floor, self.base_min_spawn_meters - meter_drop)
        self.max_spawn_meters = max(self.min_spawn_meters + 6, self.base_max_spawn_meters - meter_drop)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_SPACE:
                    if self.jump_count < self.max_jumps:
                        self.cat_vel_y = self.jump_power
                        self.on_ground = False
                        self.jump_count += 1

    def update(self):
        self.bg_x1 -= self.bg_speed
        self.bg_x2 -= self.bg_speed
        if self.bg_x1 <= -WIDTH:
            self.bg_x1 = WIDTH
        if self.bg_x2 <= -WIDTH:
            self.bg_x2 = WIDTH

        self.distance += self.obstacle_speed / self.pixels_per_meter
        self.update_difficulty()

        self.cat_vel_y += self.gravity
        self.cat_y += self.cat_vel_y
        if self.cat_y >= GROUND_Y:
            self.cat_y = GROUND_Y
            self.cat_vel_y = 0
            self.on_ground = True
            self.jump_count = 0

        cat_rect = pygame.Rect(self.cat_x, self.cat_y, 48, 48)
        self.spawn_timer += 1
        if self.spawn_timer >= self.next_spawn_frames:
            self.spawn_timer = 0
            img = random.choice(self.obstacle_imgs)
            rect = img.get_rect(midbottom=(WIDTH + 40, GROUND_Y + 48))
            self.obstacles.append((img, rect))
            self.next_spawn_frames = self._compute_next_spawn_frames()
        for obs in self.obstacles[:]:
            obs[1].x -= self.obstacle_speed
            if obs[1].right < 0:
                self.obstacles.remove(obs)
                self.score += 1

            if cat_rect.colliderect(obs[1]):
                self.running = False

    def draw(self):
        self.screen.blit(self.bg, (self.bg_x1, 0))
        self.screen.blit(self.bg, (self.bg_x2, 0))

        self.screen.blit(self.cat_img, (self.cat_x, self.cat_y))

        for obs in self.obstacles:
            self.screen.blit(obs[0], obs[1])

        distance_text = self.font.render(f"{int(self.distance)}m", True, (0, 0, 0))
        self.screen.blit(distance_text, (10, 10))

        speed_text = self.font.render(f"Speed: {self.obstacle_speed:.1f}", True, (0, 0, 0))
        self.screen.blit(speed_text, (10, 30))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        return self.get_reward()

    def get_reward(self):
        distance_int = int(self.distance)
        coin_reward = (distance_int // 100) * 10
        return {"distance": distance_int, "coins": coin_reward}

    def _compute_next_spawn_frames(self):
        meters = random.randint(self.min_spawn_meters, self.max_spawn_meters)
        speed = max(0.1, self.obstacle_speed)
        frames = int((meters * self.pixels_per_meter) / speed)
        return max(10, min(int(getattr(self, "spawn_delay", frames)), frames))


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("고양이 점프 게임")

    game = CatRunGame(screen)
    result = game.run()

    font = pygame.font.SysFont(None, 24)
    while True:
        screen.fill((200, 200, 200))
        over = font.render(f"GAME OVER - {result['distance']}m", True, (255, 0, 0))
        coins = font.render(f"Coins: +{result['coins']}", True, (0, 0, 0))
        screen.blit(over, (WIDTH // 2 - 80, HEIGHT // 2 - 20))
        screen.blit(coins, (WIDTH // 2 - 60, HEIGHT // 2 + 20))
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
