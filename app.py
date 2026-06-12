import pygame
import sys
import os
import random
from cat import Cat
import state
from game import MiniGameScreen
from shop import ShopUI
from bag import BagUI
import save
import evolution
from config import asset_path, base_path
from items import inventory_item_from_shop_id, normalize_inventory, normalize_inventory_item
from pg_utils import load_font, load_image, load_sound, play_music
from achievements import AchievementsManager, draw_toasts
from achievements_ui import AchievementsUI
from pathlib import Path
from start_flow import StartFlow
from pause_menu import PauseMenu
from photo_mode import take_photo

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

PANEL_W = 110
PANEL_BTN_H = 26
PANEL_GAP = 4
PANEL_Y = 300

ARROW_RECT = pygame.Rect(WIDTH - 34, 300, 24, 44)
LEFT_ARROW_RECT = pygame.Rect(10, 300, 24, 44)

MAIN_CAT_Y = 450
NAME_Y_OFFSET = 12
CAT_AREA_WIDTH = 280
CAT_AREA_TOP = 230
CAT_AREA_BOTTOM = BOTTOM_BTN_Y - 20
CAT_STAGE_MAX_SIZE = {
    evolution.BABY: (150, 150),
    evolution.ADULT: (225, 200),
    evolution.LION: (230, 250),
    evolution.DINO: (230, 250),
}
CAT_IMAGE_LAYOUT_OVERRIDES = {
    "lion_cat1.png": {"offset": (-20, 0), "bottom": BOTTOM_BTN_Y - 5, "max_size": (200, 128)},
    "lion_cat4.png": {"offset": (-10, 0), "bottom": BOTTOM_BTN_Y - 5, "max_size": (210, 135)},
}

CARE_ACTION_LABELS = ("밥", "놀기", "씻기", "잠자기", "진화")
CARE_ACTION_KEYS = ("feed", "play", "clean", "sleep")
MENU_ACTION_LABELS = ("설정", "미니게임", "상점", "가방", "업적")
CAT_IMAGE_ROTATE_CHANCE = 0.20

CAT_CLICK_LINES = {
    "energetic": (
        "놀아줘서 좋다냥!",
        "한 번 더 쓰다듬어 달라냥.",
        "오늘은 기분이 반짝반짝하다냥!",
        "뛰어다니고 싶다냥!",
        "꼬리가 저절로 흔들린다냥.",
        "지금 완전 신난다냥!",
        "밖에 뭐가 움직였다냥?",
        "장난감 가져와달라냥!",
        "발바닥이 근질근질하다냥.",
        "나랑 놀 준비 됐냥?",
        "오늘은 빠르게 달릴거다냥!",
        "햇빛이 좋아서 들뜬다냥.",
        "귀가 쫑긋했다냥!",
        "방금 좋은 생각났다냥.",
        "주인 손 냄새 좋다냥.",
        "심장이 콩콩 뛴다냥.",
        "뭔가 재미있는 날이다냥.",
        "한 바퀴 돌고 싶다냥!",
        "기분이 높이 점프한다냥.",
        "내가 먼저 달려간다냥!",
        "놀자고 눈빛 보낸다냥.",
        "오늘 컨디션 최고다냥.",
        "발톱 숨기고 놀겠다냥.",
        "간지러워도 좋다냥.",
        "더 가까이 와달라냥.",
        "지금 웃는 중이다냥.",
        "소리 없이 뛰어본다냥.",
        "모험을 시작하자냥!",
        "주인 따라갈 준비 됐다냥.",
    ),
    "calm": (
        "조용히 곁에 있어줘서 좋다냥.",
        "따뜻한 손길이다냥.",
        "천천히 쉬고 싶다냥.",
        "오늘 공기가 부드럽다냥.",
        "마음이 편안해진다냥.",
        "조금 더 쓰다듬어줘냥.",
        "여기 있으면 안심된다냥.",
        "눈을 천천히 감는다냥.",
        "따뜻한 시간이 좋다냥.",
        "소리가 잔잔하게 들린다냥.",
        "곁에만 있어도 좋다냥.",
        "차분히 숨 쉬는 중이다냥.",
        "이불 같은 기분이다냥.",
        "손길이 조심스러워 좋다냥.",
        "오늘은 느긋한 날이다냥.",
        "창밖을 보고 싶다냥.",
        "작은 소리도 들린다냥.",
        "마음이 동그랗다냥.",
        "기분 좋은 정적이다냥.",
        "조용한 놀이도 좋다냥.",
        "살짝 기대고 싶다냥.",
        "오늘은 얌전히 있을게냥.",
        "부드러운 시간이 흐른다냥.",
        "느린 하루도 괜찮다냥.",
        "주인 옆이 제일 편하다냥.",
        "눈인사 보내는 중이다냥.",
        "차분하게 반갑다냥.",
        "햇살 아래 쉬고 싶다냥.",
        "고요해서 행복하다냥.",
        "오늘은 마음이 맑다냥.",
        "손끝이 포근하다냥.",
    ),
    "lazy": (
        "조금만 더 누워있고 싶다냥.",
        "포근해서 잠이 온다냥.",
        "간식 생각이 난다냥.",
        "움직이기엔 너무 편하다냥.",
        "배만 살짝 만져달라냥.",
        "오늘은 누워서 놀자냥.",
        "눈꺼풀이 무겁다냥.",
        "쿠션이 나를 붙잡는다냥.",
        "잠깐만 더 꿈꿀래냥.",
        "느릿느릿 반응한다냥.",
        "일어나긴 했는데 귀찮다냥.",
        "간식 소리면 일어난다냥.",
        "햇빛 자리가 좋다냥.",
        "몸이 말랑해진다냥.",
        "눕는 것도 재능이다냥.",
        "조금만 더 뒹굴겠다냥.",
        "지금은 충전 중이다냥.",
        "느긋함이 최고다냥.",
        "손길은 환영이다냥.",
        "잘 자는 중은 아니었다냥.",
        "하품이 먼저 나온다냥.",
        "편한 곳을 찾았다냥.",
        "오늘 목표는 쉬기다냥.",
        "꿈에서 뛰어놀았다냥.",
        "밥 먹고 또 잘거다냥.",
        "움직임은 내일 생각한다냥.",
        "등을 기대고 싶다냥.",
        "지금 자세 완벽하다냥.",
        "살짝만 놀아준다냥.",
        "느린 쓰다듬이 좋다냥.",
        "쉬는 것도 중요하다냥.",
    ),
    "default": (
        "냐옹.",
        "기분이 좋아 보인다냥.",
        "주인을 바라보고 있다냥.",
        "살짝 고개를 기울인다냥.",
        "꼬리가 천천히 움직인다냥.",
        "작게 골골거린다냥.",
        "눈을 깜빡였다냥.",
        "손끝을 따라본다냥.",
        "가만히 냄새를 맡는다냥.",
        "오늘도 함께 있다냥.",
        "작은 소리로 대답했다냥.",
        "기분을 살피는 중이다냥.",
        "살금살금 다가온다냥.",
        "발끝으로 톡 건드린다냥.",
        "주변을 둘러본다냥.",
        "조금 궁금해졌다냥.",
        "귀가 살짝 움직였다냥.",
        "마음에 든 표정이다냥.",
        "편안하게 앉아있다냥.",
        "천천히 꼬리를 흔든다냥.",
        "주인 손을 바라본다냥.",
        "가까이 있어도 좋다냥.",
    ),
}

CAT_NEED_LINES = (
    ("hunger", 80, (
        "배고파... 밥 생각이 난다냥.",
        "배에서 소리가 난다냥.",
        "밥그릇을 보고 있다냥.",
        "간식 냄새가 그립다냥.",
        "조금 허전하다냥.",
    )),
    ("tiredness", 80, (
        "졸려... 조금 쉬고 싶다냥.",
        "눈이 자꾸 감긴다냥.",
        "잠자리가 필요하다냥.",
        "몸이 무겁다냥.",
        "오늘은 빨리 자고 싶다냥.",
    )),
    ("happiness", 25, (
        "오늘은 조금 심심하다냥.",
        "기분이 축 처진다냥.",
        "놀아주면 좋겠다냥.",
        "혼자 있긴 싫다냥.",
        "관심이 필요하다냥.",
    )),
    ("cleanliness", 25, (
        "몸이 찝찝하다냥.",
        "털이 엉킨 것 같다냥.",
        "깨끗해지고 싶다냥.",
        "발바닥이 신경 쓰인다냥.",
        "씻으면 기분 좋을까냥.",
    )),
)


def safe_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_stat(value, default=0):
    try:
        return state.clamp(float(value))
    except (TypeError, ValueError):
        return state.clamp(float(default))


class Game:
    def __init__(self):
        self._init_pygame()
        self._init_runtime_flags()
        self._init_start_flow()
        self._load_assets()
        self._init_fonts()
        self.pause_menu = PauseMenu(self.screen)
        self.state = state.GameState()
        self.ach = self._init_achievements()
        self._init_game_defaults()
        self.load_saved_game()
        self.app_mode = "GAME" if self.cat else "START_FLOW"

    def _init_pygame(self):
        pygame.init()
        try:
            pygame.mixer.init()
        except pygame.error:
            pass
        pygame.display.set_caption("고양이 키우기")
        pygame.key.start_text_input()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        icon_surface = load_image(asset_path("icon", "icon.png"), alpha=True)
        if icon_surface is not None:
            pygame.display.set_icon(icon_surface)
        self.clock = pygame.time.Clock()

    def _init_runtime_flags(self):
        self.running = True

        self.paused = False
        self.pause_menu = None
        self.request_quit = False
        self.request_to_start = False

        self.toast_text = ""
        self.toast_timer = 0.0
        self.cat_dialogue_text = ""
        self.cat_dialogue_timer = 0.0

        self.difficulty = "normal"

    def _init_start_flow(self):
        self.app_mode = "START_FLOW"
        self.flow = StartFlow(self.screen, assets_root=os.path.join(base_path(), "assets"))

    def _load_assets(self):
        self.back_image = self.load_image(BACK_IMAGE)
        self.back_image = pygame.transform.scale(self.back_image, (WIDTH, HEIGHT))
        self.back_rect = self.back_image.get_rect(topleft=(0, 0))

        self.coin_image = load_image(asset_path("ui", "coin.png"), size=(36, 36), smooth=True, alpha=True)
        self.click_sound = load_sound(asset_path("sounds", "button.mp3"), volume=0.25)

        play_music(asset_path("sounds", "bgm.mp3"), volume=1, loops=-1)

    def _init_fonts(self):
        pygame.font.init()
        self.font = load_font(FONT_PATH, 18)
        self.name_font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)
        self.panel_font = load_font(FONT_PATH, 17)
        self.tab_font = load_font(FONT_PATH, 18)
        self.stat_font = load_font(FONT_PATH, 16)
        self.hint_font = load_font(FONT_PATH, 16)
        self.coin_font = load_font(FONT_PATH, 20)

    def _init_achievements(self):
        try:
            base = Path(os.getenv("APPDATA") or str(Path.home())) / "growing-cat"
            base.mkdir(parents=True, exist_ok=True)
            return AchievementsManager(str(base / "achievements_save.json"))
        except OSError:
            return AchievementsManager()

    def _init_game_defaults(self):
        self.cat = None
        self.panel_open = False
        self.left_panel_open = False
        self.game_over_reason = None
        self.ending_log = {}
        self.inventory = {}
        self.scene = "MAIN"
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self._cat_image_path = None
        self._cat_image = None
        self._cat_image_stage = None
        self._cat_display_image = None
        self._cat_display_body_rect = None
        self._cat_rect = None
        self._cat_click_count = 0
        if not hasattr(self.state, "minigame_used"):
            self.state.minigame_used = state.new_minigame_usage()
        self.evolve_timer = 0

        self.evolve_menu_timer = 0

    def load_saved_game(self):
        data = save.load_game()
        if not isinstance(data, dict) or "cat" not in data:
            return

        self.state.day = max(1, safe_int(data.get("day", 1), 1))
        saved_phase = data.get("time_phase", state.MORNING)
        self.state.time_phase = saved_phase if saved_phase in (state.MORNING, state.NIGHT) else state.MORNING
        self.difficulty = state.normalize_difficulty(data.get("difficulty", "normal"))
        self.personality = state.normalize_personality(data.get("personality", "energetic"))
        self.state.difficulty = self.difficulty
        self.state.personality = self.personality

        cat_data = data.get("cat")
        if not isinstance(cat_data, dict):
            return

        name = cat_data.get("name")
        stage = cat_data.get("stage")
        if not isinstance(name, str) or not isinstance(stage, str):
            return

        self.cat = Cat(name, stage, difficulty=self.difficulty, personality=self.personality)
        try:
            self.cat.hunger = state.clamp(float(cat_data.get("hunger", 50)))
            self.cat.tiredness = state.clamp(float(cat_data.get("tiredness", 20)))
            self.cat.happiness = state.clamp(float(cat_data.get("happiness", 70)))
            self.cat.cleanliness = state.clamp(float(cat_data.get("cleanliness", 60)))
        except (TypeError, ValueError):
            pass

        self.state.money = max(0, safe_int(data.get("money", 0), 0))
        self.inventory = normalize_inventory(data.get("inventory", {}))
        self.state.minigame_used = state.normalize_minigame_usage(data.get("minigame_used"))
        self.scene = "MAIN"

    def load_image(self, filename):
        image = load_image(filename, alpha=True)
        if image is None:
            pygame.quit()
            sys.exit()
        return image

    def _save_if_game_active(self):
        if self.app_mode == "GAME" and self.scene == "MAIN" and self.cat:
            save.save_game(self.make_save_data())

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            self.handle_events(events)

            if self.request_quit:
                self._save_if_game_active()
                self.running = False
                continue

            if self.request_to_start:
                self._save_if_game_active()
                self.request_to_start = False
                self.paused = False
                self.restart_game()
                continue

            if self.app_mode == "START_FLOW":
                self.flow.update(dt)
                self.flow.draw()
                if self.flow.done and self.flow.result:
                    self.start_new_game(
                        self.flow.result.get("name", ""),
                        self.flow.result.get("difficulty", "normal"),
                        self.flow.result.get("personality", "energetic")
                    )
                pygame.display.flip()
                continue

            self.update(dt)
            self.draw()

        pygame.quit()
        sys.exit()

    def start_new_game(self, name: str, difficulty: str = "normal", personality: str = "energetic"):
        name = str(name or "").strip()
        if not name:
            return

        self.difficulty = state.normalize_difficulty(difficulty)
        self.personality = state.normalize_personality(personality)

        self.state = state.GameState(self.difficulty, self.personality)
        if not hasattr(self.state, "minigame_used"):
            self.state.minigame_used = state.new_minigame_usage()

        self.cat = Cat(name, "아기고양이", difficulty=self.difficulty, personality=self.personality)
        self.inventory = {}
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self._cat_image_path = None
        self._cat_image = None
        self._cat_image_stage = None
        self._cat_display_image = None
        self._cat_display_body_rect = None
        self._cat_rect = None
        self._cat_click_count = 0
        self.cat_dialogue_text = ""
        self.cat_dialogue_timer = 0.0
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
            self._grant_day_reward()

        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self.state.minigame_used = state.new_minigame_usage()

        evolved = phase == state.MORNING and self._try_auto_evolve()
        if evolved:
            self.scene = "EVOLVE"
            self.evolve_timer = 0

        self.check_game_over()
        save.save_game(self.make_save_data())

    def _grant_day_reward(self):
        day_reward = state.get_day_coin_reward(self.difficulty)
        self.state.money = max(0, int(self.state.money + day_reward))

        if not self.ach:
            return

        self.ach.on_event("day_end")
        self.ach.on_event("coins_earned", amount=day_reward)
        try:
            stats = {
                "happiness": int(self.cat.happiness),
                "cleanliness": int(self.cat.cleanliness),
                "hunger": int(self.cat.hunger),
                "fatigue": int(self.cat.tiredness),
            }
        except (TypeError, ValueError):
            return
        self.ach.check_stats_on_day_end(stats)

    def _current_evolution_cost(self, stage=None):
        base_cost = evolution.EVOLUTION_COST.get(stage or self.cat.stage, 0)
        return state.get_evolution_cost(base_cost, self.difficulty)

    def _can_evolve_now(self, cost):
        has_meat = self.inventory.get("고기", 0) > 0
        has_bone = self.inventory.get("뼈", 0) > 0
        can_evo, _ = evolution.can_evolve(
            self.cat,
            self.state.day,
            self.state.money,
            has_meat,
            has_bone,
            cost_override=cost,
        )
        return can_evo

    def _consume_required_evolution_item(self, stage):
        required_item = None
        if stage == evolution.ADULT:
            required_item = "고기"
        elif stage == evolution.LION:
            required_item = "뼈"

        if required_item is None:
            return True
        if self.inventory.get(required_item, 0) <= 0:
            return False
        self.inventory[required_item] -= 1
        return True

    def _notify_evolved(self):
        if not self.ach:
            return

        stage_map = {
            evolution.ADULT: "adult",
            evolution.LION: "lion",
            evolution.DINO: "dino",
        }
        self.ach.on_event("evolved", stage=stage_map.get(self.cat.stage, ""))

    def _try_auto_evolve(self):
        evolved = False
        while True:
            stage = self.cat.stage
            cost = self._current_evolution_cost(stage)
            if not self._can_evolve_now(cost) or self.state.money < cost:
                break
            if not self._consume_required_evolution_item(stage):
                break

            self.state.money -= cost
            evolution.evolve(self.cat)
            self._notify_evolved()
            evolved = True

        return evolved

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
        self.difficulty = "normal"
        self.cat = None
        self.panel_open = False
        self.left_panel_open = False
        self.game_over_reason = None
        self.ending_log = {}
        self.inventory = {}
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self._cat_image_path = None
        self._cat_image = None
        self._cat_image_stage = None
        self._cat_display_image = None
        self._cat_display_body_rect = None
        self._cat_rect = None
        self._cat_click_count = 0
        self.cat_dialogue_text = ""
        self.cat_dialogue_timer = 0.0
        self.flow.reset_to_start()
        self.app_mode = "START_FLOW"

    def make_save_data(self):
        try:
            clean_inventory = normalize_inventory(self.inventory)
        except (TypeError, ValueError):
            clean_inventory = {}

        clean_money = max(0, safe_int(getattr(self.state, "money", 0), 0))
        clean_day = max(1, safe_int(getattr(self.state, "day", 1), 1))
        clean_phase = getattr(self.state, "time_phase", state.MORNING)
        if clean_phase not in (state.MORNING, state.NIGHT):
            clean_phase = state.MORNING
        cat_stats = {
            "hunger": safe_stat(getattr(self.cat, "hunger", 50), 50),
            "tiredness": safe_stat(getattr(self.cat, "tiredness", 20), 20),
            "happiness": safe_stat(getattr(self.cat, "happiness", 70), 70),
            "cleanliness": safe_stat(getattr(self.cat, "cleanliness", 60), 60),
        }

        return {
            "day": clean_day,
            "time_phase": clean_phase,
            "difficulty": state.normalize_difficulty(getattr(self.state, "difficulty", self.difficulty)),
            "personality": state.normalize_personality(
                getattr(self.state, "personality", getattr(self, "personality", "energetic"))
            ),
            "money": clean_money,
            "inventory": clean_inventory,
            "minigame_used": state.normalize_minigame_usage(getattr(self.state, "minigame_used", None)),
            "cat": {
                "name": self.cat.name,
                "stage": self.cat.stage,
                **cat_stats,
            }
        }

    def play_click_sound(self):
        if self.click_sound:
            try:
                self.click_sound.play()
            except pygame.error:
                pass

    def open_settings(self):
        from settings import SettingsScreen
        SettingsScreen(
            self.screen,
            self.restart_game,
            play_click_sound=self.play_click_sound,
        ).run()

    def open_shop(self):
        shop = ShopUI(
            self.screen,
            self.state.money,
            self.on_buy_item,
            self.play_click_sound,
            difficulty=self.difficulty,
        )
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

        cost = self._current_evolution_cost(stage)
        can_evo, status_msg = evolution.can_evolve(
            self.cat,
            self.state.day,
            self.state.money,
            self.inventory.get("고기", 0) > 0,
            self.inventory.get("뼈", 0) > 0,
            cost_override=cost,
        )

        if not next_stage:
            return {
                "next_stage": None,
                "can_evolve": False,
                "status": status_msg,
                "lines": ["현재: 최종 단계", "더 이상 진화할 수 없습니다"],
            }

        lines = [f"현재: {stage} → 다음: {next_stage}", f"비용: {cost} 코인"]
        lines.extend(self._evolution_requirement_lines(stage))
        lines.append(f"상태: {'진화 가능' if can_evo else status_msg}")
        return {
            "next_stage": next_stage,
            "can_evolve": can_evo,
            "status": status_msg,
            "lines": lines,
        }

    def _evolution_requirement_lines(self, stage):
        if stage == evolution.BABY:
            return ["조건: 7일 이상"]
        if stage == evolution.ADULT:
            return [
                "조건: 21일 이상",
                f"아이템: 고기 1개 (보유: {self.inventory.get('고기', 0)})",
                "스탯: 행복 75↑, 피로 25↓, 청결 75↑, 배고픔 25↓",
            ]
        if stage == evolution.LION:
            return [
                "조건: 35일 이상",
                f"아이템: 뼈 1개 (보유: {self.inventory.get('뼈', 0)})",
                "스탯: 행복 80↑, 피로 15↓, 청결 80↑, 배고픔 15↓",
            ]
        return ["조건: -"]


    def try_evolve_now(self):
        info = self.get_evolve_menu_info()
        next_stage = info.get("next_stage")
        if not next_stage or not info.get("can_evolve"):
            return False

        stage = self.cat.stage
        cost = self._current_evolution_cost(stage)
        if self.state.money < cost:
            return False

        if not self._consume_required_evolution_item(stage):
            return False

        self.state.money -= cost
        self.cat.evolve_to(next_stage)
        self._notify_evolved()

        self.scene = "EVOLVE"
        self.evolve_timer = 0
        save.save_game(self.make_save_data())
        return True

    def use_item(self, item):
        item = normalize_inventory_item(item)
        if not self.cat or item not in self.inventory or self.inventory[item] <= 0:
            return

        used = True
        if item == "사료":
            self.cat.hunger = max(0, self.cat.hunger - 30)
        elif item == "생선":
            self.cat.hunger = max(0, self.cat.hunger - 50)
        elif item == "츄르":
            self.cat.hunger = max(0, self.cat.hunger - 70)
        elif item == "강아지풀":
            self.cat.happiness = min(state.MAX_STAT, self.cat.happiness + 20)
        elif item == "실":
            self.cat.happiness = min(state.MAX_STAT, self.cat.happiness + 30)
        elif item == "낚싯대":
            self.cat.happiness = min(state.MAX_STAT, self.cat.happiness + 50)
        else:
            used = False

        if not used:
            return

        self.inventory[item] -= 1
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

        inventory_item = inventory_item_from_shop_id(item_id)
        if inventory_item is None:
            return False

        try:
            self.state.money = max(0, int(self.state.money))
        except (TypeError, ValueError):
            self.state.money = 0

        if self.state.money < price:
            return False
        self.state.money -= price

        self.inventory[inventory_item] = self.inventory.get(inventory_item, 0) + 1

        if self.ach:
            self.ach.on_event("item_bought")
        
        save.save_game(self.make_save_data())
        return True

    def _advance_rect(self):
        center_x = (WIDTH - BOTTOM_BTN_W) // 2
        return pygame.Rect(center_x, BOTTOM_BTN_Y, BOTTOM_BTN_W, BOTTOM_BTN_H)

    def _panel_close_rect(self, panel_x):
        return pygame.Rect(
            panel_x,
            PANEL_Y - (PANEL_BTN_H + PANEL_GAP),
            PANEL_W,
            PANEL_BTN_H,
        )

    def _panel_button_rect(self, panel_x, index):
        return pygame.Rect(
            panel_x,
            PANEL_Y + index * (PANEL_BTN_H + PANEL_GAP),
            PANEL_W,
            PANEL_BTN_H,
        )

    def handle_click_main(self, pos):
        if self._advance_rect().collidepoint(pos):
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

        if self.panel_open and self._handle_care_panel_click(pos):
            return

        if self.left_panel_open and self._handle_menu_panel_click(pos):
            return

        if self._handle_cat_click(pos):
            return

    def _handle_cat_click(self, pos):
        if not self.cat:
            return False

        cat_rect = getattr(self, "_cat_rect", None)
        if cat_rect is None or not cat_rect.collidepoint(pos):
            return False

        self.play_click_sound()
        self._cat_click_count = max(0, safe_int(getattr(self, "_cat_click_count", 0), 0)) + 1
        self.cat_dialogue_text = self._cat_dialogue_line()
        self.cat_dialogue_timer = 2.2

        if random.random() < CAT_IMAGE_ROTATE_CHANCE and self.cat.rotate_image():
            self._cat_image_path = None
            self._cat_image = None
            self._cat_image_stage = None
            self._cat_display_image = None
            self._cat_display_body_rect = None
            save.save_game(self.make_save_data())
        return True

    def _cat_dialogue_line(self):
        for stat_name, threshold, lines in CAT_NEED_LINES:
            value = getattr(self.cat, stat_name, 0)
            try:
                value = float(value)
            except (TypeError, ValueError):
                value = 0

            if stat_name in ("happiness", "cleanliness"):
                if value <= threshold:
                    return random.choice(lines)
            elif value >= threshold:
                return random.choice(lines)

        personality = state.normalize_personality(getattr(self.cat, "personality", None))
        lines = CAT_CLICK_LINES.get(personality, CAT_CLICK_LINES["default"])
        return random.choice(lines)

    def _handle_care_panel_click(self, pos):
        panel_x = WIDTH - PANEL_W - 8
        if self._panel_close_rect(panel_x).collidepoint(pos):
            self.play_click_sound()
            self.panel_open = False
            return True

        actions = ("feed_free", "play_free", "clean", "sleep")
        for index, key in enumerate(CARE_ACTION_KEYS):
            if self._panel_button_rect(panel_x, index).collidepoint(pos):
                self.play_click_sound()
                if self.actions_used[key]:
                    return True
                if self.cat:
                    getattr(self.cat, actions[index])()
                    self.actions_used[key] = True
                    save.save_game(self.make_save_data())
                    self.check_game_over()
                return True

        evolve_index = len(CARE_ACTION_KEYS)
        if self._panel_button_rect(panel_x, evolve_index).collidepoint(pos):
            self.play_click_sound()
            self.open_evolve_menu()
            return True

        return False

    def _handle_menu_panel_click(self, pos):
        panel_x = 8
        if self._panel_close_rect(panel_x).collidepoint(pos):
            self.play_click_sound()
            self.left_panel_open = False
            return True

        actions = (self.open_settings, self.open_minigame, self.open_shop, self.open_bag, self.open_achievements)
        for index, action in enumerate(actions):
            if self._panel_button_rect(panel_x, index).collidepoint(pos):
                self.play_click_sound()
                action()
                return True

        return False

    def handle_events(self, events):
        for event in events:
            if self._handle_quit_event(event):
                continue

            if self.app_mode == "START_FLOW":
                self.flow.handle_event(event)
                continue

            if self._handle_pause_event(event):
                continue
            if self._handle_scene_key_event(event):
                continue
            self._handle_scene_mouse_event(event)

    def _handle_quit_event(self, event):
        if event.type != pygame.QUIT:
            return False

        self._save_if_game_active()
        self.running = False
        return True

    def _handle_pause_event(self, event):
        if self.app_mode != "GAME" or self.scene == "GAME_OVER":
            return False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.paused = not self.paused
            return True

        if self.paused:
            self._handle_pause_menu_action(event)
            return True

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
            self._take_photo_toast()
            return True

        return False

    def _handle_pause_menu_action(self, event):
        action = self.pause_menu.handle_event(event) if self.pause_menu else None
        if action == "resume":
            self.paused = False
        elif action == "settings":
            self.open_settings()
        elif action == "to_start":
            self.request_to_start = True
        elif action == "quit":
            self.request_quit = True
        elif action == "photo":
            self._take_photo_toast()

    def _handle_scene_key_event(self, event):
        if event.type != pygame.KEYDOWN:
            return False

        if self.scene == "GAME_OVER":
            if event.key == pygame.K_ESCAPE:
                self.running = False
                return True
            if event.key == pygame.K_r:
                self.restart_game()
                return True

        if self.scene == "EVOLVE_MENU" and event.key == pygame.K_ESCAPE:
            self.scene = "MAIN"
            return True

        return False

    def _handle_scene_mouse_event(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN:
            return
        if self.scene == "MAIN":
            self.handle_click_main(event.pos)
        elif self.scene == "EVOLVE_MENU":
            self.handle_click_evolve_menu(event.pos)

    def update(self, dt: float):
        if self.toast_timer > 0.0:
            self.toast_timer = max(0.0, float(self.toast_timer) - float(dt))
        if self.cat_dialogue_timer > 0.0:
            self.cat_dialogue_timer = max(0.0, float(self.cat_dialogue_timer) - float(dt))

        if self.paused:
            return

    def _take_photo_toast(self):
        try:
            if not self.cat:
                path = take_photo(self.screen, player_name="player")
            else:
                path = take_photo(
                    self.screen,
                    player_name=getattr(self.cat, "name", "player") or "player",
                    day=getattr(self.state, "day", None),
                    stage=getattr(self.cat, "stage", None),
                )
            self.toast_text = f"사진 저장됨: {os.path.basename(path)}"
        except (OSError, TypeError, ValueError, pygame.error):
            self.toast_text = "사진 저장 실패"
        self.toast_timer = 2.5

    def _draw_photo_toast(self):
        if self.toast_timer <= 0.0 or not self.toast_text:
            return

        text = self.toast_text
        font = self.hint_font if hasattr(self, "hint_font") and self.hint_font else self.font
        label = font.render(text, True, (255, 255, 255))

        pad_x, pad_y = 10, 8
        bg_w = label.get_width() + pad_x * 2
        bg_h = label.get_height() + pad_y * 2
        bg = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 170))
        bg.blit(label, (pad_x, pad_y))

        x = 12
        y = self.screen.get_height() - bg_h - 12
        self.screen.blit(bg, (x, y))

    def _draw_cat_dialogue(self):
        if self.scene != "MAIN":
            return
        if getattr(self, "paused", False):
            return
        if self.cat_dialogue_timer <= 0.0 or not self.cat_dialogue_text:
            return

        cat_rect = getattr(self, "_cat_rect", None)
        if cat_rect is None:
            return

        font = self.hint_font if hasattr(self, "hint_font") and self.hint_font else self.font
        label = font.render(self.cat_dialogue_text, True, (0, 0, 0))
        pad_x, pad_y = 12, 8
        bubble_w = min(WIDTH - 24, label.get_width() + pad_x * 2)
        bubble_h = label.get_height() + pad_y * 2
        bubble = pygame.Rect(0, 0, bubble_w, bubble_h)
        bubble.centerx = WIDTH // 2
        bubble.bottom = max(42, cat_rect.top - 22)

        pygame.draw.rect(self.screen, (255, 255, 255), bubble, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), bubble, width=2, border_radius=10)
        text_rect = label.get_rect(center=bubble.center)
        self.screen.blit(label, text_rect)

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

        self._draw_game_over_contents(panel_rect, panel_x, panel_y)

    def _draw_game_over_contents(self, panel_rect, panel_x, panel_y):
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
        pygame.draw.line(
            self.screen,
            (220, 220, 220),
            (panel_x + 16, sep_y),
            (panel_rect.right - 16, sep_y),
            1,
        )

        log = self.ending_log
        y = sep_y + 14
        for line in self._game_over_log_lines(log):
            t = self.font.render(line, True, (50, 50, 50))
            self.screen.blit(t, (panel_x + 24, y))
            y += 22

    def _game_over_log_lines(self, log):
        return [
            f"생존 일수 : {log.get('day', 0)}일",
            f"배고픔 : {log.get('hunger', 0)}",
            f"피로 : {log.get('tiredness', 0)}",
            f"행복 : {log.get('happiness', 0)}",
            f"청결 : {log.get('cleanliness', 0)}",
        ]

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

    def _finish_frame(self, include_pause=True):
        if self.ach:
            draw_toasts(self.screen, self.font, self.ach)

        if include_pause and self.paused and self.pause_menu:
            self.pause_menu.draw()
        self._draw_cat_dialogue()
        self._draw_photo_toast()
        pygame.display.flip()

    def _draw_game_view_base(self):
        self.screen.blit(self.back_image, self.back_rect)
        self._draw_day_phase_info()
        self._draw_money()
        self._draw_stats()
        self._draw_cat_sprite()

    def _draw_day_phase_info(self):
        diff_label = state.get_difficulty_label(self.difficulty)
        phase_label = "아침" if self.state.time_phase == state.MORNING else "밤"
        info = f"{self.state.day}일차 - {phase_label} ({diff_label})"
        self.screen.blit(self.font.render(info, True, (0, 0, 0)), (INFO_X, INFO_Y))

    def _draw_money(self):
        money = getattr(self.state, "money", 0)
        if self.coin_image:
            self.screen.blit(self.coin_image, (INFO_X, INFO_Y + 22))
            coin_text = self.coin_font.render(f"{money}", True, (0, 0, 0))
            self.screen.blit(coin_text, (INFO_X + 42, INFO_Y + 28))
            return

        coin_text = self.coin_font.render(f"🪙 {money}", True, (0, 0, 0))
        self.screen.blit(coin_text, (INFO_X, INFO_Y + 22))

    def _draw_stats(self):
        self.draw_bar(STAT_X, STAT_Y_START, "배고픔", self.cat.hunger, (255, 100, 100))
        self.draw_bar(STAT_X, STAT_Y_START + STAT_GAP, "피로", self.cat.tiredness, (100, 100, 255))
        self.draw_bar(STAT_X, STAT_Y_START + 2 * STAT_GAP, "행복", self.cat.happiness, (100, 255, 100))
        self.draw_bar(STAT_X, STAT_Y_START + 3 * STAT_GAP, "청결", self.cat.cleanliness, (180, 180, 180))

    def _draw_cat_sprite(self):
        if not self.cat or not self.cat.image_path:
            self._cat_rect = None
            return

        cat_stage = getattr(self.cat, "stage", None)
        if self._cat_image_path != self.cat.image_path or self._cat_image_stage != cat_stage:
            self._cat_image_path = self.cat.image_path
            self._cat_image_stage = cat_stage
            self._cat_image = load_image(self.cat.image_path, alpha=True)
            self._cat_display_image, self._cat_display_body_rect = self._prepare_cat_display_image(self._cat_image)

        cat_img = self._cat_display_image
        if cat_img is None:
            self._cat_rect = None
            return

        cat_rect = self._cat_display_rect(cat_img)
        self._cat_rect = cat_rect
        self.screen.blit(cat_img, cat_rect)

        name_text = self.name_font.render(f"{self.cat.name} - {self.cat.stage}", True, (0, 0, 0))
        name_rect = name_text.get_rect(center=(WIDTH // 2, cat_rect.top - NAME_Y_OFFSET))
        self.screen.blit(name_text, name_rect)

    def _prepare_cat_display_image(self, image):
        if image is None:
            return None, None

        visible_rect = self._visible_alpha_rect(image)
        if visible_rect.width > 0 and visible_rect.height > 0:
            image = image.subsurface(visible_rect).copy()

        body_rect = self._main_alpha_rect(image)
        layout = self._cat_image_layout()
        max_w, max_h = layout.get("max_size", CAT_STAGE_MAX_SIZE.get(getattr(self.cat, "stage", None), (220, 220)))
        width, height = image.get_size()
        if width <= 0 or height <= 0 or body_rect.width <= 0 or body_rect.height <= 0:
            return None, None

        area_h = layout.get("bottom", CAT_AREA_BOTTOM) - CAT_AREA_TOP
        scale = min(
            max_w / body_rect.width,
            max_h / body_rect.height,
            CAT_AREA_WIDTH / width,
            area_h / height,
            1.0,
        )
        if scale >= 1.0:
            return image, body_rect

        target_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        display = pygame.transform.smoothscale(image, target_size)
        display_body_rect = pygame.Rect(
            int(round(body_rect.x * scale)),
            int(round(body_rect.y * scale)),
            max(1, int(round(body_rect.width * scale))),
            max(1, int(round(body_rect.height * scale))),
        )
        return display, display_body_rect

    def _main_alpha_rect(self, image):
        fallback = image.get_bounding_rect(min_alpha=1)
        mask = pygame.mask.from_surface(image, 8)
        components = mask.connected_components()
        if not components:
            return fallback

        component = max(components, key=lambda item: item.count())
        rects = component.get_bounding_rects()
        if not rects:
            return fallback

        main_rect = pygame.Rect(rects[0])
        for rect in rects[1:]:
            main_rect.union_ip(rect)
        return main_rect

    def _visible_alpha_rect(self, image):
        fallback = image.get_bounding_rect(min_alpha=1)
        mask = pygame.mask.from_surface(image, 8)
        components = mask.connected_components()
        rects = []
        for component in components:
            for rect in component.get_bounding_rects():
                if rect.width > 0 and rect.height > 0:
                    rects.append(pygame.Rect(rect))

        if not rects:
            return fallback

        visible_rect = rects[0].copy()
        for rect in rects[1:]:
            visible_rect.union_ip(rect)
        return visible_rect

    def _cat_display_rect(self, cat_img):
        layout = self._cat_image_layout()
        area_bottom = layout.get("bottom", CAT_AREA_BOTTOM)
        area = pygame.Rect((WIDTH - CAT_AREA_WIDTH) // 2, CAT_AREA_TOP, CAT_AREA_WIDTH, area_bottom - CAT_AREA_TOP)
        rect = cat_img.get_rect()
        body_rect = getattr(self, "_cat_display_body_rect", None)
        if body_rect is None:
            body_rect = rect.copy()

        rect.x = int(round(area.centerx - body_rect.centerx))
        rect.bottom = area.bottom
        rect.move_ip(*layout.get("offset", (0, 0)))

        if rect.top < area.top:
            rect.top = area.top
        if rect.bottom > area.bottom:
            rect.bottom = area.bottom
        if rect.left < area.left:
            rect.left = area.left
        if rect.right > area.right:
            rect.right = area.right
        return rect

    def _cat_image_layout(self):
        image_path = getattr(self.cat, "image_path", "") if self.cat else ""
        return CAT_IMAGE_LAYOUT_OVERRIDES.get(os.path.basename(image_path), {})

    def _draw_arrow_button(self, rect, label):
        pygame.draw.rect(self.screen, (220, 220, 220), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        arrow = self.font.render(label, True, (0, 0, 0))
        self.screen.blit(arrow, arrow.get_rect(center=rect.center))

    def _draw_care_panel(self):
        if not self.panel_open:
            self._draw_arrow_button(ARROW_RECT, "◀")
            return

        panel_x = WIDTH - PANEL_W - 8
        self.draw_button(self._panel_close_rect(panel_x), "▶ 닫기", self.panel_font)

        for index, label in enumerate(CARE_ACTION_LABELS):
            rect = self._panel_button_rect(panel_x, index)
            if index < len(CARE_ACTION_KEYS):
                self.draw_button_state(rect, label, self.panel_font, not self.actions_used[CARE_ACTION_KEYS[index]])
            else:
                self.draw_button(rect, label, self.panel_font)

    def _draw_menu_panel(self):
        if not self.left_panel_open:
            self._draw_arrow_button(LEFT_ARROW_RECT, "▶")
            return

        panel_x = 8
        self.draw_button(self._panel_close_rect(panel_x), "닫기 ◀", self.panel_font)
        for index, label in enumerate(MENU_ACTION_LABELS):
            self.draw_button(self._panel_button_rect(panel_x, index), label, self.panel_font)

    def draw(self):
        if self.scene == "EVOLVE":
            self.draw_evolve()
            self._finish_frame()
            return

        if self.scene == "EVOLVE_MENU":
            self.draw_evolve_menu()
            self._finish_frame()
            return

        if self.scene == "GAME_OVER":
            self.draw_game_over()
            self._finish_frame(include_pause=False)
            return

        self._draw_game_view_base()
        self._draw_care_panel()
        self._draw_menu_panel()
        self.draw_button(self._advance_rect(), "다음 시간", self.tab_font)
        self._finish_frame()

    def draw_evolve(self):
        if not self.paused:
            self.evolve_timer += 1
        self.screen.fill((0, 0, 0))

        text1 = self.big_font.render("진화 성공!", True, (255, 255, 255))
        text2 = self.big_font.render(f"{self.cat.stage}", True, (255, 255, 0))

        self.screen.blit(text1, (WIDTH // 2 - text1.get_width() // 2, 220))
        self.screen.blit(text2, (WIDTH // 2 - text2.get_width() // 2, 260))

        if self.evolve_timer > 120:
            self.scene = "MAIN"

    def draw_evolve_menu(self):
        self._draw_game_view_base()

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
        pygame.draw.line(
            self.screen,
            (220, 220, 220),
            (panel_x + 16, panel_y + 50),
            (panel_x + panel_w - 16, panel_y + 50),
            1,
        )

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
