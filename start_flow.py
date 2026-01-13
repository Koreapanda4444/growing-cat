import os
import pygame


def get_korean_font(size: int) -> pygame.font.Font:
    for name in ("malgungothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"):
        f = pygame.font.SysFont(name, size)
        if f:
            return f
    return pygame.font.SysFont(None, size)


class Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font, enabled: bool = True):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.enabled = enabled
        self.hover = False

    def handle_event(self, event: pygame.event.Event) -> bool:
        if not self.enabled:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

    def draw(self, screen: pygame.Surface):
        if not self.enabled:
            bg = (90, 90, 90)
            fg = (170, 170, 170)
        else:
            bg = (40, 140, 70) if self.hover else (30, 110, 55)
            fg = (255, 255, 255)

        pygame.draw.rect(screen, bg, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, width=2, border_radius=10)

        t = self.font.render(self.text, True, fg)
        screen.blit(t, t.get_rect(center=self.rect.center))


class TextInput:
    def __init__(self, rect: pygame.Rect, font: pygame.font.Font, max_len: int = 12):
        self.rect = pygame.Rect(rect)
        self.font = font
        self.max_len = max_len
        self.text = ""
        self.active = True
        self.cursor_timer = 0.0
        self.cursor_show = True

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)

        if not self.active:
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            return

        if event.type == pygame.TEXTINPUT:
            for ch in event.text:
                if len(self.text) >= self.max_len:
                    break
                if ch.isprintable():
                    self.text += ch

    def update(self, dt: float):
        self.cursor_timer += dt
        if self.cursor_timer >= 0.5:
            self.cursor_timer = 0.0
            self.cursor_show = not self.cursor_show

    def draw(self, screen: pygame.Surface):
        bg = (255, 255, 255) if self.active else (200, 200, 200)
        pygame.draw.rect(screen, bg, self.rect, border_radius=8)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, width=2, border_radius=8)

        show_text = self.text
        if self.active and self.cursor_show:
            show_text += "|"

        t = self.font.render(show_text, True, (0, 0, 0))
        screen.blit(t, (self.rect.x + 10, self.rect.y + (self.rect.h - t.get_height()) // 2))


class StartFlow:
    def __init__(self, screen: pygame.Surface, assets_root: str = "assets"):
        self.screen = screen
        self.assets_root = assets_root

        self.mode = "START"
        self.done = False
        self.result = None

        self.font_title = get_korean_font(34)
        self.font_name_title = get_korean_font(24)
        self.font_btn = get_korean_font(22)
        self.font_small = get_korean_font(16)

        self._load_assets()
        self._rebuild_layout()
        self.name_input: TextInput | None = None

    def _load_assets(self):
        path = os.path.join(self.assets_root, "ui", "start.png")
        self.start_bg = pygame.image.load(path).convert_alpha()

        bg_path = os.path.join(self.assets_root, "ui", "background.png")
        self.name_bg = pygame.image.load(bg_path).convert_alpha()

    def _rebuild_layout(self):
        W, H = self.screen.get_size()

        bg = self.start_bg
        bw, bh = bg.get_size()
        scale = max(W / bw, H / bh)
        new_size = (max(1, int(bw * scale)), max(1, int(bh * scale)))
        self.start_bg_scaled = pygame.transform.smoothscale(bg, new_size)
        self.start_bg_pos = ((W - new_size[0]) // 2, (H - new_size[1]) // 2)

        self.name_bg_scaled = pygame.transform.smoothscale(self.name_bg, (W, H))
        btn_w, btn_h = 200, 48
        cx = W // 2 - btn_w // 2
        y_start = int(H * 0.80)

        self.btn_start = Button(pygame.Rect(cx, y_start, btn_w, btn_h), "시작하기", self.font_btn)
        y_diff = int(H * 0.62)
        gap = 10
        self.btn_easy = Button(pygame.Rect(cx, y_diff, btn_w, btn_h), "쉬움 (준비중)", self.font_btn, enabled=False)
        self.btn_normal = Button(pygame.Rect(cx, y_diff + (btn_h + gap), btn_w, btn_h), "보통", self.font_btn, enabled=True)
        self.btn_hard = Button(pygame.Rect(cx, y_diff + 2 * (btn_h + gap), btn_w, btn_h), "어려움 (준비중)", self.font_btn, enabled=False)

        self.diff_title_y = max(80, int(self.btn_easy.rect.y - 80))
        input_w, input_h = 340, 58
        self.name_rect = pygame.Rect(W // 2 - input_w // 2, int(H * 0.48), input_w, input_h)

    def reset_to_start(self):
        self.mode = "START"
        self.done = False
        self.result = None
        self.name_input = None
        self._rebuild_layout()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.VIDEORESIZE:
            self._rebuild_layout()

        if self.mode == "START":
            if self.btn_start.handle_event(event):
                self.mode = "DIFF"

        elif self.mode == "DIFF":
            self.btn_easy.handle_event(event)
            self.btn_hard.handle_event(event)

            if self.btn_normal.handle_event(event):
                self.mode = "NAME"
                self.name_input = TextInput(self.name_rect, self.font_btn, max_len=12)

        elif self.mode == "NAME":
            assert self.name_input is not None
            self.name_input.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._finish_if_valid()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.mode = "DIFF"
                self.name_input = None

    def _finish_if_valid(self):
        name = (self.name_input.text if self.name_input else "").strip()
        if name == "":
            return

        self.done = True
        self.result = {"difficulty": "normal", "name": name}

    def update(self, dt: float):
        if self.mode == "NAME" and self.name_input:
            self.name_input.update(dt)

    def draw(self):
        screen = self.screen
        W, H = screen.get_size()
        screen.fill((0, 0, 0))
        if self.mode == "NAME":
            screen.blit(self.name_bg_scaled, (0, 0))
        else:
            screen.blit(self.start_bg_scaled, self.start_bg_pos)

        if self.mode == "START":
            self.btn_start.draw(screen)

        elif self.mode == "DIFF":
            self._draw_center_title("난이도 선택")
            self.btn_easy.draw(screen)
            self.btn_normal.draw(screen)
            self.btn_hard.draw(screen)

        elif self.mode == "NAME":
            title = self.font_name_title.render("고양이 이름을 지어주세요", True, (0, 0, 0))
            title_y = max(60, self.name_rect.y - 70)
            screen.blit(title, title.get_rect(center=(W // 2, title_y)))

            assert self.name_input is not None
            self.name_input.draw(screen)

            hint = self.font_small.render("Enter 키로 확정", True, (0, 0, 0))
            screen.blit(hint, hint.get_rect(center=(W // 2, self.name_rect.y + self.name_rect.h + 22)))

            back = self.font_small.render("ESC: 뒤로", True, (0, 0, 0))
            screen.blit(back, (20, H - 40))

    def _draw_center_title(self, text: str):
        W, _ = self.screen.get_size()
        t = self.font_title.render(text, True, (255, 255, 255))
        y = getattr(self, "diff_title_y", 120)
        self.screen.blit(t, t.get_rect(center=(W // 2, y)))
