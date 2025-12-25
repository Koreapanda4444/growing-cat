import pygame
import os

WIDTH = 400
HEIGHT = 600

BG_COLOR = (245, 245, 245)
PANEL_COLOR = (230, 230, 230)
BORDER = (0, 0, 0)

ASSETS_DIR = "assets"
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "ThinDungGeunMo.ttf")

class BagUI:
    def __init__(self, screen, inventory, on_use, play_click_sound=None):
        self.screen = screen
        self.inventory = inventory
        self.on_use = on_use
        self.play_click_sound = play_click_sound
        self.running = True

        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
            self.big_font = pygame.font.Font(FONT_PATH, 22)
        except:
            self.font = pygame.font.Font(None, 18)
            self.big_font = pygame.font.Font(None, 22)

        self.close_rect = pygame.Rect(360, 10, 30, 30)

        self.item_rects = []

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
                if self.close_rect.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.running = False
                    return

                for rect, item in self.item_rects:
                    if rect.collidepoint(event.pos):
                        if self.inventory[item] > 0:
                            if self.play_click_sound:
                                self.play_click_sound()
                            self.inventory[item] -= 1
                            self.on_use(item)
                            return

    def draw_top(self):
        title = self.big_font.render("가방", True, (0, 0, 0))
        self.screen.blit(title, (20, 20))

        pygame.draw.rect(self.screen, PANEL_COLOR, self.close_rect)
        pygame.draw.rect(self.screen, BORDER, self.close_rect, 1)
        x_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))

    def draw_items(self):
        self.item_rects.clear()

        start_x = 40
        start_y = 80
        size = 100
        gap = 30

        items = list(self.inventory.keys())

        for i, item in enumerate(items):
            x = start_x + (i % 2) * (size + gap)
            y = start_y + (i // 2) * (size + 50)

            icon_rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.screen, (220, 220, 220), icon_rect)
            pygame.draw.rect(self.screen, BORDER, icon_rect, 2)

            name = self.font.render(item, True, (0, 0, 0))
            self.screen.blit(name, (x + 6, y + size + 4))

            count = self.font.render(f"x {self.inventory[item]}", True, (80, 80, 80))
            self.screen.blit(count, (x + 6, y + size + 22))

            self.item_rects.append((icon_rect, item))

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_top()
        self.draw_items()
        pygame.display.flip()
