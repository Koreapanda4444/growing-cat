import pygame
import sys
import os
from minigames.memory_game import MemoryGame

WIDTH = 400
HEIGHT = 600
FPS = 60

ASSETS_DIR = "assets"
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "ThinDungGeunMo.ttf")


class MiniGameScreen:
    def __init__(self, screen, state=None):
        self.screen = screen
        self.state = state
        self.clock = pygame.time.Clock()
        self.running = True

        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
            self.big_font = pygame.font.Font(FONT_PATH, 22)
        except:
            self.font = pygame.font.Font(None, 18)
            self.big_font = pygame.font.Font(None, 22)

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
                if self.selected == "memory" and self.state:
                    MemoryGame(self.screen, self.state).run()
                self.running = False

    def draw_card(self, rect, title, selected=False):
        color = (200, 220, 200) if selected else (220, 220, 220)
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

        self.draw_card(self.card_avoid, "장애물 피하기", self.selected == "jump")
        self.draw_card(self.card_memory, "메모리 게임", self.selected == "memory")

        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_start)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_start, 1)
        self.screen.blit(self.font.render("시작하기", True, (0, 0, 0)), self.font.render("시작하기", True, (0, 0, 0)).get_rect(center=self.btn_start.center))

        pygame.display.flip()
