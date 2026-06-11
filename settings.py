import pygame
import save
import time

from config import asset_path
import evolution
from items import ITEM_INFO
from pg_utils import load_font
import state as game_state

WIDTH = 400
HEIGHT = 600
FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")

class SettingsScreen:
    def __init__(self, screen, restart_callback, game=None, play_click_sound=None):
        self.screen = screen
        self.restart_callback = restart_callback
        self.game = game
        self.play_click_sound = play_click_sound
        self.running = True

        self.font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)
        self.message = ""

        self.cheat_rect = pygame.Rect(100, 285, 200, 38)
        self.reset_rect = pygame.Rect(100, 335, 200, 38)
        self.back_rect = pygame.Rect(100, 385, 200, 36)

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
                if self.cheat_rect.collidepoint(event.pos):
                    self._click()
                    if self.game is not None:
                        CheatScreen(self.screen, self.game, self.play_click_sound).run()
                    else:
                        self.message = "게임 중에만 사용 가능"

                elif self.reset_rect.collidepoint(event.pos):
                    self._click()
                    self.reset_data()

                elif self.back_rect.collidepoint(event.pos):
                    self._click()
                    self.running = False

    def _click(self):
        if self.play_click_sound:
            self.play_click_sound()

    def reset_data(self):
        if save.reset_save():
            self.restart_callback()
            self.running = False
            return True
        self.message = "초기화 실패"
        return False

    def draw_button(self, rect, text):
        pygame.draw.rect(self.screen, (230, 230, 230), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        txt = self.font.render(text, True, (0, 0, 0))
        self.screen.blit(txt, txt.get_rect(center=rect.center))

    def draw(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 140))
        self.screen.blit(overlay, (0, 0))

        panel = pygame.Rect(40, 190, 320, 270)
        pygame.draw.rect(self.screen, (245, 245, 245), panel, border_radius=12)
        pygame.draw.rect(self.screen, (0, 0, 0), panel, 2, border_radius=12)

        title = self.big_font.render("설정", True, (0, 0, 0))
        self.screen.blit(title, title.get_rect(center=(WIDTH // 2, 225)))

        self.draw_button(self.cheat_rect, "치트 모드")
        self.draw_button(self.reset_rect, "데이터 초기화")
        self.draw_button(self.back_rect, "뒤로가기")
        if self.message:
            msg = self.font.render(self.message, True, (160, 40, 40))
            self.screen.blit(msg, msg.get_rect(center=(WIDTH // 2, 435)))

        pygame.display.flip()


class CheatScreen:
    def __init__(self, screen, game, play_click_sound=None):
        self.screen = screen
        self.game = game
        self.play_click_sound = play_click_sound
        self.running = True
        self.scroll = 0
        self.message = "개발용 치트 모드"

        self.font = load_font(FONT_PATH, 15)
        self.big_font = load_font(FONT_PATH, 22)
        self.small_font = load_font(FONT_PATH, 13)
        self.close_rect = pygame.Rect(352, 12, 36, 32)
        self.row_h = 35
        self.actions = self._build_actions()

    def _build_actions(self):
        return [
            ("코인 +100", lambda: self._add_money(100)),
            ("코인 +1,000", lambda: self._add_money(1000)),
            ("코인 +10,000", lambda: self._add_money(10000)),
            ("코인 0으로", lambda: self._set_money(0)),
            ("스탯 전부 MAX", self._max_stats),
            ("스탯 안전값", self._safe_stats),
            ("배고픔 위험", lambda: self._set_stat("hunger", 95)),
            ("피로 위험", lambda: self._set_stat("tiredness", 95)),
            ("행복 위험", lambda: self._set_stat("happiness", 5)),
            ("청결 위험", lambda: self._set_stat("cleanliness", 5)),
            ("배고픔 사망", self._force_hunger_death),
            ("가출 상태", self._force_runaway),
            ("게임오버 복구", self._revive_safe),
            ("날짜 +1", lambda: self._add_day(1)),
            ("날짜 +7", lambda: self._add_day(7)),
            ("날짜 +30", lambda: self._add_day(30)),
            ("아침으로", lambda: self._set_phase(game_state.MORNING)),
            ("밤으로", lambda: self._set_phase(game_state.NIGHT)),
            ("관리 행동 초기화", self._reset_actions),
            ("미니게임 초기화", self._reset_minigames),
            ("미니게임 전부 사용", self._use_all_minigames),
            ("아이템 전부 +1", lambda: self._add_all_items(1)),
            ("아이템 전부 +5", lambda: self._add_all_items(5)),
            ("인벤토리 비우기", self._clear_inventory),
            ("진화 조건 맞추기", self._prepare_evolution),
            ("강제 다음 진화", self._force_evolve_next),
            ("아기 단계", lambda: self._set_stage(evolution.BABY)),
            ("어른 단계", lambda: self._set_stage(evolution.ADULT)),
            ("사자 단계", lambda: self._set_stage(evolution.LION)),
            ("공룡 단계", lambda: self._set_stage(evolution.DINO)),
            ("난이도 쉬움", lambda: self._set_difficulty(game_state.DIFFICULTY_EASY)),
            ("난이도 보통", lambda: self._set_difficulty(game_state.DIFFICULTY_NORMAL)),
            ("난이도 어려움", lambda: self._set_difficulty(game_state.DIFFICULTY_HARD)),
            ("성격 활발함", lambda: self._set_personality(game_state.PERSONALITY_ENERGETIC)),
            ("성격 차분함", lambda: self._set_personality(game_state.PERSONALITY_CALM)),
            ("성격 냥냥함", lambda: self._set_personality(game_state.PERSONALITY_LAZY)),
            ("고양이 이미지 변경", self._rotate_cat_image),
            ("업적 전부 해금", self._unlock_all_achievements),
            ("업적 카운터 MAX", self._max_achievement_counters),
            ("이상한 업적 발동", self._trigger_weird_achievement),
            ("강제 저장", self._save_only),
        ]

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
            elif event.type == pygame.MOUSEWHEEL:
                self._scroll_by(-event.y * 42)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event)

    def _handle_click(self, event):
        if self.close_rect.collidepoint(event.pos):
            self._click()
            self.running = False
            return
        if event.button == 4:
            self._scroll_by(-42)
            return
        if event.button == 5:
            self._scroll_by(42)
            return
        if event.button != 1:
            return

        for rect, _, action in self._button_rows():
            if rect.collidepoint(event.pos):
                self._click()
                action()
                return

    def _click(self):
        if self.play_click_sound:
            self.play_click_sound()

    def _scroll_by(self, delta):
        row_count = (len(self.actions) + 1) // 2
        visible_h = HEIGHT - 155
        max_scroll = max(0, row_count * self.row_h - visible_h + 20)
        self.scroll = max(0, min(int(self.scroll) + int(delta), max_scroll))

    def _button_rows(self):
        rows = []
        left_x = 24
        right_x = 205
        y0 = 155 - int(self.scroll)
        btn_w = 170
        btn_h = 28
        for index, (label, action) in enumerate(self.actions):
            col = index % 2
            row = index // 2
            x = left_x if col == 0 else right_x
            y = y0 + row * self.row_h
            rows.append((pygame.Rect(x, y, btn_w, btn_h), label, action))
        return rows

    def _cat(self):
        return getattr(self.game, "cat", None)

    def _state(self):
        return getattr(self.game, "state", None)

    def _save_game(self, message):
        cat = self._cat()
        if cat is None:
            self.message = "고양이 없음"
            return False
        self.game.check_game_over()
        if getattr(self.game, "scene", "MAIN") == "GAME_OVER" and getattr(cat, "alive", True) and not getattr(cat, "runaway", False):
            self.game.scene = "MAIN"
            self.game.game_over_reason = None
        save.save_game(self.game.make_save_data())
        self.message = message
        return True

    def _add_money(self, amount):
        st = self._state()
        if st is None:
            return
        st.money = max(0, int(getattr(st, "money", 0)) + int(amount))
        self._save_game(f"코인 +{amount}")

    def _set_money(self, amount):
        st = self._state()
        if st is None:
            return
        st.money = max(0, int(amount))
        self._save_game(f"코인 {amount}")

    def _max_stats(self):
        cat = self._cat()
        if cat is None:
            return
        cat.hunger = 0
        cat.tiredness = 0
        cat.happiness = game_state.MAX_STAT
        cat.cleanliness = game_state.MAX_STAT
        cat.alive = True
        cat.runaway = False
        self.game.scene = "MAIN"
        self.game.game_over_reason = None
        self._save_game("스탯 MAX")

    def _safe_stats(self):
        cat = self._cat()
        if cat is None:
            return
        cat.hunger = 10
        cat.tiredness = 10
        cat.happiness = 90
        cat.cleanliness = 90
        cat.alive = True
        cat.runaway = False
        self.game.scene = "MAIN"
        self.game.game_over_reason = None
        self._save_game("스탯 안전값")

    def _set_stat(self, stat_name, value):
        cat = self._cat()
        if cat is None:
            return
        setattr(cat, stat_name, game_state.clamp(value))
        cat._clamp_all()
        self._save_game(f"{stat_name}={value}")

    def _force_hunger_death(self):
        cat = self._cat()
        if cat is None:
            return
        cat.hunger = game_state.MAX_STAT
        cat.alive = False
        self.game.check_game_over()
        save.save_game(self.game.make_save_data())
        self.message = "배고픔 사망"

    def _force_runaway(self):
        cat = self._cat()
        if cat is None:
            return
        cat.happiness = 0
        cat.runaway = True
        self.game.check_game_over()
        save.save_game(self.game.make_save_data())
        self.message = "가출 상태"

    def _revive_safe(self):
        cat = self._cat()
        if cat is None:
            return
        cat.alive = True
        cat.runaway = False
        self.game.scene = "MAIN"
        self.game.game_over_reason = None
        self.game.ending_log = {}
        self._safe_stats()
        self.message = "게임오버 복구"

    def _add_day(self, amount):
        st = self._state()
        if st is None:
            return
        st.day = max(1, int(getattr(st, "day", 1)) + int(amount))
        self._save_game(f"날짜 +{amount}")

    def _set_phase(self, phase):
        st = self._state()
        if st is None:
            return
        st.time_phase = phase
        self._save_game("아침" if phase == game_state.MORNING else "밤")

    def _reset_actions(self):
        self.game.actions_used = {"feed": False, "play": False, "clean": False, "sleep": False}
        self._save_game("관리 행동 초기화")

    def _reset_minigames(self):
        st = self._state()
        if st is None:
            return
        st.minigame_used = game_state.new_minigame_usage()
        self._save_game("미니게임 초기화")

    def _use_all_minigames(self):
        st = self._state()
        if st is None:
            return
        st.minigame_used = {key: True for key in game_state.MINIGAME_KEYS}
        self._save_game("미니게임 전부 사용")

    def _add_all_items(self, amount):
        inv = getattr(self.game, "inventory", None)
        if inv is None:
            self.game.inventory = {}
            inv = self.game.inventory
        for item_id in ITEM_INFO:
            inv[item_id] = max(0, int(inv.get(item_id, 0))) + int(amount)
        self._save_game(f"아이템 전부 +{amount}")

    def _clear_inventory(self):
        self.game.inventory = {}
        self._save_game("인벤토리 비움")

    def _prepare_evolution(self):
        cat = self._cat()
        st = self._state()
        if cat is None or st is None:
            return
        if cat.stage == evolution.BABY:
            st.day = max(int(st.day), 7)
            st.money = max(int(st.money), self.game._current_evolution_cost(evolution.BABY))
        elif cat.stage == evolution.ADULT:
            st.day = max(int(st.day), 21)
            st.money = max(int(st.money), self.game._current_evolution_cost(evolution.ADULT))
            self.game.inventory["고기"] = max(1, int(self.game.inventory.get("고기", 0)))
            cat.hunger = 10
            cat.tiredness = 10
            cat.happiness = 90
            cat.cleanliness = 90
        elif cat.stage == evolution.LION:
            st.day = max(int(st.day), 35)
            st.money = max(int(st.money), self.game._current_evolution_cost(evolution.LION))
            self.game.inventory["뼈"] = max(1, int(self.game.inventory.get("뼈", 0)))
            cat.hunger = 5
            cat.tiredness = 5
            cat.happiness = 95
            cat.cleanliness = 95
        else:
            self.message = "최종 단계"
            return
        cat.alive = True
        cat.runaway = False
        self._save_game("진화 조건 맞춤")

    def _force_evolve_next(self):
        cat = self._cat()
        if cat is None:
            return
        next_stage = evolution.get_next_stage(getattr(cat, "stage", None))
        if not next_stage:
            self.message = "최종 단계"
            return
        cat.evolve_to(next_stage)
        self.game._notify_evolved()
        self.game.scene = "EVOLVE"
        self.game.evolve_timer = 0
        self._save_game("강제 진화")

    def _set_stage(self, stage):
        cat = self._cat()
        if cat is None:
            return
        cat.stage = stage
        cat.image_path = cat.random_image()
        cat.alive = True
        cat.runaway = False
        self.game._cat_image_path = None
        self.game._cat_image = None
        self.game.scene = "MAIN"
        self.game.game_over_reason = None
        self._save_game(f"단계: {stage}")

    def _set_difficulty(self, difficulty):
        difficulty = game_state.normalize_difficulty(difficulty)
        self.game.difficulty = difficulty
        if self._state() is not None:
            self.game.state.difficulty = difficulty
        if self._cat() is not None:
            self.game.cat.difficulty = difficulty
        self._save_game(f"난이도: {game_state.get_difficulty_label(difficulty)}")

    def _set_personality(self, personality):
        personality = game_state.normalize_personality(personality)
        self.game.personality = personality
        if self._state() is not None:
            self.game.state.personality = personality
        if self._cat() is not None:
            self.game.cat.personality = personality
        self._save_game(f"성격: {game_state.get_personality_label(personality)}")

    def _rotate_cat_image(self):
        cat = self._cat()
        if cat is None:
            return
        if cat.rotate_image():
            self.game._cat_image_path = None
            self.game._cat_image = None
            self._save_game("이미지 변경")
        else:
            self.message = "바꿀 이미지 없음"

    def _unlock_all_achievements(self):
        ach = getattr(self.game, "ach", None)
        if ach is None:
            self.message = "업적 없음"
            return
        for ach_def in ach.defs:
            ach.unlocked[ach_def.aid] = time.time()
        ach.save()
        self.message = "업적 전부 해금"

    def _max_achievement_counters(self):
        ach = getattr(self.game, "ach", None)
        if ach is None:
            self.message = "업적 없음"
            return
        for key in ach.counters:
            ach.counters[key] = max(ach.counters.get(key, 0), 10000)
        ach._check_counters()
        ach.save()
        self.message = "업적 카운터 MAX"

    def _trigger_weird_achievement(self):
        ach = getattr(self.game, "ach", None)
        if ach is None:
            self.message = "업적 없음"
            return
        ach.on_event("weird_event")
        self.message = "이상한 업적 발동"

    def _save_only(self):
        self._save_game("저장 완료")

    def _summary_lines(self):
        cat = self._cat()
        st = self._state()
        if cat is None or st is None:
            return ["게임 데이터 없음"]
        diff = game_state.get_difficulty_label(getattr(st, "difficulty", "normal"))
        phase = "아침" if getattr(st, "time_phase", game_state.MORNING) == game_state.MORNING else "밤"
        return [
            f"{getattr(st, 'day', 1)}일차 {phase} / {diff} / {getattr(cat, 'stage', '-')}",
            f"코인 {getattr(st, 'money', 0)}  배고픔 {int(cat.hunger)}  피로 {int(cat.tiredness)}",
            f"행복 {int(cat.happiness)}  청결 {int(cat.cleanliness)}",
        ]

    def draw(self):
        self.screen.fill((235, 235, 235))
        title = self.big_font.render("치트 모드", True, (0, 0, 0))
        self.screen.blit(title, (18, 14))

        pygame.draw.rect(self.screen, (220, 220, 220), self.close_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), self.close_rect, 1)
        close_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(close_text, close_text.get_rect(center=self.close_rect.center))

        y = 48
        for line in self._summary_lines():
            t = self.small_font.render(line, True, (45, 45, 45))
            self.screen.blit(t, (18, y))
            y += 18

        msg = self.small_font.render(self.message, True, (150, 40, 40))
        self.screen.blit(msg, (18, 112))
        hint = self.small_font.render("마우스 휠로 스크롤 / ESC 닫기", True, (80, 80, 80))
        self.screen.blit(hint, (18, 130))

        list_rect = pygame.Rect(0, 150, WIDTH, HEIGHT - 150)
        old_clip = self.screen.get_clip()
        self.screen.set_clip(list_rect)
        for rect, label, _ in self._button_rows():
            if rect.bottom < list_rect.top or rect.top > HEIGHT:
                continue
            pygame.draw.rect(self.screen, (248, 248, 248), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
            text = self.font.render(label, True, (0, 0, 0))
            self.screen.blit(text, text.get_rect(center=rect.center))
        self.screen.set_clip(old_clip)

        pygame.display.flip()
