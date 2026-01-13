import pygame
import random
import sys
import os

from config import asset_path
from pg_utils import load_font

ASSET_DIR = asset_path("minigames", "cat_run")
FONT_PATH = asset_path("minigames", "cat_run", "fonts", "ThinDungGeunMo.ttf")

WIDTH, HEIGHT = 400, 600
FPS = 60
GROUND_Y = 450


class CatRunGame:
    def __init__(self, screen, state=None, on_game_end=None):
        self.screen = screen
        self.state = state
        self.on_game_end = on_game_end
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = load_font(FONT_PATH, 18)

        try:
            self.bg = pygame.image.load(os.path.join(ASSET_DIR, "grass.png")).convert()
            self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        except:
            self.bg = pygame.Surface((WIDTH, HEIGHT))
            self.bg.fill((100, 150, 100))

        try:
            self.cat_img = pygame.image.load(os.path.join(ASSET_DIR, "cat.png")).convert_alpha()
            self.cat_img = pygame.transform.scale(self.cat_img, (48, 48))
        except:
            self.cat_img = pygame.Surface((48, 48))
            self.cat_img.fill((255, 200, 100))

        self.obstacle_imgs = []
        try:
            obs_lemon = pygame.image.load(os.path.join(ASSET_DIR, "lemon.png")).convert_alpha()
            obs_orange = pygame.image.load(os.path.join(ASSET_DIR, "orange.png")).convert_alpha()
            obs_water = pygame.image.load(os.path.join(ASSET_DIR, "water.png")).convert_alpha()
            small_orange = pygame.transform.scale(obs_orange, (25, 25))
            medium_lemon = pygame.transform.scale(obs_lemon, (40, 35))
            large_water = pygame.transform.scale(obs_water, (60, 30))
            self.obstacle_imgs = [small_orange, medium_lemon, large_water]
        except:
            small_orange = pygame.Surface((25, 25))
            small_orange.fill((255, 150, 0))
            medium_lemon = pygame.Surface((40, 35))
            medium_lemon.fill((255, 200, 0))
            large_water = pygame.Surface((60, 30))
            large_water.fill((0, 150, 255))
            self.obstacle_imgs = [small_orange, medium_lemon, large_water]

        self.bg_x1 = 0
        self.bg_x2 = WIDTH
        self.bg_speed = 2

        self.cat_x = 60
        self.cat_y = GROUND_Y
        self.cat_vel_y = 0
        self.gravity = 0.8
        self.jump_power = -15
        self.on_ground = True
        self.jump_count = 0
        self.max_jumps = 2
        self.obstacles = []
        self.base_obstacle_speed = 4.0
        self.obstacle_speed = self.base_obstacle_speed
        self.spawn_timer = 0
        self.spawn_delay = 90
        self.min_spawn_meters = 20
        self.max_spawn_meters = 40
        self.pixels_per_meter = 10
        self.next_spawn_frames = self._compute_next_spawn_frames()

        self.distance = 0.0
        self.score = 0

    def update_difficulty(self):
        difficulty_level = int(self.distance) // 100
        self.obstacle_speed = self.base_obstacle_speed + (difficulty_level * 1.0)
        self.spawn_delay = max(50, 90 - (difficulty_level * 5))

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

            self.update_difficulty()

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
        coin_reward = (distance_int // 100) * 20
        return {"distance": distance_int, "coins": coin_reward}

    def _compute_next_spawn_frames(self):
        meters = random.randint(self.min_spawn_meters, self.max_spawn_meters)
        speed = max(0.1, self.obstacle_speed)
        frames = int((meters * self.pixels_per_meter) / speed)
        return max(10, frames)


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
