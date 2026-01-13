import pygame
import sys
import os
from cat import Cat
import state
from game import MiniGameScreen
from shop import ShopUI
from bag import BagUI
import save
import evolution
from config import asset_path, base_path
from pg_utils import load_font, load_image, load_sound, play_music
from achievements import AchievementsManager, draw_toasts
from achievements_ui import AchievementsUI
from pathlib import Path
from start_flow import StartFlow


WIDTH = 400
HEIGHT = 600
FPS = 60

BACK_IMAGE = asset_path("ui", "background.png")
FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")

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
LEFT_ARROW_RECT = pygame.Rect(10, 300, 24, 44)

MAIN_CAT_Y = 450
NAME_Y_OFFSET = 1


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption("고양이 키우기")
        pygame.key.start_text_input()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))

        icon_surface = load_image(asset_path("icon", "icon.png"), alpha=True)
        if icon_surface is not None:
            pygame.display.set_icon(icon_surface)
        self.clock = pygame.time.Clock()
        self.running = True

        self.app_mode = "START_FLOW"
        self.difficulty = "normal"
        self.flow = StartFlow(self.screen, assets_root=os.path.join(base_path(), "assets"))

        self.back_image = self.load_image(BACK_IMAGE)
        self.back_image = pygame.transform.scale(self.back_image, (WIDTH, HEIGHT))
        self.back_rect = self.back_image.get_rect(topleft=(0, 0))

        self.coin_image = load_image(asset_path("ui", "coin.png"), size=(36, 36), smooth=True, alpha=True)

        self.click_sound = load_sound(asset_path("sounds", "button.mp3"), volume=0.25)

        play_music(asset_path("sounds", "bgm.mp3"), volume=1, loops=-1)

        pygame.font.init()
        self.font = load_font(FONT_PATH, 18)
        self.name_font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)
        self.panel_font = load_font(FONT_PATH, 17)
        self.tab_font = load_font(FONT_PATH, 18)
        self.stat_font = load_font(FONT_PATH, 16)
        self.hint_font = load_font(FONT_PATH, 16)
        self.coin_font = load_font(FONT_PATH, 20)

        self.state = state.GameState()

        try:
            base = Path(os.getenv("APPDATA") or str(Path.home())) / "growing-cat"
            base.mkdir(parents=True, exist_ok=True)
            self.ach = AchievementsManager(str(base / "achievements_save.json"))
        except Exception:
            self.ach = AchievementsManager()

        self.cat = None
        self.panel_open = False
        self.left_panel_open = False
        self.game_over_reason = None
        self.ending_log = {}
        self.inventory = {}
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        if not hasattr(self.state, "minigame_used"):
            self.state.minigame_used = {"jump": False, "memory": False, "footsteps": False}
        self.evolve_timer = 0

        self.evolve_menu_timer = 0

        self.load_saved_game()
        if self.cat:
            self.app_mode = "GAME"
        else:
            self.app_mode = "START_FLOW"

    def load_saved_game(self):
        data = save.load_game()
        if not isinstance(data, dict) or "cat" not in data:
            return

        self.state.day = max(1, int(data.get("day", 1)))
        self.state.time_phase = data.get("time_phase", state.MORNING)

        cat_data = data.get("cat")
        if not isinstance(cat_data, dict):
            return

        name = cat_data.get("name")
        stage = cat_data.get("stage")
        if not isinstance(name, str) or not isinstance(stage, str):
            return

        self.cat = Cat(name, stage)
        try:
            self.cat.hunger = state.clamp(float(cat_data.get("hunger", 50)))
            self.cat.tiredness = state.clamp(float(cat_data.get("tiredness", 20)))
            self.cat.happiness = state.clamp(float(cat_data.get("happiness", 70)))
            self.cat.cleanliness = state.clamp(float(cat_data.get("cleanliness", 60)))
        except (TypeError, ValueError):
            pass

        self.state.money = max(0, int(data.get("money", 0)))
        raw_inv = data.get("inventory", {})
        if isinstance(raw_inv, dict):
            self.inventory = {k: max(0, int(v)) for k, v in raw_inv.items() if isinstance(k, str)}
        else:
            self.inventory = {}
        self.state.minigame_used = data.get("minigame_used", {"jump": False, "memory": False, "footsteps": False})
        self.scene = "MAIN"

    def load_image(self, filename):
        try:
            return pygame.image.load(filename).convert_alpha()
        except:
            pygame.quit()
            sys.exit()

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            self.handle_events(events)

            if self.app_mode == "START_FLOW":
                self.flow.update(dt)
                self.flow.draw()
                if self.flow.done and self.flow.result:
                    self.start_new_game(self.flow.result.get("name", ""), self.flow.result.get("difficulty", "normal"))
                pygame.display.flip()
                continue

            self.draw()

        pygame.quit()
        sys.exit()

    def start_new_game(self, name: str, difficulty: str = "normal"):
        name = str(name or "").strip()
        if not name:
            return

        self.difficulty = str(difficulty or "normal")

        self.state = state.GameState()
        if not hasattr(self.state, "minigame_used"):
            self.state.minigame_used = {"jump": False, "memory": False, "footsteps": False}

        self.cat = Cat(name, "아기고양이")
        self.inventory = {}
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self.panel_open = False
        self.left_panel_open = False
        self.game_over_reason = None
        self.ending_log = {}

        self.scene = "MAIN"
        self.app_mode = "GAME"
        save.save_game(self.make_save_data())

    def advance_time(self):
        phase = self.state.advance_time()
        if phase == state.NIGHT:
            self.cat.on_night()
        else:
            self.cat.on_morning()
            self.state.money = max(0, int(self.state.money + 5))

            if self.ach:
                self.ach.on_event("day_end")
                self.ach.on_event("coins_earned", amount=5)
                try:
                    stats = {
                        "happiness": int(self.cat.happiness),
                        "cleanliness": int(self.cat.cleanliness),
                        "hunger": int(self.cat.hunger),
                        "fatigue": int(self.cat.tiredness),
                    }
                    self.ach.check_stats_on_day_end(stats)
                except Exception:
                    pass

        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self.state.minigame_used = {"jump": False, "memory": False, "footsteps": False}

        evolved = False
        while True:
            has_meat = self.inventory.get("고기", 0) > 0
            has_bone = self.inventory.get("뼈", 0) > 0
            can_evo, msg = evolution.can_evolve(self.cat, self.state.day, self.state.money, has_meat, has_bone)
            if phase == state.MORNING and can_evo:
                cost = evolution.EVOLUTION_COST.get(self.cat.stage, 0)
                if self.state.money >= cost:
                    if self.cat.stage == evolution.ADULT:
                        if self.inventory.get("고기", 0) <= 0:
                            break
                        self.inventory["고기"] -= 1
                    elif self.cat.stage == evolution.LION:
                        if self.inventory.get("뼈", 0) <= 0:
                            break
                        self.inventory["뼈"] -= 1

                    self.state.money -= cost
                    evolution.evolve(self.cat)
                    evolved = True

                    if self.ach:
                        stage_map = {
                            evolution.ADULT: "adult",
                            evolution.LION: "lion",
                            evolution.DINO: "dino",
                        }
                        self.ach.on_event("evolved", stage=stage_map.get(self.cat.stage, ""))
                else:
                    break
            else:
                break

        if evolved:
            self.scene = "EVOLVE"
            self.evolve_timer = 0

        self.check_game_over()
        save.save_game(self.make_save_data())
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}

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
        self.panel_open = False
        self.left_panel_open = False
        self.game_over_reason = None
        self.ending_log = {}
        self.inventory = {}
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self.flow.reset_to_start()
        self.app_mode = "START_FLOW"

    def make_save_data(self):
        try:
            clean_inventory = {k: max(0, int(v)) for k, v in self.inventory.items() if isinstance(k, str) and isinstance(v, (int, float))}
        except (TypeError, ValueError):
            clean_inventory = {}
        
        try:
            clean_money = max(0, int(self.state.money))
        except (TypeError, ValueError):
            clean_money = 0
        
        return {
            "day": max(1, int(self.state.day)),
            "time_phase": self.state.time_phase,
            "money": clean_money,
            "inventory": clean_inventory,
            "minigame_used": getattr(self.state, "minigame_used", {"jump": False, "memory": False, "footsteps": False}),
            "cat": {
                "name": self.cat.name,
                "stage": self.cat.stage,
                "hunger": state.clamp(float(self.cat.hunger)),
                "tiredness": state.clamp(float(self.cat.tiredness)),
                "happiness": state.clamp(float(self.cat.happiness)),
                "cleanliness": state.clamp(float(self.cat.cleanliness))
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

    def open_shop(self):
        shop = ShopUI(self.screen, self.state.money, self.on_buy_item, self.play_click_sound)
        shop.run()
        save.save_game(self.make_save_data())

    def open_minigame(self):
        MiniGameScreen(self.screen, self.state, self.ach).run()
        save.save_game(self.make_save_data())

    def open_bag(self):
        BagUI(self.screen, self.inventory, self.use_item, self.play_click_sound).run()
        save.save_game(self.make_save_data())

    def open_achievements(self):
        self.panel_open = False
        self.left_panel_open = False
        AchievementsUI(self.screen, self.ach, self.play_click_sound).run()

    def open_evolve_menu(self):
        if not self.cat:
            return
        self.panel_open = False
        self.left_panel_open = False
        self.scene = "EVOLVE_MENU"
        self.evolve_menu_timer = 0

    def get_evolve_menu_info(self):
        stage = getattr(self.cat, "stage", None)
        next_stage = evolution.get_next_stage(stage)

        has_meat = self.inventory.get("고기", 0) > 0
        has_bone = self.inventory.get("뼈", 0) > 0
        can_evo, status_msg = evolution.can_evolve(self.cat, self.state.day, self.state.money, has_meat, has_bone)

        lines = []
        if not next_stage:
            lines.append("현재: 최종 단계")
            lines.append("더 이상 진화할 수 없습니다")
            return {
                "next_stage": None,
                "can_evolve": False,
                "status": status_msg,
                "lines": lines,
            }

        cost = evolution.EVOLUTION_COST.get(stage, 0)
        lines.append(f"현재: {stage} → 다음: {next_stage}")
        lines.append(f"비용: {cost} 코인")

        if stage == evolution.BABY:
            lines.append("조건: 14일 이상")
        elif stage == evolution.ADULT:
            lines.append("조건: 30일 이상")
            lines.append(f"아이템: 고기 1개 (보유: {self.inventory.get('고기', 0)})")
            lines.append("스탯: 행복 80↑, 피로 20↓, 청결 70↑, 배고픔 30↓")
        elif stage == evolution.LION:
            lines.append("조건: 50일 이상")
            lines.append(f"아이템: 뼈 1개 (보유: {self.inventory.get('뼈', 0)})")
            lines.append("스탯: 행복 90↑, 피로 10↓, 청결 80↑, 배고픔 20↓")
        else:
            lines.append("조건: -")

        lines.append(f"상태: {'진화 가능' if can_evo else status_msg}")

        return {
            "next_stage": next_stage,
            "can_evolve": can_evo,
            "status": status_msg,
            "lines": lines,
        }

    def try_evolve_now(self):
        info = self.get_evolve_menu_info()
        next_stage = info.get("next_stage")
        if not next_stage or not info.get("can_evolve"):
            return False

        stage = self.cat.stage
        cost = evolution.EVOLUTION_COST.get(stage, 0)
        if self.state.money < cost:
            return False

        if stage == evolution.ADULT:
            if self.inventory.get("고기", 0) <= 0:
                return False
            self.inventory["고기"] -= 1
        elif stage == evolution.LION:
            if self.inventory.get("뼈", 0) <= 0:
                return False
            self.inventory["뼈"] -= 1

        self.state.money -= cost
        self.cat.evolve_to(next_stage)

        if self.ach:
            stage_map = {
                evolution.ADULT: "adult",
                evolution.LION: "lion",
                evolution.DINO: "dino",
            }
            self.ach.on_event("evolved", stage=stage_map.get(self.cat.stage, ""))

        self.scene = "EVOLVE"
        self.evolve_timer = 0
        save.save_game(self.make_save_data())
        return True

    def use_item(self, item):
        if not self.cat or item not in self.inventory or self.inventory[item] <= 0:
            return
        
        if item == "사료":
            self.cat.hunger = max(0, self.cat.hunger - 30)
            self.inventory["사료"] -= 1
        elif item == "생선":
            self.cat.hunger = max(0, self.cat.hunger - 50)
            self.inventory["생선"] -= 1
        elif item == "츄르":
            self.cat.hunger = max(0, self.cat.hunger - 70)
            self.inventory["츄르"] -= 1
        elif item == "강아지풀":
            self.cat.happiness = min(state.MAX_STAT, self.cat.happiness + 20)
            self.inventory["강아지풀"] -= 1
        elif item == "실":
            self.cat.happiness = min(state.MAX_STAT, self.cat.happiness + 30)
            self.inventory["실"] -= 1
        elif item == "낚싯대":
            self.cat.happiness = min(state.MAX_STAT, self.cat.happiness + 50)
            self.inventory["낚싯대"] -= 1
        
        self.cat._clamp_all()
        save.save_game(self.make_save_data())

    def on_buy_item(self, item):
        if not isinstance(item, dict):
            return False

        item_id = item.get("id")
        if not isinstance(item_id, str):
            return False

        try:
            price = int(item.get("price", 0))
        except (TypeError, ValueError):
            return False
        if price < 0:
            return False

        try:
            self.state.money = max(0, int(self.state.money))
        except (TypeError, ValueError):
            self.state.money = 0

        if self.state.money < price:
            return False
        self.state.money -= price

        if self.ach:
            self.ach.on_event("item_bought")
        
        if item_id == "bab":
            self.inventory["사료"] = self.inventory.get("사료", 0) + 1
        elif item_id == "fish":
            self.inventory["생선"] = self.inventory.get("생선", 0) + 1
        elif item_id == "chur":
            self.inventory["츄르"] = self.inventory.get("츄르", 0) + 1
        elif item_id == "meat":
            self.inventory["고기"] = self.inventory.get("고기", 0) + 1
        elif item_id == "doggrass":
            self.inventory["강아지풀"] = self.inventory.get("강아지풀", 0) + 1
        elif item_id == "fishing":
            self.inventory["낚싯대"] = self.inventory.get("낚싯대", 0) + 1
        elif item_id == "string":
            self.inventory["실"] = self.inventory.get("실", 0) + 1
        elif item_id == "bone":
            self.inventory["뼈"] = self.inventory.get("뼈", 0) + 1
        
        save.save_game(self.make_save_data())
        return True

    def handle_click_main(self, pos):
        center_x = (WIDTH - BOTTOM_BTN_W) // 2
        advance_rect = pygame.Rect(center_x, BOTTOM_BTN_Y, BOTTOM_BTN_W, BOTTOM_BTN_H)
        if advance_rect.collidepoint(pos):
            self.play_click_sound()
            self.advance_time()
            return

        if (not self.panel_open) and ARROW_RECT.collidepoint(pos):
            self.play_click_sound()
            self.panel_open = True
            return

        if (not self.left_panel_open) and LEFT_ARROW_RECT.collidepoint(pos):
            self.play_click_sound()
            self.left_panel_open = True
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

            labels = ["밥", "놀기", "씻기", "잠자기", "진화"]
            actions = [self.cat.feed_free, self.cat.play_free, self.cat.clean, self.cat.sleep, self.open_evolve_menu]
            keys = ["feed", "play", "clean", "sleep"]

            for i in range(5):
                r = pygame.Rect(
                    panel_x,
                    PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP),
                    PANEL_W,
                    PANEL_BTN_H
                )
                if r.collidepoint(pos):
                    self.play_click_sound()
                    if i < 4:
                        if self.actions_used[keys[i]]:
                            return
                        if self.cat:
                            actions[i]()
                            self.actions_used[keys[i]] = True
                            save.save_game(self.make_save_data())
                            self.check_game_over()
                        return

                    actions[i]()
                    return

        if self.left_panel_open:
            panel_x = 8
            left_close_rect = pygame.Rect(
                panel_x,
                PANEL_Y - (PANEL_BTN_H + PANEL_GAP),
                PANEL_W,
                PANEL_BTN_H
            )
            if left_close_rect.collidepoint(pos):
                self.play_click_sound()
                self.left_panel_open = False
                return

            labels = ["설정", "미니게임", "상점", "가방", "업적"]
            actions = [self.open_settings, self.open_minigame, self.open_shop, self.open_bag, self.open_achievements]
            for i in range(5):
                r = pygame.Rect(
                    panel_x,
                    PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP),
                    PANEL_W,
                    PANEL_BTN_H
                )
                if r.collidepoint(pos):
                    self.play_click_sound()
                    actions[i]()
                    return

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                if self.app_mode == "GAME" and self.scene == "MAIN" and self.cat:
                    save.save_game(self.make_save_data())
                self.running = False

            if self.app_mode == "START_FLOW":
                if event.type != pygame.QUIT:
                    self.flow.handle_event(event)
                continue

            elif event.type == pygame.KEYDOWN:
                if self.scene == "GAME_OVER":
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_r:
                        self.restart_game()
                        return

                if event.key == pygame.K_ESCAPE:
                    self.running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and self.scene == "MAIN":
                self.handle_click_main(event.pos)

            elif event.type == pygame.MOUSEBUTTONDOWN and self.scene == "EVOLVE_MENU":
                self.handle_click_evolve_menu(event.pos)

            elif event.type == pygame.KEYDOWN and self.scene == "EVOLVE_MENU":
                if event.key == pygame.K_ESCAPE:
                    self.scene = "MAIN"

    def handle_click_evolve_menu(self, pos):
        panel_w, panel_h = 340, 260
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = 170
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        btn_w, btn_h = 130, 34
        evolve_rect = pygame.Rect(panel_x + 30, panel_y + panel_h - 56, btn_w, btn_h)
        close_rect = pygame.Rect(panel_x + panel_w - 30 - btn_w, panel_y + panel_h - 56, btn_w, btn_h)

        if close_rect.collidepoint(pos):
            self.play_click_sound()
            self.scene = "MAIN"
            return

        info = self.get_evolve_menu_info()
        if evolve_rect.collidepoint(pos):
            self.play_click_sound()
            if info.get("can_evolve"):
                self.try_evolve_now()
            return

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

    def draw_button_state(self, rect, text, font, enabled=True):
        fill = (220, 220, 220) if enabled else (180, 180, 180)
        text_color = (0, 0, 0) if enabled else (120, 120, 120)
        pygame.draw.rect(self.screen, fill, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        txt = font.render(text, True, text_color)
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        if self.scene == "EVOLVE":
            self.draw_evolve()
            if self.ach:
                draw_toasts(self.screen, self.font, self.ach)
            pygame.display.flip()
            return

        if self.scene == "EVOLVE_MENU":
            self.draw_evolve_menu()
            if self.ach:
                draw_toasts(self.screen, self.font, self.ach)
            pygame.display.flip()
            return

        if self.scene == "GAME_OVER":
            self.draw_game_over()
            if self.ach:
                draw_toasts(self.screen, self.font, self.ach)
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

        if not self.panel_open:
            pygame.draw.rect(self.screen, (220, 220, 220), ARROW_RECT)
            pygame.draw.rect(self.screen, (0, 0, 0), ARROW_RECT, 1)
            arrow = self.font.render("◀", True, (0, 0, 0))
            self.screen.blit(arrow, arrow.get_rect(center=ARROW_RECT.center))

        if self.panel_open:
            panel_x = WIDTH - PANEL_W - 8

            close_rect = pygame.Rect(panel_x, PANEL_Y - (PANEL_BTN_H + PANEL_GAP), PANEL_W, PANEL_BTN_H)
            self.draw_button(close_rect, "▶ 닫기", self.panel_font)

            labels = ["밥", "놀기", "씻기", "잠자기", "진화"]
            for i, label in enumerate(labels):
                r = pygame.Rect(panel_x, PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP), PANEL_W, PANEL_BTN_H)
                if i == 0:
                    self.draw_button_state(r, label, self.panel_font, not self.actions_used["feed"])
                elif i == 1:
                    self.draw_button_state(r, label, self.panel_font, not self.actions_used["play"])
                elif i == 2:
                    self.draw_button_state(r, label, self.panel_font, not self.actions_used["clean"])
                elif i == 3:
                    self.draw_button_state(r, label, self.panel_font, not self.actions_used["sleep"])
                else:
                    self.draw_button(r, label, self.panel_font)

        if not self.left_panel_open:
            pygame.draw.rect(self.screen, (220, 220, 220), LEFT_ARROW_RECT)
            pygame.draw.rect(self.screen, (0, 0, 0), LEFT_ARROW_RECT, 1)
            l_arrow = self.font.render("▶", True, (0, 0, 0))
            self.screen.blit(l_arrow, l_arrow.get_rect(center=LEFT_ARROW_RECT.center))

        if self.left_panel_open:
            panel_x = 8
            left_close_rect = pygame.Rect(panel_x, PANEL_Y - (PANEL_BTN_H + PANEL_GAP), PANEL_W, PANEL_BTN_H)
            self.draw_button(left_close_rect, "닫기 ◀", self.panel_font)
            labels = ["설정", "미니게임", "상점", "가방", "업적"]
            for i, label in enumerate(labels):
                r = pygame.Rect(panel_x, PANEL_Y + i * (PANEL_BTN_H + PANEL_GAP), PANEL_W, PANEL_BTN_H)
                self.draw_button(r, label, self.panel_font)

        center_x = (WIDTH - BOTTOM_BTN_W) // 2
        advance_rect = pygame.Rect(center_x, BOTTOM_BTN_Y, BOTTOM_BTN_W, BOTTOM_BTN_H)
        self.draw_button(advance_rect, "다음 시간", self.tab_font)

        if self.ach:
            draw_toasts(self.screen, self.font, self.ach)

        pygame.display.flip()

    def draw_evolve(self):
        self.evolve_timer += 1
        self.screen.fill((0, 0, 0))

        text1 = self.big_font.render("진화 성공!", True, (255, 255, 255))
        text2 = self.big_font.render(f"{self.cat.stage}", True, (255, 255, 0))

        self.screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, 220))
        self.screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, 260))

        if self.evolve_timer > 120:
            self.scene = "MAIN"

    def draw_evolve_menu(self):
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

        if self.cat and self.cat.image_path:
            cat_img = pygame.image.load(self.cat.image_path).convert_alpha()
            cat_rect = cat_img.get_rect(center=(WIDTH // 2, MAIN_CAT_Y))
            self.screen.blit(cat_img, cat_rect)

            name_text = self.name_font.render(f"{self.cat.name} - {self.cat.stage}", True, (0, 0, 0))
            name_rect = name_text.get_rect(center=(WIDTH // 2, cat_rect.top - NAME_Y_OFFSET))
            self.screen.blit(name_text, name_rect)

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        panel_w, panel_h = 340, 260
        panel_x = WIDTH // 2 - panel_w // 2
        panel_y = 170
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)

        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (245, 245, 245, 235), panel_surf.get_rect(), border_radius=12)
        self.screen.blit(panel_surf, (panel_x, panel_y))
        pygame.draw.rect(self.screen, (60, 60, 60), panel_rect, 2, border_radius=12)

        title = self.big_font.render("진화", True, (30, 30, 30))
        self.screen.blit(title, title.get_rect(center=(panel_rect.centerx, panel_y + 26)))
        pygame.draw.line(self.screen, (220, 220, 220), (panel_x + 16, panel_y + 50), (panel_x + panel_w - 16, panel_y + 50), 1)

        info = self.get_evolve_menu_info()
        y = panel_y + 66
        for line in info.get("lines", []):
            t = self.hint_font.render(line, True, (40, 40, 40))
            self.screen.blit(t, (panel_x + 20, y))
            y += 22

        btn_w, btn_h = 130, 34
        evolve_rect = pygame.Rect(panel_x + 30, panel_y + panel_h - 56, btn_w, btn_h)
        close_rect = pygame.Rect(panel_x + panel_w - 30 - btn_w, panel_y + panel_h - 56, btn_w, btn_h)
        self.draw_button_state(evolve_rect, "진화하기", self.panel_font, bool(info.get("can_evolve")))
        self.draw_button(close_rect, "닫기", self.panel_font)


if __name__ == "__main__":
    Game().run()
