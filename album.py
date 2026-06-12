import os
from pathlib import Path

import pygame

from config import asset_path
from pg_utils import load_font
from photo_mode import album_folder, list_photos


BG_COLOR = (245, 245, 245)
PANEL_COLOR = (230, 230, 230)
BORDER = (0, 0, 0)
FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")


class AlbumUI:
    def __init__(self, screen, play_click_sound=None, folder=None):
        self.screen = screen
        self.play_click_sound = play_click_sound
        self.folder = folder or album_folder()
        self.running = True
        self.scroll = 0
        self.selected_index = None

        self.font = load_font(FONT_PATH, 17)
        self.big_font = load_font(FONT_PATH, 22)
        self.small_font = load_font(FONT_PATH, 13)

        self.close_rect = pygame.Rect(360, 10, 30, 30)
        self.back_rect = pygame.Rect(20, 548, 84, 32)
        self.prev_rect = pygame.Rect(112, 548, 80, 32)
        self.next_rect = pygame.Rect(204, 548, 80, 32)
        self.delete_rect = pygame.Rect(296, 548, 84, 32)
        self.photo_rects = []
        self.thumb_cache = {}
        self.full_cache = {}
        self.photos = list_photos(self.folder)
        self.confirm_delete = False
        self.message = ""

        self.list_top = 82
        self.card_w = 152
        self.card_h = 198
        self.card_gap_x = 24
        self.card_gap_y = 14
        self.thumb_size = (126, 150)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.handle_events()
            self.draw()

    def _click(self):
        if self.play_click_sound:
            self.play_click_sound()

    def _max_scroll(self):
        if not self.photos:
            return 0
        _, screen_h = self.screen.get_size()
        rows = (len(self.photos) + 1) // 2
        content_h = rows * (self.card_h + self.card_gap_y)
        view_h = screen_h - self.list_top - 18
        return max(0, int(content_h - view_h))

    def _scroll_by(self, delta):
        self.scroll = max(0, min(int(self.scroll) + int(delta), self._max_scroll()))

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.confirm_delete:
                        self.confirm_delete = False
                        self.message = ""
                    elif self.selected_index is not None:
                        self.selected_index = None
                    else:
                        self.running = False
                elif self.selected_index is not None and event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                    self._request_or_confirm_delete()
                elif self.selected_index is not None and event.key == pygame.K_LEFT:
                    self._select_relative(-1)
                elif self.selected_index is not None and event.key == pygame.K_RIGHT:
                    self._select_relative(1)

            elif event.type == pygame.MOUSEWHEEL:
                if self.selected_index is None:
                    self._scroll_by(-event.y * 42)

            elif event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_mouse_down(event)

    def _handle_mouse_down(self, event):
        if self.close_rect.collidepoint(event.pos):
            self._click()
            self.running = False
            return

        if self.selected_index is not None:
            if self.back_rect.collidepoint(event.pos):
                self._click()
                if self.confirm_delete:
                    self.confirm_delete = False
                    self.message = ""
                else:
                    self.selected_index = None
                return
            if self.delete_rect.collidepoint(event.pos):
                self._click()
                self._request_or_confirm_delete()
                return
            if not self.confirm_delete and self.prev_rect.collidepoint(event.pos):
                self._click()
                self._select_relative(-1)
                return
            if not self.confirm_delete and self.next_rect.collidepoint(event.pos):
                self._click()
                self._select_relative(1)
            return

        if event.button == 4:
            self._scroll_by(-42)
            return
        if event.button == 5:
            self._scroll_by(42)
            return
        if event.button != 1:
            return

        for rect, index in self.photo_rects:
            if rect.collidepoint(event.pos):
                self._click()
                self.selected_index = index
                self.confirm_delete = False
                self.message = ""
                return

    def _selected_path(self):
        if self.selected_index is None or not (0 <= self.selected_index < len(self.photos)):
            return None
        return self.photos[self.selected_index]

    def _select_relative(self, delta):
        if self.selected_index is None or not self.photos:
            return
        next_index = max(0, min(int(self.selected_index) + int(delta), len(self.photos) - 1))
        if next_index != self.selected_index:
            self.selected_index = next_index
            self.confirm_delete = False
            self.message = ""

    def _request_or_confirm_delete(self):
        path = self._selected_path()
        if path is None:
            return
        if not self.confirm_delete:
            self.confirm_delete = True
            self.message = "삭제를 다시 누르면 지워집니다."
            return
        self._delete_selected_photo(path)

    def _delete_selected_photo(self, path):
        try:
            target = Path(path).resolve()
            folder = Path(self.folder).resolve()
            if target.parent != folder:
                self.message = "삭제할 수 없는 위치입니다."
                self.confirm_delete = False
                return
            target.unlink()
        except OSError:
            self.message = "사진 삭제 실패"
            self.confirm_delete = False
            return

        self.thumb_cache.pop(path, None)
        self.full_cache.pop(path, None)
        self.photos = list_photos(self.folder)
        self.selected_index = None
        self.confirm_delete = False
        self.scroll = min(self.scroll, self._max_scroll())
        self.message = "사진 삭제됨"

    def _load_image(self, path):
        try:
            image = pygame.image.load(path).convert_alpha()
            return image
        except (OSError, TypeError, ValueError, pygame.error):
            return None

    def _fit_image(self, image, max_size):
        width, height = image.get_size()
        if width <= 0 or height <= 0:
            return None
        scale = min(max_size[0] / width, max_size[1] / height, 1.0)
        size = (max(1, int(width * scale)), max(1, int(height * scale)))
        return pygame.transform.smoothscale(image, size)

    def _thumbnail(self, path):
        cached = self.thumb_cache.get(path)
        if cached is not None:
            return cached
        image = self._load_image(path)
        if image is None:
            self.thumb_cache[path] = None
            return None
        thumb = self._fit_image(image, self.thumb_size)
        self.thumb_cache[path] = thumb
        return thumb

    def _full_image(self, path):
        cached = self.full_cache.get(path)
        if cached is not None:
            return cached
        image = self._load_image(path)
        if image is None:
            self.full_cache[path] = None
            return None
        full = self._fit_image(image, (356, 436))
        self.full_cache[path] = full
        return full

    def _short_name(self, name, limit):
        text = str(name)
        if len(text) <= limit:
            return text
        return "..." + text[-max(1, limit - 3):]

    def draw_top(self):
        title = self.big_font.render("앨범", True, (0, 0, 0))
        self.screen.blit(title, (20, 20))

        count = self.font.render(f"사진 {len(self.photos)}장", True, (70, 70, 70))
        self.screen.blit(count, (20, 52))
        if self.message and self.selected_index is None:
            msg = self.small_font.render(self.message, True, (150, 55, 55))
            self.screen.blit(msg, (132, 56))

        pygame.draw.rect(self.screen, PANEL_COLOR, self.close_rect)
        pygame.draw.rect(self.screen, BORDER, self.close_rect, 1)
        x_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))

    def draw_button(self, rect, text, *, enabled=True, danger=False):
        if enabled:
            color = (238, 214, 214) if danger else PANEL_COLOR
            text_color = (120, 35, 35) if danger else (0, 0, 0)
        else:
            color = (215, 215, 215)
            text_color = (130, 130, 130)
        pygame.draw.rect(self.screen, color, rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)
        label = self.font.render(text, True, text_color)
        self.screen.blit(label, label.get_rect(center=rect.center))

    def draw_empty(self):
        msg = self.font.render("아직 저장된 사진이 없습니다.", True, (70, 70, 70))
        hint = self.small_font.render("F12 또는 일시정지 메뉴에서 사진을 찍어보세요.", True, (100, 100, 100))
        self.screen.blit(msg, msg.get_rect(center=(200, 260)))
        self.screen.blit(hint, hint.get_rect(center=(200, 292)))

    def draw_grid(self):
        if not self.photos:
            self.draw_empty()
            return

        self.photo_rects.clear()
        screen_w, screen_h = self.screen.get_size()
        list_rect = pygame.Rect(0, self.list_top, screen_w, screen_h - self.list_top)
        old_clip = self.screen.get_clip()
        self.screen.set_clip(list_rect)

        left = (screen_w - (self.card_w * 2 + self.card_gap_x)) // 2
        y0 = self.list_top - int(self.scroll)

        for index, path in enumerate(self.photos):
            col = index % 2
            row = index // 2
            x = left + col * (self.card_w + self.card_gap_x)
            y = y0 + row * (self.card_h + self.card_gap_y)
            rect = pygame.Rect(x, y, self.card_w, self.card_h)

            if rect.bottom < self.list_top - self.card_h:
                continue
            if rect.top > screen_h:
                break

            pygame.draw.rect(self.screen, (252, 252, 252), rect)
            pygame.draw.rect(self.screen, BORDER, rect, 1)

            thumb_rect = pygame.Rect(rect.x + 13, rect.y + 10, *self.thumb_size)
            pygame.draw.rect(self.screen, (225, 225, 225), thumb_rect)
            thumb = self._thumbnail(path)
            if thumb is not None:
                self.screen.blit(thumb, thumb.get_rect(center=thumb_rect.center))
            else:
                err = self.small_font.render("불러오기 실패", True, (120, 60, 60))
                self.screen.blit(err, err.get_rect(center=thumb_rect.center))

            name = self._short_name(Path(path).stem, 18)
            label = self.small_font.render(name, True, (45, 45, 45))
            self.screen.blit(label, (rect.x + 10, rect.y + self.thumb_size[1] + 18))

            self.photo_rects.append((rect, index))

        self.screen.set_clip(old_clip)

    def draw_selected(self):
        if self.selected_index is None or not (0 <= self.selected_index < len(self.photos)):
            self.selected_index = None
            return

        path = self.photos[self.selected_index]
        image = self._full_image(path)

        area = pygame.Rect(20, 78, 360, 440)
        pygame.draw.rect(self.screen, (225, 225, 225), area)
        pygame.draw.rect(self.screen, BORDER, area, 1)

        if image is not None:
            self.screen.blit(image, image.get_rect(center=area.center))
        else:
            err = self.font.render("사진을 불러올 수 없습니다.", True, (120, 60, 60))
            self.screen.blit(err, err.get_rect(center=area.center))

        filename = os.path.basename(path)
        label_text = self.message if self.confirm_delete else self._short_name(filename, 42)
        label_color = (150, 55, 55) if self.confirm_delete else (45, 45, 45)
        label = self.small_font.render(label_text, True, label_color)
        self.screen.blit(label, (20, 526))

        self.draw_button(self.back_rect, "취소" if self.confirm_delete else "목록")
        if self.confirm_delete:
            self.draw_button(self.delete_rect, "삭제", danger=True)
        else:
            self.draw_button(self.prev_rect, "이전", enabled=self.selected_index > 0)
            self.draw_button(self.next_rect, "다음", enabled=self.selected_index < len(self.photos) - 1)
            self.draw_button(self.delete_rect, "삭제", danger=True)

    def draw(self):
        self.screen.fill(BG_COLOR)
        self.draw_top()
        if self.selected_index is None:
            self.draw_grid()
        else:
            self.draw_selected()
        pygame.display.flip()
