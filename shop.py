import pygame
import state as game_state

from config import asset_path
from items import get_shop_categories
from pg_utils import screen_events, GameQuit, load_font, cached_image as load_image

BG_COLOR = (245, 245, 245)
PANEL_COLOR = (230, 230, 230)
BORDER = (0, 0, 0)

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")

class ShopUI:
    def __init__(self, screen, coin, on_buy, play_click_sound=None, difficulty="normal"):
        self.screen = screen
        self.coin = coin
        self.on_buy = on_buy
        self.play_click_sound = play_click_sound
        self.running = True
        self.difficulty = game_state.normalize_difficulty(difficulty)

        self.font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)

        self.close_rect = pygame.Rect(360, 10, 30, 30)

        self.tab_food = pygame.Rect(30, 90, 100, 32)
        self.tab_toy = pygame.Rect(150, 90, 100, 32)
        self.tab_evolution = pygame.Rect(270, 90, 100, 32)
        self.active_tab = "FOOD"

        self.items = get_shop_categories()
        self._apply_difficulty_prices()

        self.item_rects = []
        self.page = 0
        self.prev_rect = pygame.Rect(65, 520, 95, 34)
        self.next_rect = pygame.Rect(240, 520, 95, 34)
        self.message = ''

    def _apply_difficulty_prices(self):
        for category in self.items.values():
            for item in category:
                item["price"] = game_state.get_shop_price(item["price"], self.difficulty)

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

                if self.tab_food.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.active_tab = "FOOD"
                    self.page = 0
                    self.item_rects.clear()
                elif self.tab_toy.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.active_tab = "TOY"
                    self.page = 0
                    self.item_rects.clear()
                elif self.tab_evolution.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.active_tab = "EVOLUTION"
                    self.page = 0
                    self.item_rects.clear()

                for rect, item in self.item_rects:
                    if rect.collidepoint(event.pos):
                        if self.coin >= item["price"]:
                            if self.play_click_sound:
                                self.play_click_sound()
                            ok = self.on_buy(item)
                            if ok:
                                self.coin -= item["price"]
                                self.message = "구매 완료"
                            else:
                                self.message = "구매 실패"
                        else:
                            self.message = "코인 부족"
                        return

    def item_count(self):
        return len(self.items[self.active_tab])

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
        face_rect = pygame.Rect(20, 10, 60, 60)
        pygame.draw.rect(self.screen, (220, 220, 220), face_rect)
        pygame.draw.rect(self.screen, BORDER, face_rect, 2)

        coin_box = pygame.Rect(100, 20, 160, 30)
        pygame.draw.rect(self.screen, PANEL_COLOR, coin_box)
        pygame.draw.rect(self.screen, BORDER, coin_box, 1)

        coin_text = self.font.render(f"코인: {self.coin}", True, (0, 0, 0))
        self.screen.blit(coin_text, (coin_box.x + 10, coin_box.y + 6))

        pygame.draw.rect(self.screen, PANEL_COLOR, self.close_rect)
        pygame.draw.rect(self.screen, BORDER, self.close_rect, 1)
        x_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))

    def draw_tabs(self):
        for rect, label, key in [
            (self.tab_food, "음식", "FOOD"),
            (self.tab_toy, "장난감", "TOY"),
            (self.tab_evolution, "진화", "EVOLUTION")
        ]:
            color = (210, 210, 210) if self.active_tab == key else (235, 235, 235)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, BORDER, rect, 1)
            txt = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw_items(self):
        self.item_rects.clear()
        items = self.items[self.active_tab][self.page * 4:(self.page + 1) * 4]

        start_x = 40
        start_y = 150
        gap = 30
        size = 80

        for i, item in enumerate(items):
            x = start_x + (i % 2) * (size + gap + 20)
            y = start_y + (i // 2) * (size + 70)

            icon_rect = pygame.Rect(x, y, size, size)
            pygame.draw.rect(self.screen, (220, 220, 220), icon_rect)
            pygame.draw.rect(self.screen, BORDER, icon_rect, 2)

            img = load_image(item["image"], size=(size - 4, size - 4), smooth=False)
            if img:
                self.screen.blit(img, (x + 2, y + 2))

            name = self.font.render(item["name"], True, (0, 0, 0))
            self.screen.blit(name, (x + 4, y + size + 4))

            price = self.font.render(f"{item['price']} 코인", True, (80, 80, 80))
            self.screen.blit(price, (x + 4, y + size + 22))

            self.item_rects.append((icon_rect, item))

    def draw(self):
        self.change_page(0)
        self.screen.fill(BG_COLOR)
        self.draw_top()
        self.draw_tabs()
        self.draw_items()
        self.draw_pagination()
        pygame.display.flip()
