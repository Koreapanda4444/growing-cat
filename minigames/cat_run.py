import pygame
import random
import sys
import os
ASSET_DIRS = [
    os.path.join("assets", "minigames", "cat_run"),
]
FONT_PATH = os.path.join(ASSET_DIRS[0], "fonts", "ThinDungGeunMo.ttf")

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
            obs_lemon = pygame.image.load(os.path.join(ASSET_DIRS[0], "lemon.png")).convert_alpha()
            obs_orange = pygame.image.load(os.path.join(ASSET_DIRS[0], "orange.png")).convert_alpha()
            obs_water = pygame.image.load(os.path.join(ASSET_DIRS[0], "water.png")).convert_alpha()
            # 요청 크기: 귤 25x25, 레몬 40x35, 물 60x30
            small_orange = pygame.transform.scale(obs_orange, (25, 25))
            medium_lemon = pygame.transform.scale(obs_lemon, (40, 35))
            large_water = pygame.transform.scale(obs_water, (60, 30))
            self.obstacle_imgs = [small_orange, medium_lemon, large_water]
        except:
            # 이미지 로드 실패 시 요청 크기에 맞춘 대체 도형 생성
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
        # 이단점프 처리 변수
        self.jump_count = 0
        self.max_jumps = 2

        # 대쉬 제거됨

        self.obstacles = []
        # 시작 속도 낮춤: 기본 장애물 속도를 더 낮게 설정
        self.base_obstacle_speed = 3.0
        self.obstacle_speed = self.base_obstacle_speed
        self.spawn_timer = 0
        self.spawn_delay = 90  # 기존 값은 유지하지만, 아래 랜덤 간격 로직을 사용
        # 장애물 간격을 5~15m로 랜덤화하기 위한 설정
        self.min_spawn_meters = 15
        self.max_spawn_meters = 30
        self.pixels_per_meter = 10
        self.next_spawn_frames = self._compute_next_spawn_frames()

        self.distance = 0
        self.score = 0

    def update_difficulty(self):
        # 진행 거리 기반 난이도 조정
        difficulty_level = self.distance // 100
        self.obstacle_speed = self.base_obstacle_speed + (difficulty_level * 0.5)
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

        self.cat_vel_y += self.gravity
        self.cat_y += self.cat_vel_y
        if self.cat_y >= GROUND_Y:
            self.cat_y = GROUND_Y
            self.cat_vel_y = 0
            self.on_ground = True
            # 착지 시 점프 카운트 초기화
            self.jump_count = 0

        # 대쉬 제거: 수평 이동 및 쿨다운 로직 삭제

        cat_rect = pygame.Rect(self.cat_x, self.cat_y, 48, 48)

        # 장애물 스폰: 5~15m 사이 랜덤 간격을 프레임로 환산하여 사용
        self.spawn_timer += 1
        if self.spawn_timer >= self.next_spawn_frames:
            self.spawn_timer = 0
            img = random.choice(self.obstacle_imgs)
            rect = img.get_rect(midbottom=(WIDTH + 40, GROUND_Y + 48))
            self.obstacles.append((img, rect))
            # 다음 스폰 간격 재계산
            self.next_spawn_frames = self._compute_next_spawn_frames()
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

    def _compute_next_spawn_frames(self):
        # 현재 장애물 속도 기준으로 5~15m를 프레임 수로 환산
        meters = random.randint(self.min_spawn_meters, self.max_spawn_meters)
        # 속도가 너무 작을 때 division 방지
        speed = max(0.1, self.obstacle_speed)
        frames = int((meters * self.pixels_per_meter) / speed)
        # 너무 짧은 간격 방지
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
