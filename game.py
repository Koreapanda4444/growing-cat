import pygame
import sys
import state as game_state
from minigames.memory_game import MemoryGame
from minigames.cat_run import CatRunGame
from minigames.cat_follow import CatFollowGame
from minigames.laser_chase import run_laser_chase

from config import asset_path
from pg_utils import load_font

FPS = 60    

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")


class MiniGameScreen:
    def __init__(self, screen, state=None, ach=None):
        self.screen = screen
        self.state = state
        self.ach = ach
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = load_font(FONT_PATH, 18)
        self.big_font = load_font(FONT_PATH, 22)

        self.selected = None

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
            self.draw()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(event.pos)

    def handle_click(self, pos):
        if self.btn_close.collidepoint(pos):
            self.running = False
            return

        if self.card_avoid.collidepoint(pos):
            self.selected = "jump"
            return
        if self.card_memory.collidepoint(pos):
            self.selected = "memory"
            return
        if self.card_footsteps.collidepoint(pos):
            self.selected = "footsteps"
            return
        if self.card_laser.collidepoint(pos):
            self.selected = "laser"
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

        if self.ach:
            self.ach.on_event("minigame_played")

        result = self._run_minigame(self.selected)
        self._apply_minigame_result(
            result,
            win_on_positive_coins=self.selected == "jump",
        )
        self.state.minigame_used[self.selected] = True
        self.running = False

    def _ensure_minigame_usage(self):
        self.state.minigame_used = game_state.normalize_minigame_usage(
            getattr(self.state, "minigame_used", None)
        )

    def _run_minigame(self, minigame_id):
        if minigame_id == "jump":
            return CatRunGame(self.screen, self.state).run()
        if minigame_id == "memory":
            return MemoryGame(self.screen, self.state).run()
        if minigame_id == "footsteps":
            return CatFollowGame(self.screen, self.state).run()
        if minigame_id == "laser":
            difficulty = getattr(self.state, "difficulty", "normal")
            return run_laser_chase(self.screen, difficulty=difficulty)
        return None

    def _apply_minigame_result(self, result, *, win_on_positive_coins=False):
        if not isinstance(result, dict):
            return

        coins = self._scaled_result_coins(result)
        if coins > 0:
            self._add_coins(coins)
            if self.ach:
                self.ach.on_event("coins_earned", amount=coins)

        won = bool(result.get("won")) or (win_on_positive_coins and coins > 0)
        if self.ach and won:
            self.ach.on_event("minigame_won")

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

    def draw(self):
        self.screen.fill((235, 235, 235))

        self.screen.blit(self.big_font.render("미니게임", True, (0, 0, 0)), (20, 20))
        difficulty = getattr(self.state, "difficulty", "normal") if self.state else "normal"
        difficulty_label = game_state.get_difficulty_label(difficulty)
        self.screen.blit(self.font.render(f"난이도: {difficulty_label}", True, (70, 70, 70)), (20, 54))

        pygame.draw.rect(self.screen, (220, 220, 220), self.btn_close)
        pygame.draw.rect(self.screen, (0, 0, 0), self.btn_close, 1)
        close_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(close_text, close_text.get_rect(center=self.btn_close.center))

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

        pygame.display.flip()
