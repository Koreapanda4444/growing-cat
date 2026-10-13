import pygame
import state as game_state
import minigame_records
from minigames.memory_game import MemoryGame
from minigames.cat_run import CatRunGame
from minigames.cat_follow import CatFollowGame
from minigames.laser_chase import run_laser_chase

from config import asset_path
from pg_utils import screen_events, GameQuit, load_font

CHALLENGE_GAMES = {"jump"}

FPS = 60    

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")


class MiniGameScreen:
    def __init__(self, screen, state=None, ach=None, on_save=None, on_activity=None):
        self.screen = screen
        self.state = state
        self.ach = ach
        self.on_save = on_save
        self.on_activity = on_activity
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)
        self.hint_font = load_font(FONT_PATH, 13)

        self.selected = None
        self.view = "LIST"
        self.challenge = False
        self.btn_mode = pygame.Rect(20, 88, 180, 28)
        self._result_applied = False
        self.btn_records = pygame.Rect(232, 52, 150, 32)

        self.btn_close = pygame.Rect(350, 10, 36, 36)
        self.card_avoid = pygame.Rect(40, 120, 320, 90)
        self.card_memory = pygame.Rect(40, 220, 320, 90)
        self.card_footsteps = pygame.Rect(40, 320, 320, 90)
        self.card_laser = pygame.Rect(40, 420, 320, 90)
        self.btn_start = pygame.Rect(260, 525, 110, 36)

    def run(self):
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            if self.running:
                self.draw()

    def handle_events(self):
        for event in screen_events():
            if event.type == pygame.QUIT:
                raise GameQuit
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                if self.view == "RECORDS":
                    self.view = "LIST"
                else:
                    self.running = False
                return
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                self.handle_click(event.pos)
                if not self.running:
                    return

    def handle_click(self, pos):
        if self.btn_close.collidepoint(pos):
            self.running = False
            return

        if self.btn_records.collidepoint(pos):
            self.view = "LIST" if self.view == "RECORDS" else "RECORDS"
            return
        if self.view == "RECORDS":
            return

        if self.btn_mode.collidepoint(pos):
            if self.selected in CHALLENGE_GAMES:
                self.challenge = not self.challenge
            return
        for key, rect in (("jump", self.card_avoid), ("memory", self.card_memory),
                          ("footsteps", self.card_footsteps), ("laser", self.card_laser)):
            if rect.collidepoint(pos):
                self.selected = key
                if key not in CHALLENGE_GAMES:
                    self.challenge = False
                return
        if self.btn_start.collidepoint(pos):
            self.start_selected_game()

    def start_selected_game(self):
        if not self.selected:
            return
        if not self.state:
            self.running = False
            return

        self._ensure_minigame_usage()
        if self.state.minigame_used.get(self.selected):
            return

        self._result_applied = False
        self.state.minigame_used[self.selected] = True
        if self.on_save and self.on_save() is False:
            self.state.minigame_used[self.selected] = False
            return

        result = self._run_minigame(self.selected)
        self._apply_minigame_result(
            result,
            win_on_positive_coins=self.selected == "jump" and not self.challenge,
        )
        self.running = False
        if isinstance(result, dict) and result.get("quit_requested"):
            raise GameQuit
        if self.on_save:
            self.on_save()

    def _ensure_minigame_usage(self):
        self.state.minigame_used = game_state.normalize_minigame_usage(
            getattr(self.state, "minigame_used", None)
        )

    def _run_minigame(self, minigame_id):
        if minigame_id == "jump":
            return CatRunGame(self.screen, self.state, challenge=self.challenge).run()
        if minigame_id == "memory":
            return MemoryGame(self.screen, self.state).run()
        if minigame_id == "footsteps":
            return CatFollowGame(self.screen, self.state).run()
        if minigame_id == "laser":
            difficulty = getattr(self.state, "difficulty", "normal")
            return run_laser_chase(self.screen, difficulty=difficulty)
        return None

    def _apply_minigame_result(self, result, *, win_on_positive_coins=False):
        if (self._result_applied or self.selected not in minigame_records.GAME_NAMES
                or not isinstance(result, dict) or result.get("cancelled")):
            return
        self._result_applied = True

        if self.on_activity:
            self.on_activity("minigame")
        if self.ach:
            self.ach.on_event("minigame_played")
        coins = self._scaled_result_coins(result)
        if coins > 0:
            self._add_coins(coins)
            if self.ach:
                self.ach.on_event("coins_earned", amount=coins)

        won = bool(result.get("won")) or (win_on_positive_coins and coins > 0)
        if self.ach and won:
            self.ach.on_event("minigame_won")
        self.state.minigame_records = minigame_records.record_result(
            getattr(self.state, "minigame_records", None), self.selected, result, won, self.state.difficulty
        )

    def _scaled_result_coins(self, result):
        try:
            raw_coins = int(result.get("coins", 0))
        except (TypeError, ValueError):
            raw_coins = 0

        difficulty = getattr(self.state, "difficulty", "normal")
        coins = game_state.scale_coin(raw_coins, difficulty, source="minigame")
        return max(0, coins)

    def _add_coins(self, coins):
        try:
            current = max(0, int(self.state.money))
        except (TypeError, ValueError):
            current = 0
        self.state.money = current + max(0, int(coins))

    def draw_card(self, rect, title, selected=False, disabled=False):
        color = (220, 220, 220)
        if selected:
            color = (200, 220, 200) if not disabled else (220, 120, 120)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 2)
        txt = self.font.render(title, True, (0, 0, 0))
        self.screen.blit(txt, (rect.x + 20, rect.y + 20))

    def draw_records(self):
        data = minigame_records.normalize(getattr(self.state, "minigame_records", None))
        for index, (key, name) in enumerate(minigame_records.GAME_NAMES.items()):
            rect = pygame.Rect(20, 120 + index * 100, 360, 90)
            pygame.draw.rect(self.screen, (225, 230, 225), rect)
            pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
            entry = data[key]
            self.screen.blit(self.font.render(name, True, (0, 0, 0)), (rect.x + 12, rect.y + 8))
            self.screen.blit(self.hint_font.render(f"완료 {entry['plays']}회 / 성공 {entry['wins']}회", True, (65, 65, 65)), (rect.x + 12, rect.y + 35))
            self.screen.blit(self.hint_font.render(minigame_records.best_summary(key, entry), True, (65, 65, 65)), (rect.x + 12, rect.y + 56))
            self.screen.blit(self.hint_font.render(f"도전 완료 {entry['challenge_plays']}회 / 달성 {entry['challenge_wins']}회", True, (65, 65, 65)), (rect.x + 12, rect.y + 73))

    def draw(self):
        self.screen.fill((235, 235, 235))

        self.screen.blit(self.big_font.render("미니게임 기록" if self.view == "RECORDS" else "미니게임", True, (0, 0, 0)), (20, 20))
        difficulty = getattr(self.state, "difficulty", "normal") if self.state else "normal"
        difficulty_label = game_state.get_difficulty_label(difficulty)
        self.screen.blit(self.font.render(f"난이도: {difficulty_label}", True, (70, 70, 70)), (20, 54))

        pygame.draw.rect(self.screen, (220, 220, 220), self.btn_close)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_close, 1)
        close_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(close_text, close_text.get_rect(center=self.btn_close.center))

        pygame.draw.rect(self.screen, (215, 225, 215), self.btn_records)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_records, 1)
        label = self.font.render("게임 선택" if self.view == "RECORDS" else "기록 보기", True, (0, 0, 0))
        self.screen.blit(label, label.get_rect(center=self.btn_records.center))
        if self.view == "RECORDS":
            self.draw_records()
            pygame.display.flip()
            return

        enabled = self.selected in CHALLENGE_GAMES
        pygame.draw.rect(self.screen, (205, 225, 205) if enabled else (215, 215, 215), self.btn_mode)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_mode, 1)
        mode = "도전 모드" if self.challenge else "일반 모드"
        self.screen.blit(self.hint_font.render(mode + " · 클릭해 전환" if enabled else "선택 후 모드 전환", True, (40, 40, 40)), (26, 95))

        used_jump = getattr(self.state, "minigame_used", {}).get("jump", False) if self.state else False
        used_memory = getattr(self.state, "minigame_used", {}).get("memory", False) if self.state else False
        used_footsteps = getattr(self.state, "minigame_used", {}).get("footsteps", False) if self.state else False
        used_laser = getattr(self.state, "minigame_used", {}).get("laser", False) if self.state else False
        self.draw_card(self.card_avoid, "장애물 피하기", self.selected == "jump", used_jump)
        self.draw_card(self.card_memory, "메모리 게임", self.selected == "memory", used_memory)
        self.draw_card(self.card_footsteps, "고양이 따라가기", self.selected == "footsteps", used_footsteps)
        self.draw_card(self.card_laser, "레이저 포인터", self.selected == "laser", used_laser)

        pygame.draw.rect(self.screen, (200, 200, 200), self.btn_start)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_start, 1)
        start_text = self.font.render("시작하기", True, (0, 0, 0))
        self.screen.blit(start_text, start_text.get_rect(center=self.btn_start.center))

        hint = self.hint_font.render("ESC 중단: 보상 없음 / 현재 시간대 시도 소모", True, (90, 70, 70))
        self.screen.blit(hint, hint.get_rect(center=(200, 580)))
        pygame.display.flip()
