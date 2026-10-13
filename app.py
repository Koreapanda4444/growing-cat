import pygame
import sys
import os
import random
import math
from cat import Cat
import state
from game import MiniGameScreen
from shop import ShopUI
from bag import BagUI
from album import AlbumUI
from competition_ui import CompetitionUI
import save
import evolution
import competition
import daily_events
import daily_missions
from config import asset_path, base_path
from items import inventory_item_from_shop_id, normalize_inventory, normalize_inventory_item
from pg_utils import GameQuit, load_font, load_image, load_sound, play_music
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

CARE_ACTION_LABELS = ("밥", "놀기", "씻기", "잠자기", "진화", "특별 돌봄")
CARE_ACTION_KEYS = ("feed", "play", "clean", "sleep")
CARE_STAT_KEYS = {"feed": "hunger", "play": "happiness", "clean": "cleanliness", "sleep": "tiredness"}
FRIENDSHIP_ACTION_KEYS = (*CARE_ACTION_KEYS, "pet")
MENU_ACTION_LABELS = ("설정", "미니게임", "대회", "상점", "가방", "업적", "앨범", "오늘의 활동")
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


CAT_FRIENDSHIP_LINES = {
    "낯선 사이": ("너를 천천히 알아가는 중이다냥.", "조심히 다가가도 괜찮겠냥?", "아직은 조금 낯설다냥."),
    "익숙한 사이": ("이제 네 발소리를 안다냥.", "오늘도 와줘서 반갑다냥.", "손길이 점점 익숙해진다냥."),
    "친구": ("넌 내 좋은 친구다냥!", "같이 보내는 시간이 좋다냥.", "오늘도 옆자리를 남겨뒀다냥."),
    "단짝": ("눈만 봐도 마음이 통한다냥.", "네 곁이면 안심된다냥.", "우리만의 놀이를 하자냥."),
    "가족": ("네 곁이 내 집이다냥.", "오래오래 함께 지내자냥.", "언제나 네 편이다냥."),
}

CAT_STAGE_LINES = {
    evolution.BABY: ("작은 발로 세상을 배우는 중이다냥.", "조금씩 커지는 게 느껴진다냥.", "아직 궁금한 게 많다냥!"),
    evolution.ADULT: ("이제 제법 의젓해졌다냥.", "어릴 때보다 높이 뛸 수 있다냥.", "널 지켜보는 건 내 일이다냥."),
    evolution.LION: ("갈기가 근사하게 자랐다냥!", "작게 어흥 해보겠다냥.", "사자여도 손길은 좋다냥."),
    evolution.DINO: ("큰 몸으로도 살살 다가간다냥.", "공룡이어도 네 고양이다냥!", "꼬리를 조심히 움직이겠다냥."),
}


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
        self.competition = competition.new_competition_data()
        self.scene = "MAIN"
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self.friendship_used = {key: False for key in FRIENDSHIP_ACTION_KEYS}
        self.special_care = state.normalize_special_care(None, self.state.day)
        self.daily_events = daily_events.new_data()
        self.daily_missions = daily_missions.new_data()
        self._cat_image_path = None
        self._cat_image = None
        self._cat_image_stage = None
        self._cat_display_image = None
        self._cat_display_body_rect = None
        self._cat_rect = None
        self._cat_click_count = 0
        self._dialogue_history = []
        self._reset_cat_animation()
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
        saved_image = cat_data.get("image")
        if isinstance(saved_image, str):
            available = self.cat.available_images()
            candidates = {Path(path).name: path for path in available}
            image_name = saved_image.replace(chr(92), "/").split("/")[-1]
            if saved_image.replace(chr(92), "/").startswith("cats/") and image_name in candidates:
                self.cat.image_path = candidates[image_name]
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
        usage = data.get("care_usage")
        if (isinstance(usage, dict) and usage.get("day") == self.state.day
                and usage.get("phase") == self.state.time_phase
                and isinstance(usage.get("used"), dict)):
            self.actions_used = {key: bool(usage["used"].get(key, False)) for key in CARE_ACTION_KEYS}
        else:
            self.actions_used = {key: False for key in CARE_ACTION_KEYS}
        self.cat.friendship = state.normalize_friendship(cat_data.get("friendship", 0))
        friendship_usage = data.get("friendship_usage")
        if (isinstance(friendship_usage, dict) and friendship_usage.get("day") == self.state.day
                and friendship_usage.get("phase") == self.state.time_phase
                and isinstance(friendship_usage.get("used"), dict)):
            self.friendship_used = {
                key: bool(friendship_usage["used"].get(key, False)) for key in FRIENDSHIP_ACTION_KEYS
            }
        else:
            self.friendship_used = {key: False for key in FRIENDSHIP_ACTION_KEYS}
        self.special_care = state.normalize_special_care(data.get("special_care"), self.state.day)
        self.competition = competition.normalize_competition_data(data.get("competition"))
        self.daily_events = daily_events.normalize(data.get("daily_events"))
        saved_missions = daily_missions.normalize(data.get("daily_missions"))
        self.daily_missions = daily_missions.for_day(saved_missions, self.state)
        missions_created = saved_missions != self.daily_missions
        self.scene = "MAIN"
        self.check_game_over()
        if not self.game_over_reason:
            if self._prepare_daily_event() or missions_created:
                save.save_game(self.make_save_data())
            self._show_pending_event()

    def load_image(self, filename):
        image = load_image(filename, alpha=True)
        if image is None:
            pygame.quit()
            sys.exit()
        return image

    def _save_if_game_active(self):
        if self.app_mode == "GAME" and self.cat:
            return save.save_game(self.make_save_data())
        return False

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            events = pygame.event.get()
            try:
                self.handle_events(events)
            except GameQuit:
                self.request_quit = True

            if self.request_quit:
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

        self._save_if_game_active()
        pygame.quit()

    def start_new_game(self, name: str, difficulty: str = "normal", personality: str = "energetic"):
        name = str(name or "").strip()
        if not name:
            return

        self.paused = False
        self.request_to_start = False
        self.difficulty = state.normalize_difficulty(difficulty)
        self.personality = state.normalize_personality(personality)

        self.state = state.GameState(self.difficulty, self.personality)
        if not hasattr(self.state, "minigame_used"):
            self.state.minigame_used = state.new_minigame_usage()

        self.cat = Cat(name, "아기고양이", difficulty=self.difficulty, personality=self.personality)
        self.inventory = {}
        self.competition = competition.new_competition_data()
        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self.friendship_used = {key: False for key in FRIENDSHIP_ACTION_KEYS}
        self.special_care = state.normalize_special_care(None, self.state.day)
        self.daily_events = daily_events.new_data()
        self.daily_missions = daily_missions.new_data()
        self._cat_image_path = None
        self._cat_image = None
        self._cat_image_stage = None
        self._cat_display_image = None
        self._cat_display_body_rect = None
        self._cat_rect = None
        self._cat_click_count = 0
        self._dialogue_history = []
        self._reset_cat_animation()
        self.cat_dialogue_text = ""
        self.cat_dialogue_timer = 0.0
        self.panel_open = False
        self.left_panel_open = False
        self.game_over_reason = None
        self.ending_log = {}

        self.scene = "MAIN"
        self.app_mode = "GAME"
        self.daily_missions = daily_missions.for_day(self.daily_missions, self.state)
        self._prepare_daily_event()
        self._show_pending_event()
        save.save_game(self.make_save_data())

    def advance_time(self):
        if not self.cat or self.scene != "MAIN" or self.cat.check_game_over():
            return
        if self.daily_events["status"] == "pending":
            self.scene = "EVENT"
            return
        phase = self.state.advance_time()
        self.special_care = state.normalize_special_care(self.special_care, self.state.day)
        if phase == state.NIGHT:
            self.cat.on_night()
        else:
            self.cat.on_morning()
            self._grant_day_reward()

        self.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self.friendship_used = {key: False for key in FRIENDSHIP_ACTION_KEYS}
        self.state.minigame_used = state.new_minigame_usage()

        if self.cat.mood in ("hungry", "tired", "uncomfortable", "lonely"):
            self.cat.change_friendship(-1)
        self.check_game_over()
        evolved = not self.game_over_reason and phase == state.MORNING and self._try_auto_evolve()
        if evolved:
            self.scene = "EVOLVE"
            self.evolve_timer = 0

        self.check_game_over()
        if phase == state.MORNING and not self.game_over_reason:
            self.daily_missions = daily_missions.for_day(self.daily_missions, self.state)
            self._prepare_daily_event()
            if self.scene != "EVOLVE":
                self._show_pending_event()
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
            self.cat.alive = result != "DEAD"
            self.cat.runaway = result == "RUNAWAY"
            self.paused = False

    def restart_game(self):
        self.state = state.GameState()
        self.difficulty = "normal"
        self.personality = "energetic"
        self._init_game_defaults()
        self.paused = False
        self.request_to_start = False
        self.cat_dialogue_text = ""
        self.cat_dialogue_timer = 0.0
        self.toast_text = ""
        self.toast_timer = 0.0
        self.flow.reset_to_start()
        self.app_mode = "START_FLOW"

    def _reset_game(self):
        self.ach = self._init_achievements()
        self.restart_game()

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
            "care_usage": {
                "day": clean_day,
                "phase": clean_phase,
                "used": {key: bool(self.actions_used.get(key, False)) for key in CARE_ACTION_KEYS},
            },
            "friendship_usage": {
                "day": clean_day,
                "phase": clean_phase,
                "used": {key: bool(self.friendship_used.get(key, False)) for key in FRIENDSHIP_ACTION_KEYS},
            },
            "special_care": state.normalize_special_care(self.special_care, clean_day),
            "daily_events": daily_events.normalize(self.daily_events),
            "daily_missions": daily_missions.normalize(self.daily_missions),
            "competition": competition.copy_for_save(getattr(self, "competition", None)),
            "cat": {
                "name": self.cat.name,
                "stage": self.cat.stage,
                "friendship": state.normalize_friendship(self.cat.friendship),
                "image": (
                    f"cats/{Path(self.cat.image_path).parent.name}/{Path(self.cat.image_path).name}"
                    if self.cat.image_path and Path(self.cat.image_path).parent.name in ("baby", "adult", "lion", "dino")
                    else None
                ),
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
            self._reset_game,
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

    def open_minigame(self):
        MiniGameScreen(self.screen, self.state, self.ach, self._save_if_game_active, on_activity=self._record_daily_activity).run()

    def open_competition(self):
        self.panel_open = False
        self.left_panel_open = False
        CompetitionUI(
            self.screen,
            self.cat,
            self.state,
            self.inventory,
            self.competition,
            self.enter_competition,
            self.play_click_sound,
        ).run()

    def enter_competition(self):
        if not self.cat or self.cat.check_game_over():
            return {"ok": False, "message": "고양이가 없습니다.", "competition_data": self.competition}

        day = max(1, safe_int(getattr(self.state, "day", 1), 1))
        comp = competition.competition_for_day(day)
        if not competition.is_event_day(day):
            return {"ok": False, "message": "오늘은 대회 날이 아닙니다.", "competition_data": self.competition}
        if competition.entered_today(self.competition, day):
            return {"ok": False, "message": "오늘은 이미 참가했습니다.", "competition_data": self.competition}

        fee = competition.entry_fee(comp, self.difficulty)
        try:
            money = max(0, int(self.state.money))
        except (TypeError, ValueError):
            money = 0
        if money < fee:
            return {"ok": False, "message": "참가비가 부족합니다.", "competition_data": self.competition}

        self.state.money = money - fee
        score = competition.roll_score(comp["id"], self.cat, self.state, self.inventory)
        grade = competition.grade_for_score(score, self.difficulty)
        reward = competition.reward_for_grade(comp, grade, self.difficulty)
        self.state.money += reward
        self.competition = competition.record_result(
            self.competition,
            day=day,
            comp=comp,
            grade=grade,
            score=score,
            reward=reward,
        )

        if self.ach:
            self.ach.on_event("competition_entered", grade=grade)
            if reward > 0:
                self.ach.on_event("coins_earned", amount=reward)
        save.save_game(self.make_save_data())
        return {
            "ok": True,
            "message": f"{grade}등급! {score}점 / +{reward}코인",
            "competition_data": self.competition,
        }

    def open_bag(self):
        BagUI(self.screen, self.inventory, self.use_item, self.play_click_sound).run()

    def open_achievements(self):
        self.panel_open = False
        self.left_panel_open = False
        AchievementsUI(self.screen, self.ach, self.play_click_sound).run()

    def open_album(self):
        self.panel_open = False
        self.left_panel_open = False
        AlbumUI(self.screen, self.play_click_sound).run()

    def _record_daily_activity(self, activity):
        self.daily_missions, changed = daily_missions.record(self.daily_missions, activity)
        if changed and daily_missions.completed(self.daily_missions):
            self.toast_text = "오늘의 일일 목표를 모두 달성했습니다!"
            self.toast_timer = 2.5
        return changed

    def claim_daily_mission(self, index):
        if self.scene != "DAILY" or not self.cat or self.cat.check_game_over():
            return False
        before = daily_missions.normalize(self.daily_missions)
        money_before = self.state.money
        inventory_before = dict(self.inventory)
        data, reward = daily_missions.claim(self.daily_missions, index, self.state, self.inventory)
        if reward is None:
            return False
        self.daily_missions = data
        if not save.save_game(self.make_save_data()):
            self.daily_missions = before
            self.state.money = money_before
            self.inventory.clear()
            self.inventory.update(inventory_before)
            self.toast_text = "보상 저장 실패. 다시 받아주세요."
            self.toast_timer = 2.5
            return False
        if self.ach:
            self.ach.on_event("coins_earned", amount=reward["coins"])
        self.toast_text = f"미션 보상 +{reward['coins']}코인"
        if reward["completed_today"]:
            self.toast_text += f" / 연속 {data['streak']}일"
        if reward["items"]:
            self.toast_text += " / 사료 +1"
        self.toast_timer = 2.5
        return True

    def _prepare_daily_event(self):
        previous_day = self.daily_events["day"]
        self.daily_events = daily_events.roll_for_day(self.daily_events, self.state.day, self.cat)
        return self.daily_events["day"] != previous_day

    def _show_pending_event(self):
        if self.daily_events["status"] == "pending" and not self.game_over_reason:
            self.scene = "EVENT"

    def open_daily_content(self):
        self.panel_open = False
        self.left_panel_open = False
        self.scene = "DAILY"

    def resolve_daily_event(self, choice=0):
        if self.scene != "EVENT":
            return False
        data, applied = daily_events.resolve(self.daily_events, self.cat, self.state, self.inventory, choice)
        if not applied:
            return False
        self.daily_events = data
        result = data["result"]
        if result["coins"] > 0 and self.ach:
            self.ach.on_event("coins_earned", amount=result["coins"])
        self.toast_text = "이벤트 결과가 오늘의 활동에 기록되었습니다."
        self.toast_timer = 2.5
        self._start_cat_reaction(self.cat.mood)
        self.scene = "DAILY"
        save.save_game(self.make_save_data())
        return True

    def _event_choice_rect(self, index):
        return pygame.Rect(35, 330 + index * 52, 330, 42)

    def _daily_result_text(self, result=None):
        if result is None:
            result = self.daily_events.get("result") or {}
        names = {"hunger": "배고픔", "tiredness": "피로", "happiness": "행복", "cleanliness": "청결"}
        parts = [f"{names[key]} {value:+g}" for key, value in result.get("stats", {}).items() if value]
        if result.get("coins"):
            parts.append(f"코인 {result['coins']:+d}")
        if result.get("friendship"):
            parts.append(f"친밀도 {result['friendship']:+d}")
        parts.extend(f"{item} +{count}" for item, count in result.get("items", {}).items())
        return " / ".join(parts) or "조용히 하루를 보냈습니다."

    def _draw_wrapped_text(self, text, pos, max_width, color=(70, 70, 70), font=None):
        font = font or self.hint_font
        x, y = pos
        line = ""
        for char in str(text):
            if line and font.size(line + char)[0] > max_width:
                self.screen.blit(font.render(line, True, color), (x, y))
                y += font.get_height() + 4
                line = ""
            line += char
        self.screen.blit(font.render(line, True, color), (x, y))
        return y + font.get_height() + 4

    def handle_click_daily_content(self, pos):
        if self.scene == "EVENT":
            event = daily_events.EVENTS.get(self.daily_events["event"])
            for index in range(len(event["choices"]) if event else 0):
                if self._event_choice_rect(index).collidepoint(pos):
                    self.resolve_daily_event(index)
                    return
            if pygame.Rect(100, 490, 200, 30).collidepoint(pos):
                self.scene = "MAIN"
        elif pygame.Rect(120, 530, 160, 34).collidepoint(pos):
            self.scene = "MAIN"
        elif self.daily_events["status"] == "pending" and pygame.Rect(240, 205, 130, 32).collidepoint(pos):
            self.scene = "EVENT"
        else:
            for index in range(len(self.daily_missions["goals"])):
                if self._daily_mission_claim_rect(index).collidepoint(pos):
                    self.claim_daily_mission(index)
                    return

    def open_evolve_menu(self):
        if not self.cat:
            return
        self.panel_open = False
        self.left_panel_open = False
        self.scene = "EVOLVE_MENU"
        self.evolve_menu_timer = 0

    def open_special_care(self):
        if not self.cat or self.cat.check_game_over():
            return
        self.special_care = state.normalize_special_care(self.special_care, self.state.day)
        self.panel_open = False
        self.left_panel_open = False
        self.scene = "SPECIAL_CARE"

    def _special_care_choices(self):
        choices = list(state.SPECIAL_CARE)
        choices.sort(key=lambda action: (
            not self._special_care_preview(action)["allowed"],
            self.cat.mood not in state.SPECIAL_CARE[action]["moods"],
            self.cat.personality != state.SPECIAL_CARE[action]["preferred"],
        ))
        return choices

    def _special_care_preview(self, action):
        repetition = state.special_care_repetition(self.special_care, action, self.state.day)
        return self.cat.special_care_preview(action, repetition)

    def choose_special_care(self, action):
        if self.scene != "SPECIAL_CARE" or not self.cat or action not in state.SPECIAL_CARE:
            return False
        self.special_care = state.normalize_special_care(self.special_care, self.state.day)
        if self.special_care["used"]:
            return False
        repetition = state.special_care_repetition(self.special_care, action, self.state.day)
        result = self.cat.apply_special_care(action, repetition)
        if not result["allowed"]:
            return False
        self.special_care = {"day": self.state.day, "used": True, "last_action": action,
                             "last_used_day": self.state.day, "repeat_count": repetition}
        lines = state.SPECIAL_CARE[action]["lines"]
        self.cat_dialogue_text = self._remember_cat_line(random.choice(
            [line for line in lines if line not in self._dialogue_history] or list(lines)
        ))
        self.cat_dialogue_timer = 2.5
        self._record_daily_activity("special")
        self._start_cat_reaction({"quiet": "calm", "groom": "clean", "hide": "play", "cuddle": "sleep"}[action])
        self.toast_text = f"특별 돌봄 완료 / 친밀도 {result['friendship']:+d}"
        self.toast_timer = 2.0
        self.scene = "MAIN"
        save.save_game(self.make_save_data())
        return True

    def _special_care_card_rect(self, index):
        return pygame.Rect(35, 203 + index * 64, 330, 56)

    def handle_click_special_care(self, pos):
        if pygame.Rect(130, 483, 140, 34).collidepoint(pos):
            self.play_click_sound()
            self.scene = "MAIN"
            return
        for index, action in enumerate(self._special_care_choices()):
            if self._special_care_card_rect(index).collidepoint(pos):
                self.play_click_sound()
                self.choose_special_care(action)
                return

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
        if not self.cat or self.cat.check_game_over() or item not in self.inventory or self.inventory[item] <= 0:
            return

        action = "feed" if item in ("사료", "생선", "츄르") else "play"
        before = getattr(self.cat, CARE_STAT_KEYS[action])
        previous_mood = self.cat.mood
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
        self._record_care_friendship(action, before)
        self._record_daily_activity(action)
        self._start_cat_reaction(action)
        self.cat_dialogue_text = self._remember_cat_line(
            self.cat.care_reaction(action, previous_mood, recent=self._dialogue_history)
        )
        self.cat_dialogue_timer = 2.2
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
        self._record_daily_activity("buy")

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
        self._start_cat_reaction("click")
        mission_changed = self._record_daily_activity("pet")
        self.cat_dialogue_timer = 2.2

        friendship_recorded = not self.friendship_used["pet"]
        if friendship_recorded:
            self.friendship_used["pet"] = True
            if self.cat.mood in ("happy", "calm"):
                self._change_friendship(1)

        image_changed = random.random() < CAT_IMAGE_ROTATE_CHANCE and self.cat.rotate_image()
        if image_changed:
            self._cat_image_path = None
            self._cat_image = None
            self._cat_image_stage = None
            self._cat_display_image = None
            self._cat_display_body_rect = None
        if friendship_recorded or image_changed or mission_changed:
            save.save_game(self.make_save_data())
        return True

    def _change_friendship(self, amount):
        delta = self.cat.change_friendship(amount)
        if delta:
            self.toast_text = f"친밀도 {delta:+d}"
            self.toast_timer = 1.5
        return delta

    def _record_care_friendship(self, action, before):
        if self.friendship_used[action]:
            return
        self.friendship_used[action] = True
        self._change_friendship(self.cat.care_friendship_change(action, before))

    def _remember_cat_line(self, line):
        self._dialogue_history.append(line)
        self._dialogue_history = self._dialogue_history[-4:]
        return line

    def _cat_dialogue_pools(self):
        mood = self.cat.mood
        urgent = mood not in ("happy", "calm")
        personality = state.normalize_personality(self.cat.personality)
        friendship_label, _, _ = state.friendship_progress(self.cat.friendship)
        pools = [
            (55 if urgent else 30, state.MOOD_PROFILE[mood]["lines"]),
            (12 if urgent else 45, CAT_CLICK_LINES[personality]),
            (8 if urgent else 22, CAT_FRIENDSHIP_LINES[friendship_label]),
            (5 if urgent else 18, CAT_STAGE_LINES.get(self.cat.stage, CAT_CLICK_LINES["default"])),
            (3, CAT_CLICK_LINES["default"]),
        ]
        for stat_name, threshold, lines in CAT_NEED_LINES:
            value = getattr(self.cat, stat_name)
            deficit = threshold - value if stat_name in ("happiness", "cleanliness") else value - threshold
            if deficit >= 0:
                pools.append((70 + deficit * 2, lines))
        return pools

    def _cat_dialogue_line(self):
        available = []
        weights = []
        for weight, lines in self._cat_dialogue_pools():
            choices = [line for line in lines if line not in self._dialogue_history]
            if choices:
                available.append(choices)
                weights.append(weight)
        lines = random.choices(available, weights=weights, k=1)[0]
        return self._remember_cat_line(random.choice(lines))

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
                if self.cat and not self.cat.check_game_over():
                    previous_mood = self.cat.mood
                    before = getattr(self.cat, CARE_STAT_KEYS[key])
                    getattr(self.cat, actions[index])()
                    self._record_care_friendship(key, before)
                    self._record_daily_activity(key)
                    self._start_cat_reaction(key)
                    self.cat_dialogue_text = self._remember_cat_line(
                        self.cat.care_reaction(key, previous_mood, recent=self._dialogue_history)
                    )
                    self.cat_dialogue_timer = 2.2
                    self.actions_used[key] = True
                    save.save_game(self.make_save_data())
                    self.check_game_over()
                return True

        evolve_index = len(CARE_ACTION_KEYS)
        if self._panel_button_rect(panel_x, evolve_index).collidepoint(pos):
            self.play_click_sound()
            self.open_evolve_menu()
            return True
        if self._panel_button_rect(panel_x, evolve_index + 1).collidepoint(pos):
            self.play_click_sound()
            self.open_special_care()
            return True

        return False

    def _handle_menu_panel_click(self, pos):
        panel_x = 8
        if self._panel_close_rect(panel_x).collidepoint(pos):
            self.play_click_sound()
            self.left_panel_open = False
            return True

        actions = (
            self.open_settings,
            self.open_minigame,
            self.open_competition,
            self.open_shop,
            self.open_bag,
            self.open_achievements,
            self.open_album,
            self.open_daily_content,
        )
        for index, action in enumerate(actions):
            if self._panel_button_rect(panel_x, index).collidepoint(pos):
                self.play_click_sound()
                action()
                self._discard_events = True
                return True

        return False

    def handle_events(self, events):
        self._discard_events = False
        if any(event.type == pygame.QUIT for event in events):
            self.request_quit = True
            return
        for event in events:
            if self.request_quit or self.request_to_start or self._discard_events:
                break
            previous = (self.app_mode, self.scene, self.paused)

            if self.app_mode == "START_FLOW":
                self.flow.handle_event(event)
            elif not self._handle_pause_event(event) and not self._handle_scene_key_event(event):
                self._handle_scene_mouse_event(event)
            if previous != (self.app_mode, self.scene, self.paused):
                break

    def _handle_pause_event(self, event):
        if self.app_mode != "GAME" or self.scene == "GAME_OVER":
            return False

        if (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
                and self.scene in ("EVOLVE_MENU", "SPECIAL_CARE", "EVENT", "DAILY") and not self.paused):
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
            self._discard_events = True
        elif action == "to_start":
            self.request_to_start = True
        elif action == "quit":
            self.request_quit = True
        elif action == "photo":
            self._take_photo_toast()
        elif action == "album":
            self.open_album()
            self._discard_events = True

    def _handle_scene_key_event(self, event):
        if event.type != pygame.KEYDOWN:
            return False

        if self.scene == "GAME_OVER":
            if event.key == pygame.K_ESCAPE:
                self.request_quit = True
                return True
            if event.key == pygame.K_r:
                self.restart_game()
                return True

        if self.scene == "DAILY" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
            self.claim_daily_mission(event.key - pygame.K_1)
            return True

        if self.scene == "EVENT" and event.key in (pygame.K_RETURN, pygame.K_1, pygame.K_2, pygame.K_3):
            self.resolve_daily_event(0 if event.key == pygame.K_RETURN else event.key - pygame.K_1)
            return True

        if self.scene == "SPECIAL_CARE" and event.key in (pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4):
            self.choose_special_care(self._special_care_choices()[event.key - pygame.K_1])
            return True

        if self.scene in ("EVOLVE_MENU", "SPECIAL_CARE", "EVENT", "DAILY") and event.key == pygame.K_ESCAPE:
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
        elif self.scene == "SPECIAL_CARE" and event.button == 1:
            self.handle_click_special_care(event.pos)
        elif self.scene in ("EVENT", "DAILY") and event.button == 1:
            self.handle_click_daily_content(event.pos)

    def update(self, dt: float):
        if self.toast_timer > 0.0:
            self.toast_timer = max(0.0, float(self.toast_timer) - float(dt))
        if self.cat_dialogue_timer > 0.0:
            self.cat_dialogue_timer = max(0.0, float(self.cat_dialogue_timer) - float(dt))

        if self.paused or self.scene != "MAIN" or not self.cat:
            return
        self._cat_animation_clock += max(0.0, dt)
        mood = self.cat.mood
        if mood != self._cat_last_mood:
            if self._cat_last_mood is not None and self._cat_reaction_kind is None:
                self._start_cat_reaction(mood)
            self._cat_last_mood = mood
        if self._cat_reaction_kind is not None:
            self._cat_reaction_elapsed += max(0.0, dt)
            if self._cat_reaction_elapsed >= self._cat_reaction_duration:
                self._cat_reaction_kind = None
                self._cat_reaction_elapsed = 0.0

    def _reset_cat_animation(self):
        self._cat_animation_clock = 0.0
        self._cat_reaction_kind = None
        self._cat_reaction_elapsed = 0.0
        self._cat_reaction_duration = 0.0
        self._cat_last_mood = None
        self._cat_animation_cache = {}

    def _start_cat_reaction(self, kind):
        self._cat_reaction_kind = kind
        self._cat_reaction_elapsed = 0.0
        self._cat_reaction_duration = 1.1 if kind in ("sleep", "tired") else 0.75

    def _cat_animation_values(self):
        if self.paused or self.scene != "MAIN":
            return 1.0, 0.0, 0.0, 255
        mood = self.cat.mood
        breath = math.sin(self._cat_animation_clock * (1.8 if mood == "tired" else 2.8))
        scale, dx, dy, alpha = 1.0 + breath * 0.008, 0.0, -max(0.0, breath), 255
        kind = self._cat_reaction_kind
        if kind is None:
            return scale, dx, dy, alpha
        progress = min(1.0, self._cat_reaction_elapsed / self._cat_reaction_duration)
        pulse = math.sin(math.pi * progress)
        wave = math.sin(math.tau * progress * 2)
        if kind in ("click", "play", "happy"):
            dy -= pulse * (7 if mood in ("happy", "calm") else 3)
            scale += pulse * 0.025
            if kind == "play":
                dx = wave * 4
        elif kind in ("feed", "calm", "lonely"):
            scale += pulse * 0.02
            dy -= pulse * 2
        elif kind in ("clean", "uncomfortable", "hungry"):
            dx = wave * 3
            alpha -= int(pulse * 15)
        elif kind in ("sleep", "tired"):
            scale -= pulse * 0.025
            alpha -= int(pulse * 35)
        return scale, dx, dy, alpha

    def _animated_cat_frame(self, image, base_rect):
        scale, dx, dy, alpha = self._cat_animation_values()
        area = self._cat_sprite_area()
        width, height = image.get_size()
        scale = min(scale, area.width / width, area.height / height)
        size = (max(1, round(width * scale)), max(1, round(height * scale)))
        alpha = max(220, min(255, round(alpha / 5) * 5))
        key = (size, alpha)
        frame = self._cat_animation_cache.get(key)
        if frame is None:
            if len(self._cat_animation_cache) >= 48:
                self._cat_animation_cache.clear()
            frame = image if size == image.get_size() and alpha == 255 else pygame.transform.smoothscale(image, size)
            if alpha != 255:
                frame.set_alpha(alpha)
            self._cat_animation_cache[key] = frame
        rect = frame.get_rect(midbottom=(round(base_rect.centerx + dx), round(base_rect.bottom + dy)))
        rect.clamp_ip(area)
        return frame, rect

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
            self.toast_text = f"앨범 저장됨: {os.path.basename(path)}"
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
        y = 490 if self.scene == "DAILY" else self.screen.get_height() - bg_h - 12
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
        self._draw_cat_mood()
        self._draw_friendship()
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

    def _draw_cat_mood(self):
        mood = state.MOOD_PROFILE[self.cat.mood]
        pygame.draw.circle(self.screen, mood["color"], (INFO_X + 5, 90), 4)
        label = self.hint_font.render(f"기분: {mood['label']}", True, mood["color"])
        self.screen.blit(label, (INFO_X + 15, 82))
        profile = state.get_personality_profile(self.cat.personality)
        personality = self.hint_font.render(f"성격: {profile['label']}", True, (60, 60, 60))
        preferred = self.hint_font.render(
            f"좋아하는 돌봄: {state.CARE_LABELS[profile['preferred_action']]}", True, (60, 60, 60)
        )
        self.screen.blit(personality, (INFO_X, 106))
        self.screen.blit(preferred, (INFO_X, 128))

    def _draw_friendship(self):
        value = state.normalize_friendship(self.cat.friendship)
        label, target, progress = state.friendship_progress(value)
        self.screen.blit(self.hint_font.render(f"친밀도: {label}", True, (90, 55, 90)), (INFO_X, 154))
        bar = pygame.Rect(INFO_X, 178, 180, 8)
        pygame.draw.rect(self.screen, (225, 210, 225), bar)
        if progress > 0:
            pygame.draw.rect(self.screen, (175, 100, 160), (bar.x, bar.y, int(bar.width * progress), bar.height))
        pygame.draw.rect(self.screen, (90, 55, 90), bar, 1)
        text = "최고 단계" if value == state.FRIENDSHIP_MAX else f"{value}/{target} · 다음 단계까지 {target - value}"
        self.screen.blit(self.hint_font.render(text, True, (90, 55, 90)), (INFO_X, 192))

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
            self._cat_animation_cache.clear()

        cat_img = self._cat_display_image
        if cat_img is None:
            self._cat_rect = None
            return

        base_rect = self._cat_display_rect(cat_img)
        frame, cat_rect = self._animated_cat_frame(cat_img, base_rect)
        self._cat_rect = cat_rect
        self.screen.blit(frame, cat_rect)

        name_text = self.name_font.render(f"{self.cat.name} - {self.cat.stage}", True, (0, 0, 0))
        name_rect = name_text.get_rect(center=(WIDTH // 2, base_rect.top - NAME_Y_OFFSET))
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

    def _cat_sprite_area(self):
        bottom = self._cat_image_layout().get("bottom", CAT_AREA_BOTTOM)
        return pygame.Rect((WIDTH - CAT_AREA_WIDTH) // 2, CAT_AREA_TOP, CAT_AREA_WIDTH, bottom - CAT_AREA_TOP)

    def _cat_display_rect(self, cat_img):
        layout = self._cat_image_layout()
        area = self._cat_sprite_area()
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
        if self.scene in ("EVENT", "DAILY"):
            self.draw_daily_content()
            self._finish_frame()
            return

        if self.scene == "SPECIAL_CARE":
            self.draw_special_care()
            self._finish_frame()
            return

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

    def draw_daily_content(self):
        self.screen.fill((245, 245, 245))
        self.screen.blit(self.big_font.render(f"{self.state.day}일차 · 오늘의 활동", True, (30, 30, 30)), (20, 24))
        event = daily_events.EVENTS.get(self.daily_events["event"])
        self.screen.blit(self.hint_font.render(f"누적 이벤트 완료: {self.daily_events['completed']}회", True, (80, 80, 80)), (20, 54))
        if self.scene == "EVENT" and event:
            panel = pygame.Rect(20, 118, 360, 420)
            pygame.draw.rect(self.screen, (230, 235, 225), panel, border_radius=12)
            pygame.draw.rect(self.screen, (60, 60, 60), panel, 2, border_radius=12)
            self._draw_wrapped_text(event["title"], (35, 143), 330, font=self.big_font)
            y = 185
            for line in event["text"]:
                y = self._draw_wrapped_text(line, (35, y), 330)
            self._draw_wrapped_text(f"이야기 종류: {daily_events.KIND_LABELS[event['kind']]}", (35, 249), 330)
            self._draw_wrapped_text("하루 한 번 발생 / 확인한 결과는 저장됩니다.", (35, 275), 330)
            for index, choice in enumerate(event["choices"]):
                rect = self._event_choice_rect(index)
                result = daily_events.preview_choice(self.daily_events["event"], index, self.cat, self.state, self.inventory)
                enabled = result["available"]
                pygame.draw.rect(self.screen, (220, 225, 215) if enabled else (220, 220, 220), rect, border_radius=5)
                pygame.draw.rect(self.screen, (60, 60, 60), rect, 1, border_radius=5)
                label = self.panel_font.render(f"{index + 1}. {choice['label']}", True, (30, 30, 30) if enabled else (125, 125, 125))
                self.screen.blit(label, (rect.x + 7, rect.y + 4))
                self._draw_wrapped_text(self._daily_result_text(result) if enabled else "코인이 부족합니다.", (rect.x + 7, rect.y + 24), 316, font=self.stat_font)
            self.draw_button(pygame.Rect(100, 490, 200, 30), "나중에 (ESC)", self.panel_font)
            return
        self.screen.blit(self.big_font.render("오늘의 이벤트", True, (30, 30, 30)), (20, 80))
        self._draw_wrapped_text(event["title"] if event else "오늘은 조용한 하루입니다.", (20, 120), 360)
        if self.daily_events["status"] == "pending":
            self._draw_wrapped_text("아직 선택하지 않은 이야기가 있습니다.", (20, 158), 360)
            self.draw_button(pygame.Rect(240, 205, 130, 32), "이벤트 보기", self.panel_font)
        elif event:
            result = self.daily_events.get("result") or {}
            y = self._draw_wrapped_text(result.get("message", "선택한 결과가 기록되었습니다."), (20, 158), 360)
            self._draw_wrapped_text(self._daily_result_text(), (20, y), 360)
        self._draw_daily_missions()
        self.draw_button(pygame.Rect(120, 530, 160, 34), "닫기 (ESC)", self.panel_font)

    def _daily_mission_rect(self, index):
        return pygame.Rect(20, 292 + index * 64, 360, 56)

    def _daily_mission_claim_rect(self, index):
        rect = self._daily_mission_rect(index)
        return pygame.Rect(rect.right - 96, rect.y + 18, 86, 28)

    def _draw_daily_missions(self):
        streak = f"연속 {self.daily_missions['streak']}일 · 최고 {self.daily_missions['best_streak']}일"
        self.screen.blit(self.hint_font.render(streak, True, (90, 65, 90)), (140, 264))
        self.screen.blit(self.big_font.render("일일 목표", True, (30, 30, 30)), (20, 260))
        for index, goal in enumerate(self.daily_missions["goals"]):
            rect = self._daily_mission_rect(index)
            done = goal["progress"] >= goal["target"]
            pygame.draw.rect(self.screen, (215, 235, 215) if done else (230, 230, 230), rect, border_radius=5)
            pygame.draw.rect(self.screen, (70, 70, 70), rect, 1, border_radius=5)
            label = f"{daily_missions.LABELS[goal['id']]} {goal['target']}회"
            self.screen.blit(self.panel_font.render(label, True, (35, 35, 35)), (rect.x + 10, rect.y + 5))
            progress = f"{goal['progress']}/{goal['target']}" + (" · 보상 받음" if goal["claimed"] else f" · +{goal['reward']}코인")
            self.screen.blit(self.hint_font.render(progress, True, (70, 70, 70)), (rect.x + 10, rect.y + 25))
            bar = pygame.Rect(rect.x + 10, rect.y + 46, 220, 5)
            pygame.draw.rect(self.screen, (195, 195, 195), bar)
            pygame.draw.rect(self.screen, (80, 145, 100), (bar.x, bar.y, round(bar.width * goal["progress"] / goal["target"]), bar.height))
            button = self._daily_mission_claim_rect(index)
            self.draw_button_state(button, "받음" if goal["claimed"] else "보상 받기", self.panel_font, done and not goal["claimed"])
        status = "전체 달성 보너스 지급 완료!" if self.daily_missions["bonus_claimed"] else "세 미션 보상을 받으면 연속 달성에 반영됩니다."
        self._draw_wrapped_text(status, (20, 490), 360)


    def draw_special_care(self):
        self._draw_game_view_base()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))
        panel = pygame.Rect(20, 115, 360, 420)
        pygame.draw.rect(self.screen, (245, 245, 245), panel, border_radius=12)
        pygame.draw.rect(self.screen, (60, 60, 60), panel, 2, border_radius=12)
        title = self.big_font.render("특별 돌봄", True, (30, 30, 30))
        self.screen.blit(title, title.get_rect(center=(200, 140)))
        self.screen.blit(self.hint_font.render("하루 한 번 / 같은 선택 연속 시 효과 감소", True, (70, 70, 70)), (35, 165))
        mood_label = state.MOOD_PROFILE[self.cat.mood]["label"]
        self.screen.blit(self.hint_font.render(f"기분: {mood_label} / 숫자 1~4로도 선택", True, (70, 70, 70)), (35, 184))
        names = {"hunger": "배고픔", "tiredness": "피로", "happiness": "행복", "cleanliness": "청결"}
        for index, action in enumerate(self._special_care_choices()):
            info = state.SPECIAL_CARE[action]
            result = self._special_care_preview(action)
            enabled = not self.special_care["used"] and result["allowed"]
            rect = self._special_care_card_rect(index)
            pygame.draw.rect(self.screen, (220, 235, 220) if enabled else (220, 220, 220), rect, border_radius=5)
            pygame.draw.rect(self.screen, (70, 70, 70), rect, 1, border_radius=5)
            recommended = enabled and (self.cat.mood in info["moods"] or self.cat.personality == info["preferred"])
            text = f"{index + 1}. {info['label']}" + (" · 추천" if recommended else "")
            self.screen.blit(self.panel_font.render(text, True, (30, 30, 30) if enabled else (125, 125, 125)), (rect.x + 8, rect.y + 7))
            effects = " / ".join(f"{names[stat]} {delta:+g}" for stat, delta in result["stats"].items())
            if not result["allowed"]:
                effects = "기본 돌봄으로 컨디션을 회복해 주세요."
            self.screen.blit(self.hint_font.render(effects, True, (90, 90, 90)), (rect.x + 8, rect.y + 31))
        status = "오늘은 이미 특별 돌봄을 했습니다." if self.special_care["used"] else "선택 즉시 적용 / 취소하면 사용하지 않습니다."
        self.screen.blit(self.hint_font.render(status, True, (100, 60, 60)), (35, 461))
        self.draw_button(pygame.Rect(130, 483, 140, 34), "닫기 (ESC)", self.panel_font)

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
            self._show_pending_event()

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
