import pygame
import save
import os

WIDTH = 400
HEIGHT = 600
FONT_PATH = os.path.join("assets", "fonts", "ThinDungGeunMo.ttf")

class SettingsScreen:
    def __init__(self, screen, restart_callback):
        self.screen = screen
        self.restart_callback = restart_callback
        self.running = True

        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
            self.big_font = pygame.font.Font(FONT_PATH, 22)
        except:
            self.font = pygame.font.Font(None, 20)
            self.big_font = pygame.font.Font(None, 26)

        self.reset_rect = pygame.Rect(100, 300, 200, 44)
        self.back_rect = pygame.Rect(100, 360, 200, 36)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.handle_events()
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.reset_rect.collidepoint(event.pos):
                    save.reset_save()
                    self.restart_callback()
                    self.running = False

                elif self.back_rect.collidepoint(event.pos):
                    self.running = False

    def draw_button(self, rect, text):
        pygame.draw.rect(self.screen, (230, 230, 230), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        txt = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(40, 200, 320, 240)
        pygame.draw.rect(self.screen, (245, 245, 245), panel, border_radius=12)
        pygame.draw.rect(self.screen, (0, 0, 0), panel, 2, border_radius=12)

        title = self.big_font.render("설정", True, (0, 0, 0))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 230)))

        self.draw_button(self.reset_rect, "데이터 초기화")
        self.draw_button(self.back_rect, "뒤로가기")

        pygame.display.flip()
