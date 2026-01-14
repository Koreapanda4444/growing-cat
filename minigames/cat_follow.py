import os
import random
import pygame

from config import asset_path
from pg_utils import load_font, load_image, solid_surface

FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")
ASSET_DIR = asset_path("minigames", "cat_follow")


class CatFollowGame:
    def __init__(self, screen: pygame.Surface, state=None, ach=None):
        self.screen = screen
        self.state = state
        self.ach = ach
        self.clock = pygame.time.Clock()
        self.running = True

        self.font = load_font(FONT_PATH, 22)
        self.font_big = load_font(FONT_PATH, 38)

        self.grid = 5
        self.start_len = 5
        self.target_round = 3
        self.show_on_s = 0.5
        self.show_off_s = 0.15
        self.max_fails = 1

        self.cats_correct = 0
        self.rounds_cleared = 0
        self.round_idx = 1
        self.seq_len = self.start_len
        self.fails = 0

        self.phase = "SHOW"
        self.show_timer = 0.0
        self.show_step = 0
        self.show_on = True

        self.sequence = []
        self.input_index = 0

        self.last_click = None
        self.last_click_timer = 0.0

        self.won = False
        self._result_once = False

        self._cat_src = self._load_cat_source()
        self._scaled_tile = None
        self._cat_tile = None

        self.sequence = self._new_sequence(self.seq_len)

    def _load_cat_source(self) -> pygame.Surface:
        primary = os.path.join(ASSET_DIR, "cat.png")
        fallback_footsteps = asset_path("minigames", "footsteps", "cat.png")
        fallback_cat_run = asset_path("minigames", "cat_run", "cat.png")
        img = load_image(primary, alpha=True)
        if img is None:
            img = load_image(fallback_footsteps, alpha=True)
        if img is None:
            img = load_image(fallback_cat_run, alpha=True)
        if img is None:
            img = solid_surface((64, 64), (255, 210, 120), alpha=True)
        return img

    def _new_sequence(self, length: int):
        g = self.grid
        return [(random.randrange(g), random.randrange(g)) for _ in range(length)]

    def _coins_from(self, cats_correct: int, rounds_cleared: int):
        cats_correct = max(0, int(cats_correct))
        rounds_cleared = max(0, int(rounds_cleared))
        return cats_correct * 2 + rounds_cleared * 10

    def _build_layout(self):
        w, h = self.screen.get_size()
        ui_offset_y = int(h * 0.06)

        grid_top = int(h * 0.20) + ui_offset_y
        grid_bottom_reserved = int(h * 0.16)
        side_margin = int(w * 0.06)

        max_grid_w = max(1, w - side_margin * 2)
        max_grid_h = max(1, h - grid_top - grid_bottom_reserved)
        tile = max(10, min(max_grid_w // self.grid, max_grid_h // self.grid))

        gx = (w - tile * self.grid) // 2
        gy = grid_top
        return w, h, tile, gx, gy, ui_offset_y

    def _cell_at_pos(self, pos, tile, gx, gy):
        x, y = pos
        g = self.grid
        if not (gx <= x < gx + tile * g and gy <= y < gy + tile * g):
            return None
        cx = (x - gx) // tile
        cy = (y - gy) // tile
        return int(cy), int(cx)

    def _ensure_scaled_cat(self, tile: int):
        if self._scaled_tile == tile and self._cat_tile is not None:
            return
        pad = max(2, int(tile * 0.12))
        side = max(4, tile - pad * 2)
        self._cat_tile = pygame.transform.smoothscale(self._cat_src, (side, side))
        self._scaled_tile = tile

    def _finish(self, won: bool):
        self.phase = "RESULT"
        self.won = bool(won)

    def run(self):
        if self.ach:
            self.ach.on_event("minigame_played")

        while self.running:
            dt = self.clock.tick(60) / 1000.0
            w, h, tile, gx, gy, ui_offset_y = self._build_layout()
            self._ensure_scaled_cat(tile)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self._finish(False)
                    self.running = False
                    break

                if self.phase == "RESULT":
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.running = False
                    continue

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self._finish(False)
                    continue

                if self.phase == "INPUT":
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        cell = self._cell_at_pos(event.pos, tile, gx, gy)
                        if cell is None:
                            continue

                        self.last_click = cell
                        self.last_click_timer = 0.12

                        if cell == self.sequence[self.input_index]:
                            self.cats_correct += 1
                            self.input_index += 1

                            if self.input_index >= len(self.sequence):
                                self.rounds_cleared += 1
                                self.round_idx += 1

                                if self.round_idx > self.target_round:
                                    self._finish(True)
                                else:
                                    self.sequence = self._new_sequence(self.seq_len)
                                    self.input_index = 0
                                    self.phase = "SHOW"
                                    self.show_timer = 0.0
                                    self.show_step = 0
                                    self.show_on = True
                        else:
                            self.fails += 1
                            if self.fails >= self.max_fails:
                                self._finish(False)
                            else:
                                self.phase = "SHOW"
                                self.show_timer = 0.0
                                self.show_step = 0
                                self.show_on = True
                                self.input_index = 0

            if self.last_click_timer > 0:
                self.last_click_timer -= dt
                if self.last_click_timer <= 0:
                    self.last_click = None

            if self.phase == "SHOW":
                self.show_timer += dt
                dur = self.show_on_s if self.show_on else self.show_off_s
                if self.show_timer >= dur:
                    self.show_timer = 0.0
                    if self.show_on:
                        self.show_on = False
                    else:
                        self.show_on = True
                        self.show_step += 1

                if self.show_step >= len(self.sequence):
                    self.phase = "INPUT"
                    self.input_index = 0

            if self.phase == "RESULT" and not self._result_once:
                if self.won and self.ach:
                    self.ach.on_event("minigame_won")
                self._result_once = True

            self.screen.fill((18, 18, 22))

            title = self.font_big.render("고양이 따라가기", True, (255, 255, 255))
            self.screen.blit(title, title.get_rect(center=(w // 2, int(h * 0.09) + ui_offset_y)))

            hud = self.font.render(
                f"ROUND {min(self.round_idx, self.target_round)}/{self.target_round}",
                True,
                (235, 235, 235),
            )
            self.screen.blit(hud, hud.get_rect(center=(w // 2, int(h * 0.14) + ui_offset_y)))

            gap = 1
            border_radius = max(6, tile // 6)

            for r in range(self.grid):
                for c in range(self.grid):
                    rect = pygame.Rect(gx + c * tile, gy + r * tile, tile - gap, tile - gap)
                    pygame.draw.rect(self.screen, (70, 70, 80), rect, border_radius=border_radius)

                    if self.phase == "SHOW" and self.show_on and self.show_step < len(self.sequence):
                        sr, sc = self.sequence[self.show_step]
                        if (r, c) == (sr, sc):
                            pygame.draw.rect(self.screen, (230, 230, 100), rect, border_radius=border_radius)
                            cx = rect.centerx - self._cat_tile.get_width() // 2
                            cy = rect.centery - self._cat_tile.get_height() // 2
                            self.screen.blit(self._cat_tile, (cx, cy))

                    if self.last_click == (r, c) and self._cat_tile is not None:
                        cx = rect.centerx - self._cat_tile.get_width() // 2
                        cy = rect.centery - self._cat_tile.get_height() // 2
                        self.screen.blit(self._cat_tile, (cx, cy))
                        pygame.draw.rect(self.screen, (120, 220, 140), rect, width=3, border_radius=border_radius)

                    pygame.draw.rect(self.screen, (0, 0, 0), rect, width=2, border_radius=border_radius)

            if self.phase == "INPUT":
                prog = self.font.render(f"입력: {self.input_index}/{len(self.sequence)}", True, (255, 255, 255))
                self.screen.blit(prog, prog.get_rect(center=(w // 2, min(int(h * 0.92), h - 24))))
            elif self.phase == "SHOW":
                prog = self.font.render("기억하세요...", True, (255, 255, 255))
                self.screen.blit(prog, prog.get_rect(center=(w // 2, min(int(h * 0.92), h - 24))))

            if self.phase == "RESULT":
                overlay = pygame.Surface((w, h), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                self.screen.blit(overlay, (0, 0))

                msg = "성공!" if self.won else "실패!"
                m = self.font_big.render(msg, True, (255, 255, 255))
                self.screen.blit(m, m.get_rect(center=(w // 2, int(h * 0.45))))

                coins = self._coins_from(self.cats_correct, self.rounds_cleared)
                sub = self.font.render(f"COINS +{coins}", True, (230, 230, 230))
                self.screen.blit(sub, sub.get_rect(center=(w // 2, int(h * 0.56))))

                hint = self.font.render("ENTER를 누르면 돌아갑니다", True, (210, 210, 210))
                self.screen.blit(hint, hint.get_rect(center=(w // 2, int(h * 0.66))))

            pygame.display.flip()

        coins = self._coins_from(self.cats_correct, self.rounds_cleared)
        return {"won": bool(self.won), "score": 0, "coins": int(coins)}
