import pygame

from config import asset_path
from items import get_item_info
from pg_utils import screen_events, GameQuit, load_font, cached_image as load_image

BG_COLOR = (245, 245, 245)
PANEL_COLOR = (230, 230, 230)
BORDER = (0, 0, 0)

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")

class BagUI:
    def __init__(self, screen, inventory, on_use, play_click_sound=None):
        self.screen = screen
        self.inventory = inventory
        self.on_use = on_use
        self.play_click_sound = play_click_sound
        self.running = True

        self.font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)

        self.close_rect = pygame.Rect(360, 10, 30, 30)
        self.item_rects = []
        self.page = 0
        self.prev_rect = pygame.Rect(65, 520, 95, 34)
        self.next_rect = pygame.Rect(240, 520, 95, 34)
        self.message = ''

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.handle_events()
            if self.running:
                self.draw()

    def handle_events(self):
        for event in screen_events():
            if event.type == pygame.QUIT:
                raise GameQuit

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.change_page(-1 if event.key == pygame.K_LEFT else 1)
                    return

            elif event.type == pygame.MOUSEWHEEL:
                self.change_page(-event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.prev_rect.collidepoint(event.pos):
                    self.change_page(-1)
                    return
                if self.next_rect.collidepoint(event.pos):
                    self.change_page(1)
                    return
                if self.close_rect.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.running = False
                    return

                for rect, item in self.item_rects:
                    if rect.collidepoint(event.pos):
                        if self.inventory.get(item, 0) > 0:
                            if self.play_click_sound:
                                self.play_click_sound()
                            previous = self.inventory.get(item, 0)
                            self.on_use(item)
                            self.message = "사용 완료" if self.inventory.get(item, 0) < previous else "사용 불가"
                            return

    def item_count(self):
        return sum(count > 0 for count in self.inventory.values())

    def change_page(self, delta):
        last = max(0, (self.item_count() - 1) // 4)
        page = max(0, min(last, self.page + delta))
        if self.page != page:
            self.item_rects.clear()
        self.page = page

    def draw_pagination(self):
        self.change_page(0)
        for rect, label in ((self.prev_rect, "이전"), (self.next_rect, "다음")):
            pygame.draw.rect(self.screen, PANEL_COLOR, rect)
            pygame.draw.rect(self.screen, BORDER, rect, 1)
            caption = self.font.render(label, True, BORDER)
            self.screen.blit(caption, caption.get_rect(center=rect.center))
        pages = max(1, (self.item_count() + 3) // 4)
        page_text = self.font.render(f"{self.page + 1}/{pages}", True, BORDER)
        self.screen.blit(page_text, page_text.get_rect(center=(200, 537)))
        if self.message:
            feedback = self.font.render(self.message, True, (40, 90, 60))
            self.screen.blit(feedback, feedback.get_rect(center=(200, 575)))

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
        size = 80
        gap = 30

        items = [
            item_id
            for item_id, count in self.inventory.items()
            if count > 0
        ]

        for i, item_id in enumerate(items[self.page * 4:(self.page + 1) * 4]):
            x = start_x + (i % 2) * (size + gap + 20)
            y = start_y + (i // 2) * (size + 70)

            icon_rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.screen, (220, 220, 220), icon_rect)
            pygame.draw.rect(self.screen, BORDER, icon_rect, 2)

            item_info = get_item_info(item_id)
            img = load_image(item_info.get("image", ""), size=(size - 4, size - 4), smooth=False)
            if img:
                self.screen.blit(img, (x + 2, y + 2))

            name = self.font.render(item_info.get("name", item_id), True, (0, 0, 0))
            self.screen.blit(name, (x + 6, y + size + 4))

            count = self.font.render(f"x {self.inventory[item_id]}", True, (80, 80, 80))
            self.screen.blit(count, (x + 6, y + size + 22))

            self.item_rects.append((icon_rect, item_id))

    def draw(self):
        self.change_page(0)
        self.screen.fill(BG_COLOR)
        self.draw_top()
        self.draw_items()
        self.draw_pagination()
        pygame.display.flip()
