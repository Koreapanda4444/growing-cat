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

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("고양이 키우기")

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.bg_color = (240, 240, 240)

        self.back_image = self.load_image(BACK_IMAGE)
        self.back_image = pygame.transform.scale(self.back_image, (WIDTH, HEIGHT))
        self.back_rect = self.back_image.get_rect(topleft=(0, 0))
        pygame.font.init()
        FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "ThinDungGeunMo.ttf")
        try:
            self.font = pygame.font.Font(FONT_PATH, 22)
        except:
            self.font = pygame.font.Font(None, 28)

        self.state = state.GameState()
        self.cat = Cat()

        self.btn_time = pygame.Rect(100, 520, 200, 40)

        self.btn_feed = pygame.Rect(30, 420, 150, 40)
        self.btn_play = pygame.Rect(220, 420, 150, 40)
        self.btn_clean = pygame.Rect(100, 470, 200, 40)

    def load_image(self, filename):
        path = os.path.join(ASSETS_DIR, filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except pygame.error as e:
            print(f"[ERROR] 이미지 로드 실패: {path}")
            print(e)
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
        if self.btn_time.collidepoint(pos):
            self.advance_time()
            return

        if self.btn_feed.collidepoint(pos):
            self.cat.feed_free()

        elif self.btn_play.collidepoint(pos):
            self.cat.play_free()

        elif self.btn_clean.collidepoint(pos):
            self.cat.clean()

    def advance_time(self):
        phase = self.state.advance_time()

        if phase == state.NIGHT:
            self.cat.on_night()
        else:
            self.cat.on_morning()

    def draw_bar(self, x, y, label, value, color):
        width = 300
        height = 18

        ratio = value / state.MAX_STAT
        fill = int(width * ratio)

        text = self.font.render(f"{label}: {int(value)}", True, (0, 0, 0))
        self.screen.blit(text, (x, y - 18))

        pygame.draw.rect(self.screen, (0, 0, 0), (x, y, width, height), 2)
        pygame.draw.rect(
            self.screen,
            color,
            (x + 2, y + 2, max(0, fill - 4), height - 4)
        )

    def draw_button(self, rect, text, enabled=True):
        color = (220, 220, 220) if enabled else (160, 160, 160)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)

        txt = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        self.screen.fill(self.bg_color)
        self.screen.blit(self.back_image, self.back_rect)

        info = f"{self.state.day}일차 - {'아침' if self.state.time_phase == state.MORNING else '밤'}"
        self.screen.blit(self.font.render(info, True, (0, 0, 0)), (20, 20))

        self.draw_bar(50, 80, "배고픔", self.cat.hunger, (255, 100, 100))
        self.draw_bar(50, 130, "피로", self.cat.tiredness, (100, 100, 255))
        self.draw_bar(50, 180, "행복", self.cat.happiness, (100, 255, 100))
        self.draw_bar(50, 230, "청결", self.cat.cleanliness, (180, 180, 180))

        is_morning = self.state.time_phase == state.MORNING

        self.draw_button(self.btn_feed, "밥주기", True)
        self.draw_button(self.btn_play, "놀이주기", True)
        self.draw_button(self.btn_clean, "씻기기", True)

        time_text = "밤으로 보내기" if is_morning else "다음날 아침"
        self.draw_button(self.btn_time, time_text, True)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
