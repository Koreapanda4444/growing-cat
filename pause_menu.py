import pygame


class _Button:
    def __init__(self, rect: pygame.Rect, text: str, font: pygame.font.Font):
        self.rect = pygame.Rect(rect)
        self.text = text
        self.font = font
        self.hover = False

    def handle(self, event: pygame.event.Event) -> bool:
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False

    def draw(self, screen: pygame.Surface):
        bg = (60, 180, 90) if self.hover else (40, 140, 70)
        pygame.draw.rect(screen, bg, self.rect, border_radius=10)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, width=2, border_radius=10)
        t = self.font.render(self.text, True, (255, 255, 255))
        screen.blit(t, t.get_rect(center=self.rect.center))


class PauseMenu:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._rebuild()

    def _rebuild(self):
        self._init_fonts()
        self._build()

    def _init_fonts(self):
        W, H = self.screen.get_size()

        title_size = max(22, min(32, int(H * 0.045)))
        btn_size = max(16, min(22, int(H * 0.032)))
        hint_size = max(12, min(18, int(H * 0.024)))

        for name in ("malgungothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"):
            f1 = pygame.font.SysFont(name, title_size)
            f2 = pygame.font.SysFont(name, btn_size)
            f3 = pygame.font.SysFont(name, hint_size)
            if f1 and f2 and f3:
                self.font_title, self.font_btn, self.font_hint = f1, f2, f3
                return
        self.font_title = pygame.font.SysFont(None, title_size)
        self.font_btn = pygame.font.SysFont(None, btn_size)
        self.font_hint = pygame.font.SysFont(None, hint_size)

    def _build(self):
        W, H = self.screen.get_size()

        bw = min(300, max(220, W - 60))
        bh = max(38, min(52, int(self.font_btn.get_height() * 1.8)))
        gap = max(8, int(bh * 0.18))
        x = W // 2 - bw // 2
        y0 = int(H * 0.28)

        self.btn_resume = _Button(pygame.Rect(x, y0 + 0*(bh+gap), bw, bh), "계속하기", self.font_btn)
        self.btn_settings = _Button(pygame.Rect(x, y0 + 1*(bh+gap), bw, bh), "설정", self.font_btn)
        self.btn_photo = _Button(pygame.Rect(x, y0 + 2*(bh+gap), bw, bh), "사진찍기(F12)", self.font_btn)
        self.btn_to_start = _Button(pygame.Rect(x, y0 + 3*(bh+gap), bw, bh), "시작 화면으로", self.font_btn)
        self.btn_quit = _Button(pygame.Rect(x, y0 + 4*(bh+gap), bw, bh), "종료", self.font_btn)

        self.buttons = [
            ("resume", self.btn_resume),
            ("settings", self.btn_settings),
            ("photo", self.btn_photo),
            ("to_start", self.btn_to_start),
            ("quit", self.btn_quit),
        ]

    def handle_event(self, event: pygame.event.Event) -> str | None:
        if event.type == pygame.VIDEORESIZE:
            self._rebuild()

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"

        if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
            return "photo"

        for action, btn in self.buttons:
            if btn.handle(event):
                return action

        return None

    def draw(self):
        screen = self.screen
        W, H = screen.get_size()

        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 170))
        screen.blit(overlay, (0, 0))

        title = self.font_title.render("일시정지", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(W // 2, int(H * 0.20))))

        hint = self.font_hint.render("ESC: 계속하기   F12: 사진찍기", True, (220, 220, 220))
        screen.blit(hint, hint.get_rect(center=(W // 2, int(H * 0.26))))

        for _, btn in self.buttons:
            btn.draw(screen)
