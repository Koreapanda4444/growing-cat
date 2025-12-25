import pygame
import os

WIDTH = 400
HEIGHT = 600

BG_COLOR = (245, 245, 245)
PANEL_COLOR = (230, 230, 230)
BORDER = (0, 0, 0)

ASSETS_DIR = "assets"
FONT_PATH = os.path.join(ASSETS_DIR, "fonts", "ThinDungGeunMo.ttf")

class ShopUI:
    def __init__(self, screen, coin, on_buy, play_click_sound=None):
        self.screen = screen
        self.coin = coin
        self.on_buy = on_buy
        self.play_click_sound = play_click_sound
        self.running = True

        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
            self.big_font = pygame.font.Font(FONT_PATH, 22)
        except:
            self.font = pygame.font.Font(None, 18)
            self.big_font = pygame.font.Font(None, 22)

        self.close_rect = pygame.Rect(360, 10, 30, 30)

        self.tab_food = pygame.Rect(30, 90, 100, 32)
        self.tab_toy = pygame.Rect(150, 90, 100, 32)
        self.tab_evolution = pygame.Rect(270, 90, 100, 32)
        self.active_tab = "FOOD"

        self.items = {
            "FOOD": [
                {"name": "밥", "price": 30, "id": "bab", "image": "assets/foods/bab.png"},
                {"name": "생선", "price": 50, "id": "fish", "image": "assets/foods/fish.png"},
                {"name": "츄르", "price": 80, "id": "chur", "image": "assets/foods/chur.png"},
            ],
            "TOY": [
                {"name": "강아지풀", "price": 30, "id": "doggrass", "image": "assets/toys/doggrass.png"},
                {"name": "낚싯대", "price": 50, "id": "fishing", "image": "assets/toys/fishing.png"},
                {"name": "실", "price": 40, "id": "string", "image": "assets/toys/string.png"},
            ],
            "EVOLUTION": [
                {"name": "고기", "price": 100, "id": "meat", "image": "assets/evolution/meat.png"},
                {"name": "뼈", "price": 300, "id": "bone", "image": "assets/evolution/bone.png"},
            ]
        }

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

                if self.tab_food.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.active_tab = "FOOD"
                elif self.tab_toy.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.active_tab = "TOY"
                elif self.tab_evolution.collidepoint(event.pos):
                    if self.play_click_sound:
                        self.play_click_sound()
                    self.active_tab = "EVOLUTION"

                for rect, item in self.item_rects:
                    if rect.collidepoint(event.pos):
                        if self.coin >= item["price"]:
                            if self.play_click_sound:
                                self.play_click_sound()
                            ok = self.on_buy(item)
                            if ok:
                                self.coin -= item["price"]

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
        items = self.items[self.active_tab]

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

            try:
                img = pygame.image.load(item["image"]).convert_alpha()
                img = pygame.transform.scale(img, (size - 4, size - 4))
                self.screen.blit(img, (x + 2, y + 2))
            except:
                pass

            name = self.font.render(item["name"], True, (0, 0, 0))
            self.screen.blit(name, (x + 4, y + size + 4))

            price = self.font.render(f"{item['price']} 코인", True, (80, 80, 80))
            self.screen.blit(price, (x + 4, y + size + 22))

            self.item_rects.append((icon_rect, item))

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_top()
        self.draw_tabs()
        self.draw_items()
        pygame.display.flip()
