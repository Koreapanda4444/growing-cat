import pygame
import random
import sys
import os
ASSET_DIRS = [
    os.path.join("assets", "minigames", "cat_run"),
]
FONT_PATH = os.path.join(ASSET_DIRS[0], "fonts", "ThinDungGeunMo.ttf")

WIDTH, HEIGHT = 400, 300
FPS = 60
GROUND_Y = 230


class CatRunGame:
    def __init__(self, screen, state=None, on_game_end=None):
        self.screen = screen
        self.state = state
        self.on_game_end = on_game_end
        self.clock = pygame.time.Clock()
        self.running = True

        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
        except:
            self.font = pygame.font.SysFont(None, 24)

        try:
            self.bg = pygame.image.load(os.path.join(ASSET_DIRS[0], "grass.png")).convert()
            self.bg = pygame.transform.scale(self.bg, (WIDTH, HEIGHT))
        except:
            self.bg = pygame.Surface((WIDTH, HEIGHT))
            self.bg.fill((100, 150, 100))

        try:
            self.cat_img = pygame.image.load(os.path.join(ASSET_DIRS[0], "cat.png")).convert_alpha()
            self.cat_img = pygame.transform.scale(self.cat_img, (48, 48))
        except:
            self.cat_img = pygame.Surface((48, 48))
            self.cat_img.fill((255, 200, 100))

        self.obstacle_imgs = []
        try:
            obs1 = pygame.image.load(os.path.join(ASSET_DIRS[0], "lemon.png")).convert_alpha()
            obs2 = pygame.image.load(os.path.join(ASSET_DIRS[0], "orange.png")).convert_alpha()
            obs3 = pygame.image.load(os.path.join(ASSET_DIRS[0], "water.png")).convert_alpha()
            self.obstacle_imgs = [
                pygame.transform.scale(obs1, (32, 32)),
                pygame.transform.scale(obs2, (32, 32)),
                pygame.transform.scale(obs3, (40, 20)),
            ]
        except:
            for color in [(255, 200, 0), (255, 150, 0), (0, 150, 255)]:
                surf = pygame.Surface((32, 32))
                surf.fill(color)
                self.obstacle_imgs.append(surf)

        self.bg_x1 = 0
        self.bg_x2 = WIDTH
        self.bg_speed = 2

        self.cat_x = 60
        self.cat_y = GROUND_Y
        self.cat_vel_y = 0
        self.gravity = 0.8
        self.jump_power = -12
        self.on_ground = True

        self.obstacles = []
        self.obstacle_speed = 4.0
        self.spawn_timer = 0
        self.spawn_delay = 90

        self.distance = 0
        self.score = 0

    def update_difficulty(self):

        difficulty_level = self.distance // 100
        self.obstacle_speed = 4.0 + (difficulty_level * 0.5)
        self.spawn_delay = max(50, 90 - (difficulty_level * 5))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if event.key == pygame.K_SPACE and self.on_ground:
                    self.cat_vel_y = self.jump_power
                    self.on_ground = False

    def update(self):
        self.bg_x1 -= self.bg_speed
        self.bg_x2 -= self.bg_speed
        if self.bg_x1 <= -WIDTH:
            self.bg_x1 = WIDTH
        if self.bg_x2 <= -WIDTH:
            self.bg_x2 = WIDTH

        self.cat_vel_y += self.gravity
        self.cat_y += self.cat_vel_y
        if self.cat_y >= GROUND_Y:
            self.cat_y = GROUND_Y
            self.cat_vel_y = 0
            self.on_ground = True

        cat_rect = pygame.Rect(self.cat_x, self.cat_y, 48, 48)

        self.spawn_timer += 1
        if self.spawn_timer > self.spawn_delay:
            self.spawn_timer = 0
            img = random.choice(self.obstacle_imgs)
            rect = img.get_rect(midbottom=(WIDTH + 40, GROUND_Y + 48))
            self.obstacles.append((img, rect))
        for obs in self.obstacles[:]:
            obs[1].x -= self.obstacle_speed
            if obs[1].right < 0:
                self.obstacles.remove(obs)
                self.score += 1
                self.distance = int(self.score * 10)
                self.update_difficulty()

            if cat_rect.colliderect(obs[1]):
                self.running = False

    def draw(self):
        self.screen.blit(self.bg, (self.bg_x1, 0))
        self.screen.blit(self.bg, (self.bg_x2, 0))

        self.screen.blit(self.cat_img, (self.cat_x, self.cat_y))

        for obs in self.obstacles:
            self.screen.blit(obs[0], obs[1])

        distance_text = self.font.render(f"{self.distance}m", True, (0, 0, 0))
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
        coin_reward = (self.distance // 100) * 10
        return {"distance": self.distance, "coins": coin_reward}


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
