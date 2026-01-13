import pygame
import random
import os

from config import asset_path
from pg_utils import load_font

WIDTH = 400
HEIGHT = 600

GRID_COLS = 4
GRID_ROWS = 4
CARD_SIZE = 72
CARD_GAP = 10

BOARD_X = 30
BOARD_Y = 90

ASSET_DIR = asset_path("minigames", "memory_game")
FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")

class MemoryGame:
    def __init__(self, screen, state):
        self.screen = screen
        self.state = state
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = load_font(FONT_PATH, 22)
        self.small_font = load_font(FONT_PATH, 16)

        self.cards = []
        self.first = None
        self.second = None
        self.lock = False
        self.fail_count = 0

        self.board_margin_x = 20
        self.board_top = 140
        self.board_bottom = HEIGHT - 60
        self.card_gap = 12
        avail_w = WIDTH - 2 * self.board_margin_x
        avail_h = self.board_bottom - self.board_top
        card_w = (avail_w - (GRID_COLS - 1) * self.card_gap) / GRID_COLS
        card_h = (avail_h - (GRID_ROWS - 1) * self.card_gap) / GRID_ROWS
        self.card_size = int(min(card_w, card_h))
        used_w = GRID_COLS * self.card_size + (GRID_COLS - 1) * self.card_gap
        used_h = GRID_ROWS * self.card_size + (GRID_ROWS - 1) * self.card_gap
        self.board_x = (WIDTH - used_w) // 2
        self.board_y = self.board_top + (avail_h - used_h) // 2
        self.started = False
        self.reveal_end_ms = None
        self.limit_start_ms = None
        self.time_limit_ms = 30000

        self.back_image = None
        back_path = os.path.join(ASSET_DIR, "memoryback.png")
        try:
            img = pygame.image.load(back_path).convert_alpha()
            self.back_image = pygame.transform.smoothscale(img, (self.card_size, self.card_size))
        except:
            self.back_image = None
        if self.back_image is None:
            self.back_image = pygame.Surface((self.card_size, self.card_size))
            self.back_image.fill((180, 180, 180))

        self.load_cards()

    def load_cards(self):
        all_ids = list(range(1, 17))
        chosen = random.sample(all_ids, 8)

        colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
            (255, 100, 255), (100, 255, 255), (255, 150, 100), (150, 100, 255)
        ]

        images = {}
        for idx, cid in enumerate(chosen):
            img_surface = None
            path = os.path.join(ASSET_DIR, f"memory{cid}.png")
            try:
                img_surface = pygame.image.load(path).convert_alpha()
                img_surface = pygame.transform.smoothscale(img_surface, (self.card_size, self.card_size))
            except:
                img_surface = None
            if img_surface is None:
                img_surface = pygame.Surface((self.card_size, self.card_size))
                img_surface.fill(colors[idx % len(colors)])
            images[cid] = img_surface

        ids = chosen * 2
        random.shuffle(ids)

        self.cards.clear()
        for i, cid in enumerate(ids):
            x = self.board_x + (i % GRID_COLS) * (self.card_size + self.card_gap)
            y = self.board_y + (i // GRID_COLS) * (self.card_size + self.card_gap)

            self.cards.append({
                "id": cid,
                "image": images[cid],
                "rect": pygame.Rect(x, y, self.card_size, self.card_size),
                "revealed": True,
                "matched": False
            })

        now = pygame.time.get_ticks()
        self.reveal_end_ms = now + 3000

    def handle_click(self, pos):
        if self.lock or not self.started:
            return

        for card in self.cards:
            if (
                card["rect"].collidepoint(pos)
                and not card["revealed"]
                and not card["matched"]
            ):
                card["revealed"] = True

                if not self.first:
                    self.first = card
                elif not self.second:
                    self.second = card
                    self.check_match()
                break

    def check_match(self):
        if self.first["id"] == self.second["id"]:
            self.first["matched"] = True
            self.second["matched"] = True
            self.first = None
            self.second = None
        else:
            self.lock = True
            self.fail_count += 1
            pygame.time.set_timer(pygame.USEREVENT, 700)

    def update(self):
        now = pygame.time.get_ticks()
        if not self.started and self.reveal_end_ms and now >= self.reveal_end_ms:
            for c in self.cards:
                if not c["matched"]:
                    c["revealed"] = False
            self.started = True
            self.limit_start_ms = now

        if all(c["matched"] for c in self.cards):
            reward = max(10, 100 - 10 * self.fail_count)
            if self.state is not None:
                try:
                    self.state.money = max(0, int(self.state.money) + int(reward))
                except (TypeError, ValueError):
                    self.state.money = max(0, int(reward))
            self.running = False
            return

        if self.started and self.limit_start_ms and now - self.limit_start_ms > self.time_limit_ms:
            self.running = False

    def draw(self):
        self.screen.fill((245, 245, 245))

        title = self.font.render("메모리 게임", True, (0, 0, 0))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        info = self.small_font.render(
            f"실수 횟수: {self.fail_count}", True, (80, 80, 80)
        )
        self.screen.blit(info, (20, 60))

        if self.started and self.limit_start_ms:
            now = pygame.time.get_ticks()
            remain_ms = max(0, self.time_limit_ms - (now - self.limit_start_ms))
            remain_s = round(remain_ms / 1000, 1)
            t = self.small_font.render(f"남은 시간: {remain_s}초", True, (120, 80, 80))
            self.screen.blit(t, (WIDTH - t.get_width() - 20, 60))

        for card in self.cards:
            if card["revealed"] or card["matched"]:
                self.screen.blit(card["image"], (card["rect"].x, card["rect"].y))
            else:
                self.screen.blit(self.back_image, (card["rect"].x, card["rect"].y))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

                elif event.type == pygame.USEREVENT:
                    self.first["revealed"] = False
                    self.second["revealed"] = False
                    self.first = None
                    self.second = None
                    self.lock = False
                    pygame.time.set_timer(pygame.USEREVENT, 0)

            self.update()
            self.draw()
