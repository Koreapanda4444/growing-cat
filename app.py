import pygame
import sys
import os

from cat import Cat
import state


WIDTH = 400
HEIGHT = 600
FPS = 60

ASSETS_DIR = "assets"
BACK_IMAGE = "ui/background.png"
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "ThinDungGeunMo.ttf")

INFO_X = 8
INFO_Y = 18

STAT_X = 235
STAT_Y_START = 28
STAT_GAP = 38
BAR_HEIGHT = 10
BAR_WIDTH = 155

TAB_Y = 550
TAB_W = 100
TAB_H = 34

PANEL_W = 110
PANEL_BTN_H = 26
PANEL_GAP = 4
PANEL_Y = 270

ARROW_RECT = pygame.Rect(365, 320, 24, 44)


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("고양이 키우기")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.back_image = self.load_image(BACK_IMAGE)
        self.back_image = pygame.transform.scale(self.back_image, (WIDTH, HEIGHT))
        self.back_rect = self.back_image.get_rect(topleft=(0, 0))

        pygame.font.init()
        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
            self.panel_font = pygame.font.Font(FONT_PATH, 17)
            self.tab_font = pygame.font.Font(FONT_PATH, 18)
            self.stat_font = pygame.font.Font(FONT_PATH, 16)
        except:
            self.font = pygame.font.Font(None, 18)
            self.panel_font = pygame.font.Font(None, 17)
            self.tab_font = pygame.font.Font(None, 18)
            self.stat_font = pygame.font.Font(None, 16)

        self.state = state.GameState()
        self.cat = Cat()

        self.panel_open = False

        self.btn_shop = pygame.Rect(20, TAB_Y, TAB_W, TAB_H)
        self.btn_minigame = pygame.Rect(150, TAB_Y, TAB_W, TAB_H)
        self.btn_bag = pygame.Rect(280, TAB_Y, TAB_W, TAB_H)

    def load_image(self, filename):
        path = os.path.join(ASSETS_DIR, filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except:
            pygame.quit()
            sys.exit()

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.draw()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        if not self.panel_open and ARROW_RECT.collidepoint(pos):
            self.panel_open = True
            return

        if self.panel_open:
            panel_x = WIDTH - PANEL_W - 8
            close_rect = pygame.Rect(panel_x, PANEL_Y - PANEL_BTN_H - 4, PANEL_W, PANEL_BTN_H)
            if close_rect.collidepoint(pos):
                self.panel_open = False
                return

            actions = [
                self.cat.feed_free,
                self.cat.play_free,
                self.cat.clean,
                self.advance_time,   # ⭐ 잠자기 = 시간 진행
            ]

            for i, action in enumerate(actions):
                r = pygame.Rect(
                    panel_x,
                    PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP),
                    PANEL_W,
                    PANEL_BTN_H
                )
                if r.collidepoint(pos):
                    action()
                    return

    def advance_time(self):
        phase = self.state.advance_time()
        if phase == state.NIGHT:
            self.cat.on_night()
        else:
            self.cat.on_morning()

    def draw_bar(self, x, y, label, value, color):
        ratio = value / state.MAX_STAT
        fill = int(BAR_WIDTH * ratio)

        text = self.stat_font.render(f"{label}: {int(value)}", True, (0, 0, 0))
        self.screen.blit(text, (x, y - 14))

        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, BAR_WIDTH, BAR_HEIGHT), 1)
        pygame.draw.rect(
            self.screen,
            color,
            (x + 2, y + 2, max(0, fill - 4), BAR_HEIGHT - 4)
        )

    def draw_button(self, rect, text, font):
        pygame.draw.rect(self.screen, (220, 220, 220), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        txt = font.render(text, True, (0, 0, 0))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        self.screen.blit(self.back_image, self.back_rect)

        info = f"{self.state.day}일차 - {'아침' if self.state.time_phase == state.MORNING else '밤'}"
        self.screen.blit(self.font.render(info, True, (0, 0, 0)), (INFO_X, INFO_Y))

        self.draw_bar(STAT_X, STAT_Y_START, "배고픔", self.cat.hunger, (255, 100, 100))
        self.draw_bar(STAT_X, STAT_Y_START + STAT_GAP, "피로", self.cat.tiredness, (100, 100, 255))
        self.draw_bar(STAT_X, STAT_Y_START + 2 * STAT_GAP, "행복", self.cat.happiness, (100, 255, 100))
        self.draw_bar(STAT_X, STAT_Y_START + 3 * STAT_GAP, "청결", self.cat.cleanliness, (180, 180, 180))

        if not self.panel_open:
            pygame.draw.rect(self.screen, (200, 200, 200), ARROW_RECT)
            pygame.draw.rect(self.screen, (0, 0, 0), ARROW_RECT, 1)
            arrow = self.font.render("▶", True, (0, 0, 0))
            self.screen.blit(arrow, arrow.get_rect(center=ARROW_RECT.center))

        if self.panel_open:
            panel_x = WIDTH - PANEL_W - 8
            panel_h = 4 * (PANEL_BTN_H + PANEL_GAP) + PANEL_BTN_H

            pygame.draw.rect(
                self.screen,
                (230, 230, 230),
                (panel_x, PANEL_Y - PANEL_BTN_H - 6, PANEL_W, panel_h)
            )
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),
                (panel_x, PANEL_Y - PANEL_BTN_H - 6, PANEL_W, panel_h),
                1
            )

            self.draw_button(
                pygame.Rect(panel_x, PANEL_Y - PANEL_BTN_H - 4, PANEL_W, PANEL_BTN_H),
                "◀ 닫기",
                self.panel_font
            )

            labels = ["밥", "놀기", "씻기", "잠자기"]
            for i, label in enumerate(labels):
                r = pygame.Rect(
                    panel_x,
                    PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP),
                    PANEL_W,
                    PANEL_BTN_H
                )
                self.draw_button(r, label, self.panel_font)

        self.draw_button(self.btn_shop, "상점", self.tab_font)
        self.draw_button(self.btn_minigame, "미니게임", self.tab_font)
        self.draw_button(self.btn_bag, "가방", self.tab_font)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
