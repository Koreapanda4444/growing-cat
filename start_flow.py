import os
import pygame


def get_korean_font(size: int) -> pygame.font.Font:
    # 윈도우/맥/리눅스에서 한글 잘 나오는 폰트 후보들
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
        # 색은 단순히 UI용이라 고정값 사용
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
    """
    모드:
      - "START": 시작 배경(start.png) + [시작하기]
      - "DIFF" : 난이도 선택(쉬움/보통/어려움) -> 보통만 활성
      - "NAME" : 이름 입력 -> 확인 누르면 완료(게임 시작 신호)
    완료되면:
      flow.done == True
      flow.result == {"difficulty": "normal", "name": "..."}
    """

    def __init__(self, screen: pygame.Surface, assets_root: str = "assets"):
        self.screen = screen
        self.assets_root = assets_root

        self.mode = "START"
        self.done = False
        self.result = None  # dict

        self.font_title = get_korean_font(44)
        self.font_name_title = get_korean_font(24)
        self.font_btn = get_korean_font(26)
        self.font_small = get_korean_font(18)

        self._load_assets()
        self._rebuild_layout()

        # 이름 입력
        self.name_input: TextInput | None = None

    def _load_assets(self):
        # 사용자가 말한: assets/ui/start.png
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

        # 버튼 배치(원하는 위치로 숫자만 바꾸면 됨)
        btn_w, btn_h = 220, 56
        cx = W // 2 - btn_w // 2
        y_start = int(H * 0.70)

        self.btn_start = Button(pygame.Rect(cx, y_start, btn_w, btn_h), "시작하기", self.font_btn)

        # 난이도 버튼들
        y_diff = int(H * 0.42)
        gap = 14
        self.btn_easy = Button(pygame.Rect(cx, y_diff, btn_w, btn_h), "쉬움 (준비중)", self.font_btn, enabled=False)
        self.btn_normal = Button(pygame.Rect(cx, y_diff + (btn_h + gap), btn_w, btn_h), "보통", self.font_btn, enabled=True)
        self.btn_hard = Button(pygame.Rect(cx, y_diff + 2 * (btn_h + gap), btn_w, btn_h), "어려움 (준비중)", self.font_btn, enabled=False)

        # 이름 입력 UI
        input_w, input_h = 340, 58
        self.name_rect = pygame.Rect(W // 2 - input_w // 2, int(H * 0.48), input_w, input_h)

    def reset_to_start(self):
        """설정의 초기화 버튼에서 이거 호출하면 '완전 시작창'으로 돌아감"""
        self.mode = "START"
        self.done = False
        self.result = None
        self.name_input = None
        self._rebuild_layout()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.VIDEORESIZE:
            # 화면 크기 바뀌면 레이아웃 재계산(네가 리사이즈 지원하면 유용)
            self._rebuild_layout()

        if self.mode == "START":
            if self.btn_start.handle_event(event):
                self.mode = "DIFF"

        elif self.mode == "DIFF":
            # 쉬움/어려움은 disabled라 클릭 무시됨
            self.btn_easy.handle_event(event)
            self.btn_hard.handle_event(event)

            if self.btn_normal.handle_event(event):
                # 보통만 지원
                self.mode = "NAME"
                self.name_input = TextInput(self.name_rect, self.font_btn, max_len=12)

        elif self.mode == "NAME":
            assert self.name_input is not None
            self.name_input.handle_event(event)

            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self._finish_if_valid()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # 이름 입력에서 ESC 누르면 난이도로 돌아가기
                self.mode = "DIFF"
                self.name_input = None

    def _finish_if_valid(self):
        name = (self.name_input.text if self.name_input else "").strip()
        if name == "":
            # 이름이 비었으면 간단 안내만 띄우기(텍스트)
            # (팝업 쓰고 싶으면 여기서 토스트/메시지박스 구현)
            return

        self.done = True
        self.result = {"difficulty": "normal", "name": name}

    def update(self, dt: float):
        if self.mode == "NAME" and self.name_input:
            self.name_input.update(dt)

    def draw(self):
        screen = self.screen
        W, H = screen.get_size()

        # 배경
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
        self.screen.blit(t, t.get_rect(center=(W // 2, 120)))
