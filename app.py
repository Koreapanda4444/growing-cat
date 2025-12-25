import pygame
import sys
import os

from cat import Cat
import state
from game import MiniGameScreen
import save


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

BOTTOM_BTN_Y = 540
BOTTOM_BTN_W = 100
BOTTOM_BTN_H = 36
BOTTOM_GAP = 20

PANEL_W = 110
PANEL_BTN_H = 26
PANEL_GAP = 4
PANEL_Y = 300

ARROW_RECT = pygame.Rect(WIDTH - 34, 300, 24, 44)

MAIN_CAT_Y = 450
NAME_Y_OFFSET = 1


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("고양이 키우기")
        pygame.key.start_text_input()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene = "NAMING"
        self.input_name = ""
        self.cursor_visible = True
        self.cursor_timer = 0

        self.back_image = self.load_image(BACK_IMAGE)
        self.back_image = pygame.transform.scale(self.back_image, (WIDTH, HEIGHT))
        self.back_rect = self.back_image.get_rect(topleft=(0, 0))

        try:
            self.coin_image = pygame.image.load(os.path.join(ASSETS_DIR, "ui", "coin.png")).convert_alpha()
            self.coin_image = pygame.transform.smoothscale(self.coin_image, (36, 36))
        except:
            self.coin_image = None

        try:
            self.click_sound = pygame.mixer.Sound(os.path.join(ASSETS_DIR, "sounds", "button.mp3"))
            self.click_sound.set_volume(0.5)
        except:
            self.click_sound = None

        try:
            pygame.mixer.music.load(os.path.join(ASSETS_DIR, "sounds", "bgm.mp3"))
            pygame.mixer.music.set_volume(5)
            pygame.mixer.music.play(-1)
        except:
            pass

        pygame.font.init()
        try:
            self.font = pygame.font.Font(FONT_PATH, 18)
            self.name_font = pygame.font.Font(FONT_PATH, 18)
            self.big_font = pygame.font.Font(FONT_PATH, 22)
            self.panel_font = pygame.font.Font(FONT_PATH, 17)
            self.tab_font = pygame.font.Font(FONT_PATH, 18)
            self.stat_font = pygame.font.Font(FONT_PATH, 16)
            self.hint_font = pygame.font.Font(FONT_PATH, 16)
            self.coin_font = pygame.font.Font(FONT_PATH, 20)
        except:
            self.font = pygame.font.Font(None, 18)
            self.name_font = pygame.font.Font(None, 18)
            self.big_font = pygame.font.Font(None, 22)
            self.panel_font = pygame.font.Font(None, 17)
            self.tab_font = pygame.font.Font(None, 18)
            self.stat_font = pygame.font.Font(None, 16)
            self.hint_font = pygame.font.Font(None, 16)
            self.coin_font = pygame.font.Font(None, 20)

        self.state = state.GameState()
        self.cat = None
        self.panel_open = False
        self.game_over_reason = None
        self.ending_log = {}

        self.load_saved_game()

    def load_saved_game(self):
        data = save.load_game()
        if data and "cat" in data:
            self.state.day = data["day"]
            self.state.time_phase = data["time_phase"]
            
            cat_data = data["cat"]
            self.cat = Cat(cat_data["name"], cat_data["stage"])
            self.cat.hunger = cat_data["hunger"]
            self.cat.tiredness = cat_data["tiredness"]
            self.cat.happiness = cat_data["happiness"]
            self.cat.cleanliness = cat_data["cleanliness"]
            
            self.state.money = data.get("money", 0)
            self.scene = "MAIN"

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

    def advance_time(self):
        phase = self.state.advance_time()
        if phase == state.NIGHT:
            self.cat.on_night()
        else:
            self.cat.on_morning()
            self.state.money += 5

        self.check_game_over()
        save.save_game(self.make_save_data())

    def check_game_over(self):
        result = self.cat.check_game_over()
        if result:
            self.game_over_reason = result
            self.ending_log = {
                "day": self.state.day,
                "hunger": int(self.cat.hunger),
                "tiredness": int(self.cat.tiredness),
                "happiness": int(self.cat.happiness),
                "cleanliness": int(self.cat.cleanliness),
            }
            self.scene = "GAME_OVER"

    def restart_game(self):
        self.state = state.GameState()
        self.cat = None
        self.input_name = ""
        self.scene = "NAMING"
        self.panel_open = False
        self.game_over_reason = None
        self.ending_log = {}

    def make_save_data(self):
        return {
            "day": self.state.day,
            "time_phase": self.state.time_phase,
            "money": self.state.money,
            "cat": {
                "name": self.cat.name,
                "stage": self.cat.stage,
                "hunger": self.cat.hunger,
                "tiredness": self.cat.tiredness,
                "happiness": self.cat.happiness,
                "cleanliness": self.cat.cleanliness
            }
        }

    def spend_money(self, amount):
        if self.state.money >= amount:
            self.state.money -= amount
            return True
        return False

    def play_click_sound(self):
        if self.click_sound:
            self.click_sound.play()

    def open_settings(self):
        from settings import SettingsScreen
        SettingsScreen(self.screen, self.restart_game).run()

    def handle_click_main(self, pos):
        start_x = (WIDTH - (BOTTOM_BTN_W * 3 + BOTTOM_GAP * 2)) // 2
        minigame_rect = pygame.Rect(
            start_x + (BOTTOM_BTN_W + BOTTOM_GAP),
            BOTTOM_BTN_Y,
            BOTTOM_BTN_W,
            BOTTOM_BTN_H
        )
        if minigame_rect.collidepoint(pos):
            MiniGameScreen(self.screen).run()
            return

        if ARROW_RECT.collidepoint(pos):
            self.play_click_sound()
            self.panel_open = not self.panel_open
            return

        if self.panel_open:
            panel_x = WIDTH - PANEL_W - 8

            close_rect = pygame.Rect(
                panel_x,
                PANEL_Y - (PANEL_BTN_H + PANEL_GAP),
                PANEL_W,
                PANEL_BTN_H
            )
            if close_rect.collidepoint(pos):
                self.play_click_sound()
                self.panel_open = False
                return

            labels = ["밥", "놀기", "씻기", "잠자기", "설정"]
            actions = [self.cat.feed_free, self.cat.play_free, self.cat.clean, self.advance_time, self.open_settings]

            for i in range(5):
                r = pygame.Rect(
                    panel_x,
                    PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP),
                    PANEL_W,
                    PANEL_BTN_H
                )
                if r.collidepoint(pos):
                    self.play_click_sound()
                    if i == 4:
                        self.open_settings()
                    elif self.cat:
                        actions[i]()
                        save.save_game(self.make_save_data())
                        self.check_game_over()
                    return

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.scene == "MAIN" and self.cat:
                    save.save_game(self.make_save_data())
                self.running = False

            elif event.type == pygame.TEXTINPUT and self.scene == "NAMING":
                for ch in event.text:
                    if len(self.input_name) < 10:
                        self.input_name += ch

            elif event.type == pygame.KEYDOWN:
                if self.scene == "GAME_OVER":
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.restart_game()
                        return

                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if self.scene == "NAMING":
                    if event.key == pygame.K_BACKSPACE:
                        self.input_name = self.input_name[:-1]
                    elif event.key == pygame.K_RETURN and self.input_name.strip():
                        self.cat = Cat(self.input_name.strip(), "아기고양이")
                        self.scene = "MAIN"

            elif event.type == pygame.MOUSEBUTTONDOWN and self.scene == "MAIN":
                self.handle_click_main(event.pos)

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

    def draw_naming(self):
        self.screen.blit(self.back_image, self.back_rect)

        title = self.big_font.render("고양이 이름을 지어주세요", True, (0, 0, 0))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 250))

        box_rect = pygame.Rect(70, 300, 260, 44)
        pygame.draw.rect(self.screen, (255, 255, 255), box_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), box_rect, 2)

        name_surface = self.big_font.render(self.input_name, True, (0, 0, 0))
        self.screen.blit(name_surface, (box_rect.x + 12, box_rect.y + 8))

        self.cursor_timer += 1
        if self.cursor_timer % 30 == 0:
            self.cursor_visible = not self.cursor_visible

        if self.cursor_visible:
            cursor_x = box_rect.x + 12 + name_surface.get_width() + 2
            cursor_y = box_rect.y + 8
            pygame.draw.line(self.screen, (0, 0, 0), (cursor_x, cursor_y), (cursor_x, cursor_y + 26), 2)

        hint = self.hint_font.render("Enter 키를 눌러 확정", True, (120, 120, 120))
        self.screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, box_rect.y + 52))

    def draw_game_over(self):
        self.screen.blit(self.back_image, self.back_rect)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = 320, 260
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = 180
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (245, 245, 245, 230), panel_surf.get_rect(), border_radius=12)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (255, 80, 80), panel_rect, 2, border_radius=12)

        title = self.big_font.render("GAME OVER", True, (255, 80, 80))
        shadow = self.big_font.render("GAME OVER", True, (30, 30, 30))
        title_cx = panel_rect.centerx
        title_y = panel_y + 18
        self.screen.blit(shadow, shadow.get_rect(center=(title_cx + 1, title_y + 1)))
        self.screen.blit(title, title.get_rect(center=(title_cx, title_y)))

        msg = "고양이가 죽었습니다…" if self.game_over_reason == "DEAD" else "고양이가 가출했습니다…"
        text = self.font.render(msg, True, (60, 60, 60))
        self.screen.blit(text, text.get_rect(center=(panel_rect.centerx, title_y + 40)))

        hint1 = self.font.render("ESC 키를 눌러 종료", True, (100, 100, 100))
        hint2 = self.font.render("R 키를 눌러 재시작", True, (100, 100, 100))
        self.screen.blit(hint1, hint1.get_rect(center=(panel_rect.centerx, title_y + 72)))
        self.screen.blit(hint2, hint2.get_rect(center=(panel_rect.centerx, title_y + 94)))

        sep_y = title_y + 108
        pygame.draw.line(self.screen, (220, 220, 220), (panel_x + 16, sep_y), (panel_x + panel_w - 16, sep_y), 1)

        log = self.ending_log
        y = sep_y + 14
        for line in [
            f"생존 일수 : {log.get('day', 0)}일",
            f"배고픔 : {log.get('hunger', 0)}",
            f"피로 : {log.get('tiredness', 0)}",
            f"행복 : {log.get('happiness', 0)}",
            f"청결 : {log.get('cleanliness', 0)}",
        ]:
            t = self.font.render(line, True, (50, 50, 50))
            self.screen.blit(t, (panel_x + 24, y))
            y += 22

    def draw_button(self, rect, text, font):
        pygame.draw.rect(self.screen, (220, 220, 220), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        txt = font.render(text, True, (0, 0, 0))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        if self.scene == "GAME_OVER":
            self.draw_game_over()
            pygame.display.flip()
            return

        if self.scene == "NAMING":
            self.draw_naming()
            pygame.display.flip()
            return

        self.screen.blit(self.back_image, self.back_rect)

        info = f"{self.state.day}일차 - {'아침' if self.state.time_phase == state.MORNING else '밤'}"
        self.screen.blit(self.font.render(info, True, (0, 0, 0)), (INFO_X, INFO_Y))

        money = getattr(self.state, "money", 0)
        if self.coin_image:
            self.screen.blit(self.coin_image, (INFO_X, INFO_Y + 22))
            coin_text = self.coin_font.render(f"{money}", True, (0, 0, 0))
            self.screen.blit(coin_text, (INFO_X + 42, INFO_Y + 28))
        else:
            coin_text = self.coin_font.render(f"🪙 {money}", True, (0, 0, 0))
            self.screen.blit(coin_text, (INFO_X, INFO_Y + 22))

        self.draw_bar(STAT_X, STAT_Y_START, "배고픔", self.cat.hunger, (255, 100, 100))
        self.draw_bar(STAT_X, STAT_Y_START + STAT_GAP, "피로", self.cat.tiredness, (100, 100, 255))
        self.draw_bar(STAT_X, STAT_Y_START + 2 * STAT_GAP, "행복", self.cat.happiness, (100, 255, 100))
        self.draw_bar(STAT_X, STAT_Y_START + 3 * STAT_GAP, "청결", self.cat.cleanliness, (180, 180, 180))

        cat_img = pygame.image.load(self.cat.image_path).convert_alpha()
        cat_rect = cat_img.get_rect(center=(WIDTH // 2, MAIN_CAT_Y))
        self.screen.blit(cat_img, cat_rect)

        name_text = self.name_font.render(f"{self.cat.name} - {self.cat.stage}", True, (0, 0, 0))
        name_rect = name_text.get_rect(center=(WIDTH // 2, cat_rect.top - NAME_Y_OFFSET))
        self.screen.blit(name_text, name_rect)

        pygame.draw.rect(self.screen, (220, 220, 220), ARROW_RECT)
        pygame.draw.rect(self.screen, (0, 0, 0), ARROW_RECT, 1)
        arrow = self.font.render("◀", True, (0, 0, 0))
        self.screen.blit(arrow, arrow.get_rect(center=ARROW_RECT.center))

        if self.panel_open:
            panel_x = WIDTH - PANEL_W - 8

            close_rect = pygame.Rect(panel_x, PANEL_Y - (PANEL_BTN_H + PANEL_GAP), PANEL_W, PANEL_BTN_H)
            self.draw_button(close_rect, "▶ 닫기", self.panel_font)

            labels = ["밥", "놀기", "씻기", "잠자기", "설정"]
            for i, label in enumerate(labels):
                r = pygame.Rect(panel_x, PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP), PANEL_W, PANEL_BTN_H)
                self.draw_button(r, label, self.panel_font)

        start_x = (WIDTH - (BOTTOM_BTN_W * 3 + BOTTOM_GAP * 2)) // 2
        labels = ["상점", "미니게임", "가방"]
        for i, label in enumerate(labels):
            x = start_x + i * (BOTTOM_BTN_W + BOTTOM_GAP)
            r = pygame.Rect(x, BOTTOM_BTN_Y, BOTTOM_BTN_W, BOTTOM_BTN_H)
            self.draw_button(r, label, self.tab_font)

        pygame.display.flip()


if __name__ == "__main__":
    Game().run()
