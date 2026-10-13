import pygame
import random

from config import asset_path
from pg_utils import screen_events, load_font, cached_image as load_image, solid_surface
import state as game_state

WIDTH = 400
HEIGHT = 600

GRID_COLS = 4
GRID_ROWS = 4
FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")
MISMATCH_EVENT = pygame.USEREVENT + 1

class MemoryGame:
    def __init__(self, screen, state, challenge=False):
        self.screen = screen
        self.state = state
        self.difficulty = game_state.normalize_difficulty(getattr(state, "difficulty", None))
        self.balance = game_state.get_minigame_profile(self.difficulty, "memory")
        self.challenge = bool(challenge)
        self.stage = 1
        self.target_stages = (2 if self.difficulty == "easy" else 3) if self.challenge else 1
        self.total_pairs = 0
        self.total_elapsed_ms = 0
        self.completed_stages = 0
        self.order_index = 0
        self.required_order = []
        self.stage_fail_start = 0
        self.shuffle_reveal_until = None
        self.error_limit = {"easy": 6, "normal": 4, "hard": 3}[self.difficulty]
        self.clock = pygame.time.Clock()
        self.running = True
        self.cancelled = False
        self.quit_requested = False

        self.font = load_font(FONT_PATH, 22)
        self.small_font = load_font(FONT_PATH, 16)
        self.card_label_font = load_font(FONT_PATH, 12)

        self.cards = []
        self.first = None
        self.second = None
        self.lock = False
        self.fail_count = 0

        self.board_margin_x = 20
        self.board_top = 140
        self.board_bottom = HEIGHT - 60
        self.card_gap = 12
        avail_w = WIDTH - 2 * self.board_margin_x
        avail_h = self.board_bottom - self.board_top
        card_w = (avail_w - (GRID_COLS - 1) * self.card_gap) / GRID_COLS
        card_h = (avail_h - (GRID_ROWS - 1) * self.card_gap) / GRID_ROWS
        self.card_size = int(min(card_w, card_h))
        used_w = GRID_COLS * self.card_size + (GRID_COLS - 1) * self.card_gap
        used_h = GRID_ROWS * self.card_size + (GRID_ROWS - 1) * self.card_gap
        self.board_x = (WIDTH - used_w) // 2
        self.board_y = self.board_top + (avail_h - used_h) // 2
        self.started = False
        self.reveal_end_ms = None
        self.limit_start_ms = None
        self.preview_ms = int(self.balance["preview_ms"])
        self.base_preview_ms = self.preview_ms
        self.time_limit_ms = int(self.balance["time_limit_ms"])
        self.mismatch_ms = int(self.balance["mismatch_ms"])
        self.reward_base = int(self.balance["reward_base"])
        self.fail_penalty = int(self.balance["fail_penalty"])

        self.won = False
        self.reward_coins = 0

        self.back_image = load_image(
            asset_path("minigames", "memory_game", "memoryback.png"),
            size=(self.card_size, self.card_size),
            smooth=True,
            alpha=True,
        ) or solid_surface((self.card_size, self.card_size), (180, 180, 180))

        self.load_cards()

    def load_cards(self):
        all_ids = list(range(1, 17))
        chosen = random.sample(all_ids, 8)
        self.required_order = sorted(chosen)
        self.order_index = 0

        colors = [
            (255, 100, 100), (100, 255, 100), (100, 100, 255), (255, 255, 100),
            (255, 100, 255), (100, 255, 255), (255, 150, 100), (150, 100, 255)
        ]

        images = {}
        for idx, cid in enumerate(chosen):
            images[cid] = load_image(
                asset_path("minigames", "memory_game", f"memory{cid}.png"),
                size=(self.card_size, self.card_size),
                smooth=True,
                alpha=True,
            ) or solid_surface((self.card_size, self.card_size), colors[idx % len(colors)])

        ids = chosen * 2
        random.shuffle(ids)

        self.cards.clear()
        for i, cid in enumerate(ids):
            x = self.board_x + (i % GRID_COLS) * (self.card_size + self.card_gap)
            y = self.board_y + (i // GRID_COLS) * (self.card_size + self.card_gap)

            self.cards.append({
                "id": cid,
                "image": images[cid],
                "rect": pygame.Rect(x, y, self.card_size, self.card_size),
                "revealed": True,
                "matched": False
            })

        now = pygame.time.get_ticks()
        self.reveal_end_ms = now + self.preview_ms

    def handle_click(self, pos):
        if self.lock or not self.started:
            return

        for card in self.cards:
            if (
                card["rect"].collidepoint(pos)
                and not card["revealed"]
                and not card["matched"]
            ):
                card["revealed"] = True

                if not self.first:
                    self.first = card
                elif not self.second:
                    self.second = card
                    self.check_match()
                break

    def check_match(self):
        ordered = (not self.challenge or self.stage == 1
                   or self.first["id"] == self.required_order[self.order_index])
        if self.first["id"] == self.second["id"] and ordered:
            self.first["matched"] = True
            self.second["matched"] = True
            self.first = None
            self.second = None
            self.order_index += 1
            if self.challenge and self.stage >= 3 and self.order_index % 2 == 0:
                hidden = [card for card in self.cards if not card["matched"]]
                rects = [card["rect"].copy() for card in hidden]
                random.shuffle(rects)
                for card, rect in zip(hidden, rects):
                    card["rect"] = rect
                    card["revealed"] = True
                if hidden:
                    self.shuffle_reveal_until = pygame.time.get_ticks() + max(650, round(self.base_preview_ms * 0.4))
                    self.lock = True
        else:
            self.lock = True
            self.fail_count += 1
            self._set_mismatch_timer(getattr(self, "mismatch_ms", 700))

    def _set_mismatch_timer(self, milliseconds: int):
        try:
            pygame.time.set_timer(MISMATCH_EVENT, milliseconds)
        except pygame.error:
            pass

    def handle_mismatch_timeout(self):
        if self.first is not None and self.second is not None:
            self.first["revealed"] = False
            self.second["revealed"] = False
        self.first = None
        self.second = None
        self.lock = False
        self._set_mismatch_timer(0)

    def update(self):
        now = pygame.time.get_ticks()
        if self.shuffle_reveal_until is not None and now >= self.shuffle_reveal_until:
            for card in self.cards:
                if not card["matched"]:
                    card["revealed"] = False
            self.shuffle_reveal_until = None
            self.lock = False
        if not self.started and self.reveal_end_ms and now >= self.reveal_end_ms:
            for c in self.cards:
                if not c["matched"]:
                    c["revealed"] = False
            self.started = True
            self.limit_start_ms = now

        if self.challenge and self.fail_count - self.stage_fail_start > self.error_limit:
            self.running = False
            return
        if all(c["matched"] for c in self.cards):
            self.total_pairs += len(self.cards) // 2
            self.completed_stages += 1
            self.total_elapsed_ms += max(0, now - self.limit_start_ms) if self.limit_start_ms is not None else 0
            if self.stage < self.target_stages:
                self.stage += 1
                self.stage_fail_start = self.fail_count
                self.preview_ms = max(600, round(self.base_preview_ms * (0.9 ** (self.stage - 1))))
                self.started = False
                self.limit_start_ms = None
                self.first = self.second = None
                self.shuffle_reveal_until = None
                self.lock = False
                self._set_mismatch_timer(0)
                pygame.event.clear(MISMATCH_EVENT)
                self.load_cards()
                return
            reward = max(10, self.reward_base + (10 if self.challenge else 0) - self.fail_penalty * self.fail_count)
            self.won = True
            self.reward_coins = reward
            self.running = False
            return

        if self.started and self.limit_start_ms and now - self.limit_start_ms > self.time_limit_ms:
            self.running = False

    def draw(self):
        self.screen.fill((245, 245, 245))

        title = self.font.render(f"메모리 도전 {self.stage}/{self.target_stages}" if self.challenge else "메모리 게임", True, (0, 0, 0))
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        info = self.small_font.render(
            f"실수 횟수: {self.fail_count}", True, (80, 80, 80)
        )
        self.screen.blit(info, (20, 60))

        if self.started and self.limit_start_ms:
            now = pygame.time.get_ticks()
            remain_ms = max(0, self.time_limit_ms - (now - self.limit_start_ms))
            remain_s = round(remain_ms / 1000, 1)
            t = self.small_font.render(f"남은 시간: {remain_s}초", True, (120, 80, 80))
            self.screen.blit(t, (WIDTH - t.get_width() - 20, 60))

        if self.challenge:
            target = self.required_order[self.order_index] if self.order_index < len(self.required_order) else "완료"
            rule = "자유 매칭" if self.stage == 1 else f"작은 번호 순서 · 다음 {target}"
            self.screen.blit(self.small_font.render(f"{rule} / 단계 실수 한도 {self.error_limit}", True, (90, 70, 70)), (20, 88))
            if self.stage >= 3:
                self.screen.blit(self.small_font.render("재배치된 카드는 잠깐 다시 보여줍니다.", True, (90, 70, 70)), (20, 110))
        for card in self.cards:
            if card["revealed"] or card["matched"]:
                self.screen.blit(card["image"], (card["rect"].x, card["rect"].y))
                if self.challenge:
                    badge = pygame.Rect(card["rect"].x + 2, card["rect"].y + 2, 20, 16)
                    pygame.draw.rect(self.screen, (250, 250, 250), badge)
                    label = self.card_label_font.render(str(card["id"]), True, (0, 0, 0))
                    self.screen.blit(label, label.get_rect(center=badge.center))
            else:
                self.screen.blit(self.back_image, (card["rect"].x, card["rect"].y))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.clock.tick(60)

            for event in screen_events():
                if event.type == pygame.QUIT:
                    self.quit_requested = True
                    self.cancelled = True
                    self.running = False
                    break

                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.cancelled = True
                    self.running = False
                    break

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)

                elif event.type == MISMATCH_EVENT:
                    self.handle_mismatch_timeout()

            if self.running:
                self.update()
                self.draw()

        self._set_mismatch_timer(0)
        pygame.event.clear(MISMATCH_EVENT)
        return self.get_result()

    def get_result(self):
        pairs = self.total_pairs + (0 if self.won else sum(card["matched"] for card in self.cards) // 2)
        elapsed = self.total_elapsed_ms
        if not self.won and self.limit_start_ms is not None:
            elapsed += max(0, pygame.time.get_ticks() - self.limit_start_ms)
        return {"pairs": pairs, "errors": self.fail_count, "score": max(0, pairs * 100 - self.fail_count * 10),
                "elapsed_ms": elapsed, "stages": self.completed_stages,
                "mode": "challenge" if self.challenge else "normal",
                "challenge_won": self.challenge and self.won and not self.cancelled,
                "won": bool(self.won) and not self.cancelled,
                "coins": 0 if self.cancelled else int(self.reward_coins),
                "cancelled": self.cancelled, "quit_requested": self.quit_requested}
