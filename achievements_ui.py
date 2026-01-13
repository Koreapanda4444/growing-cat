import pygame

from config import asset_path
from pg_utils import load_font

BG_COLOR = (245, 245, 245)
PANEL_COLOR = (230, 230, 230)
BORDER = (0, 0, 0)

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")


class AchievementsUI:
    def __init__(self, screen, ach, play_click_sound=None):
        self.screen = screen
        self.ach = ach
        self.play_click_sound = play_click_sound
        self.running = True

        self.font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)

        self.close_rect = pygame.Rect(360, 10, 30, 30)

        self.scroll = 0
        self.row_h = 56
        self.list_top = 80
        self.list_bottom_pad = 20

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.handle_events()
            self.draw()

    def _max_scroll(self, items_count: int) -> int:
        _, screen_h = self.screen.get_size()
        view_h = screen_h - self.list_top - self.list_bottom_pad
        content_h = items_count * self.row_h
        return max(0, int(content_h - view_h))

    def _scroll_by(self, delta: int):
        items = self.ach.get_list() if self.ach else []
        max_scroll = self._max_scroll(len(items))
        self.scroll = max(0, min(int(self.scroll) + int(delta), max_scroll))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.MOUSEWHEEL:
                self._scroll_by(-event.y * 40)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.close_rect.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.running = False
                    return

                if event.button == 4:
                    self._scroll_by(-40)
                elif event.button == 5:
                    self._scroll_by(40)

    def draw_top(self):
        title = self.big_font.render("업적", True, (0, 0, 0))
        self.screen.blit(title, (20, 20))

        pygame.draw.rect(self.screen, PANEL_COLOR, self.close_rect)
        pygame.draw.rect(self.screen, BORDER, self.close_rect, 1)
        x_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))

        if self.ach:
            items = self.ach.get_list()
            unlocked = sum(1 for it in items if it.get("unlocked"))
            total = len(items)
            points = sum(int(it.get("points", 0)) for it in items if it.get("unlocked"))
            meta = self.font.render(f"해금 {unlocked}/{total}  |  점수 {points}", True, (60, 60, 60))
            self.screen.blit(meta, (20, 52))

    def draw_list(self):
        screen_w, screen_h = self.screen.get_size()
        list_rect = pygame.Rect(0, self.list_top, screen_w, screen_h - self.list_top - self.list_bottom_pad)

        if not self.ach:
            msg = self.font.render("업적 데이터를 불러올 수 없습니다.", True, (80, 80, 80))
            self.screen.blit(msg, (20, self.list_top))
            return

        items = self.ach.get_list()
        y = self.list_top - int(self.scroll)

        old_clip = self.screen.get_clip()
        self.screen.set_clip(list_rect)

        for it in items:
            if y < self.list_top - self.row_h:
                y += self.row_h
                continue
            if y > screen_h + self.row_h:
                break

            rect = pygame.Rect(20, y, screen_w - 40, self.row_h - 8)
            if it.get("unlocked"):
                pygame.draw.rect(self.screen, (190, 235, 205), rect)
            else:
                pygame.draw.rect(self.screen, (220, 220, 220), rect)
            pygame.draw.rect(self.screen, BORDER, rect, 1)

            title = self.font.render(f"{it.get('title', '')}  (+{it.get('points', 0)})", True, (0, 0, 0))
            desc = self.font.render(str(it.get("desc", "")), True, (70, 70, 70))
            self.screen.blit(title, (rect.x + 10, rect.y + 6))
            self.screen.blit(desc, (rect.x + 10, rect.y + 30))

            y += self.row_h

        self.screen.set_clip(old_clip)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_top()
        self.draw_list()
        pygame.display.flip()
