import random

import pygame

import state as game_state
from config import asset_path
from pg_utils import load_font, screen_events


class TimingGame:
    def __init__(self, screen, state=None, challenge=False):
        self.screen = screen
        self.difficulty = game_state.normalize_difficulty(getattr(state, "difficulty", None))
        self.balance = game_state.get_minigame_profile(self.difficulty, "timing")
        self.challenge = bool(challenge)
        self.clock = pygame.time.Clock()
        self.font = load_font(asset_path("fonts", "ThinDungGeunMo.ttf"), 18)
        self.big_font = load_font(asset_path("fonts", "ThinDungGeunMo.ttf"), 24)
        self.small_font = load_font(asset_path("fonts", "ThinDungGeunMo.ttf"), 14)
        self.gauge = pygame.Rect(40, 260, 320, 40)
        self.round_limit = 6 if self.challenge else 5
        self.speed = self.balance["speed"] * (1.15 if self.challenge else 1)
        self.band_width = self.balance["width"] * (0.8 if self.challenge else 1)
        self.target_score = self.balance["challenge_score"] if self.challenge else self.balance["target_score"]
        self.round_index = 1
        self.score = self.hits = self.misses = self.perfects = 0
        self.combo = self.best_combo = 0
        self.won = False
        self.phase = "PLAY"
        self.feedback = ""
        self.feedback_left = 0.0
        self._new_round()

    def _new_round(self):
        self.phase = "PLAY"
        self.travel = 0.0
        self.position = 0.0
        self.center = random.uniform(0.30, 0.70)
        self.time_left = float(self.balance["round_seconds"])

    def judge(self, timed_out=False):
        if self.phase != "PLAY":
            return
        distance = abs(self.position - self.center)
        hit = not timed_out and distance <= self.band_width / 2
        perfect = hit and distance <= self.band_width / 6
        if hit:
            self.hits += 1
            self.perfects += int(perfect)
            self.combo += 1
            self.best_combo = max(self.best_combo, self.combo)
            gained = 30 if perfect else 20
            self.score += gained
            self.feedback = f"{'완벽!' if perfect else '성공!'} +{gained}점"
        else:
            self.misses += 1
            self.combo = 0
            self.feedback = "시간 초과" if timed_out else "아쉬워요! 다음 판정에 집중하세요."
        self.phase = "FEEDBACK"
        self.feedback_left = 0.6

    def update(self, dt):
        if self.phase == "PLAY":
            self.travel += max(0, dt) * self.speed
            offset = self.travel % 2
            self.position = offset if offset <= 1 else 2 - offset
            self.time_left = max(0.0, self.time_left - dt)
            if self.time_left <= 0:
                self.judge(timed_out=True)
        elif self.phase == "FEEDBACK":
            self.feedback_left -= dt
            if self.feedback_left <= 0:
                if self.round_index >= self.round_limit:
                    self.phase = "RESULT"
                    self.won = self.score >= self.target_score
                else:
                    self.round_index += 1
                    self._new_round()

    def get_result(self, *, cancelled=False, quit_requested=False):
        complete = self.phase == "RESULT" and not cancelled
        won = complete and self.won
        coins = 4 + self.hits * 2 + self.perfects + (10 if won else 0) + (5 if won and self.challenge else 0)
        return {"won": won, "coins": min(40, coins) if complete else 0, "score": self.score,
                "hits": self.hits, "misses": self.misses, "perfects": self.perfects,
                "best_combo": self.best_combo, "accuracy": self.hits * 100 // (self.hits + self.misses) if self.hits + self.misses else 0,
                "rounds": self.hits + self.misses, "mode": "challenge" if self.challenge else "normal",
                "challenge_won": self.challenge and won, "cancelled": not complete, "quit_requested": quit_requested}

    def draw(self):
        self.screen.fill((245, 245, 245))
        title = self.big_font.render("타이밍 도전" if self.challenge else "타이밍 놀이", True, (30, 30, 30))
        self.screen.blit(title, title.get_rect(center=(200, 40)))
        lines = (f"난이도 {game_state.get_difficulty_label(self.difficulty)} / {self.round_index}/{self.round_limit}회",
                 f"점수 {self.score}/{self.target_score} / 최고 콤보 {self.best_combo}",
                 "움직이는 선이 초록 영역에 왔을 때 누르세요.", "Space 또는 마우스 클릭 / ESC 중단")
        for index, line in enumerate(lines):
            self.screen.blit(self.small_font.render(line, True, (65, 65, 65)), (25, 84 + index * 26))
        pygame.draw.rect(self.screen, (215, 215, 215), self.gauge, border_radius=6)
        band = pygame.Rect(round(self.gauge.x + (self.center - self.band_width / 2) * self.gauge.width), self.gauge.y, round(self.band_width * self.gauge.width), self.gauge.height)
        pygame.draw.rect(self.screen, (115, 195, 130), band)
        perfect = pygame.Rect(round(self.gauge.x + (self.center - self.band_width / 6) * self.gauge.width), self.gauge.y, max(1, round(self.band_width * self.gauge.width / 3)), self.gauge.height)
        pygame.draw.rect(self.screen, (235, 195, 95), perfect)
        pygame.draw.rect(self.screen, (60, 60, 60), self.gauge, 2, border_radius=6)
        x = round(self.gauge.x + self.position * self.gauge.width)
        pygame.draw.line(self.screen, (70, 75, 165), (x, self.gauge.y - 10), (x, self.gauge.bottom + 10), 4)
        text = f"남은 판정 시간 {self.time_left:.1f}초" if self.phase == "PLAY" else self.feedback
        label = self.font.render(text, True, (60, 60, 60))
        self.screen.blit(label, label.get_rect(center=(200, 360)))
        if self.phase == "RESULT":
            panel = pygame.Rect(25, 400, 350, 160)
            pygame.draw.rect(self.screen, (220, 235, 220), panel, border_radius=10)
            result = self.get_result()
            coins = game_state.scale_coin(result["coins"], self.difficulty)
            lines = ("성공!" if self.won else "다음에는 더 잘할 수 있어요!",
                     f"일반 보상 +{coins}코인 / 정확도 {result['accuracy']}%",
                     "Enter 또는 ESC로 돌아가기")
            for index, line in enumerate(lines):
                label = self.font.render(line, True, (35, 35, 35))
                self.screen.blit(label, label.get_rect(center=(200, 433 + index * 42)))
        pygame.display.flip()

    def run(self):
        while True:
            dt = self.clock.tick(60) / 1000
            for event in screen_events():
                if event.type == pygame.QUIT:
                    return self.get_result(cancelled=self.phase != "RESULT", quit_requested=True)
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return self.get_result(cancelled=self.phase != "RESULT")
                if self.phase == "RESULT":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        return self.get_result()
                elif ((event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE)
                      or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1)):
                    self.judge()
            self.update(dt)
            self.draw()
