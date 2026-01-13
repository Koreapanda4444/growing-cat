import pygame
import sys
import os
from minigames.memory_game import MemoryGame
from minigames.cat_run import CatRunGame

from config import asset_path
from pg_utils import load_font

WIDTH = 400
HEIGHT = 600
FPS = 60

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")


class MiniGameScreen:
    def __init__(self, screen, state=None):
        self.screen = screen
        self.state = state
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)

        self.selected = None

        self.btn_close = pygame.Rect(350, 10, 36, 36)
        self.card_avoid = pygame.Rect(40, 150, 320, 110)
        self.card_memory = pygame.Rect(40, 280, 320, 110)
        self.btn_start = pygame.Rect(260, 510, 110, 36)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        if self.btn_close.collidepoint(pos):
            self.running = False
        elif self.card_avoid.collidepoint(pos):
            self.selected = "jump"
        elif self.card_memory.collidepoint(pos):
            self.selected = "memory"
        elif self.btn_start.collidepoint(pos):
            if self.selected:
                if self.selected == "jump" and self.state:
                    if getattr(self.state, "minigame_used", {}).get("jump"):
                        return
                    result = CatRunGame(self.screen, self.state).run()
                    if result and self.state:
                        try:
                            coins = int(result.get("coins", 0))
                        except (TypeError, ValueError):
                            coins = 0
                        coins = max(0, coins)
                        try:
                            self.state.money = max(0, int(self.state.money) + coins)
                        except (TypeError, ValueError):
                            self.state.money = coins
                    self.state.minigame_used["jump"] = True
                elif self.selected == "memory" and self.state:
                    if getattr(self.state, "minigame_used", {}).get("memory"):
                        return
                    MemoryGame(self.screen, self.state).run()
                    self.state.minigame_used["memory"] = True
                self.running = False

    def draw_card(self, rect, title, selected=False, disabled=False):
        color = (220, 220, 220)
        if selected:
            color = (200, 220, 200) if not disabled else (220, 120, 120)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
        txt = self.font.render(title, True, (0, 0, 0))
        self.screen.blit(txt, (rect.x + 20, rect.y + 20))

    def draw(self):
        self.screen.fill((235, 235, 235))

        self.screen.blit(self.big_font.render("미니게임", True, (0, 0, 0)), (20, 20))

        pygame.draw.rect(self.screen, (220, 220, 220), self.btn_close)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_close, 1)
        self.screen.blit(self.font.render("X", True, (0, 0, 0)), self.font.render("X", True, (0, 0, 0)).get_rect(center=self.btn_close.center))

        used_jump = getattr(self.state, "minigame_used", {}).get("jump", False) if self.state else False
        used_memory = getattr(self.state, "minigame_used", {}).get("memory", False) if self.state else False
        self.draw_card(self.card_avoid, "장애물 피하기", self.selected == "jump", used_jump)
        self.draw_card(self.card_memory, "메모리 게임", self.selected == "memory", used_memory)

        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_start)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_start, 1)
        self.screen.blit(self.font.render("시작하기", True, (0, 0, 0)), self.font.render("시작하기", True, (0, 0, 0)).get_rect(center=self.btn_start.center))

        pygame.display.flip()
