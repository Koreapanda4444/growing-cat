import pygame

import competition
import state as game_state
from config import asset_path
from pg_utils import load_font


BG_COLOR = (245, 245, 245)
PANEL_COLOR = (230, 230, 230)
BORDER = (0, 0, 0)
FONT_PATH = asset_path("fonts", "ThinDungGeunMo.ttf")


class CompetitionUI:
    def __init__(self, screen, cat, state, inventory, competition_data, on_enter, play_click_sound=None):
        self.screen = screen
        self.cat = cat
        self.state = state
        self.inventory = inventory
        self.competition_data = competition.normalize_competition_data(competition_data)
        self.on_enter = on_enter
        self.play_click_sound = play_click_sound
        self.running = True
        self.message = ""

        self.font = load_font(FONT_PATH, 17)
        self.big_font = load_font(FONT_PATH, 22)
        self.small_font = load_font(FONT_PATH, 13)

        self.close_rect = pygame.Rect(360, 10, 30, 30)
        self.enter_rect = pygame.Rect(245, 248, 120, 36)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.handle_events()
            self.draw()

    def _click(self):
        if self.play_click_sound:
            self.play_click_sound()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._try_enter()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.close_rect.collidepoint(event.pos):
                    self._click()
                    self.running = False
                    return
                if self.enter_rect.collidepoint(event.pos):
                    self._click()
                    self._try_enter()

    def _try_enter(self):
        if not self._can_enter():
            return
        result = self.on_enter()
        if not isinstance(result, dict):
            self.message = "참가 실패"
            return
        self.competition_data = competition.normalize_competition_data(result.get("competition_data", self.competition_data))
        self.message = str(result.get("message", ""))

    def _context(self):
        day = max(1, int(getattr(self.state, "day", 1)))
        comp = competition.competition_for_day(day)
        difficulty = getattr(self.state, "difficulty", "normal")
        fee = competition.entry_fee(comp, difficulty)
        event_day = competition.is_event_day(day)
        entered = competition.entered_today(self.competition_data, day)
        estimate = competition.estimate_score(comp["id"], self.cat, self.state, self.inventory)
        est_grade = competition.grade_for_score(estimate, difficulty)
        today_result = competition.latest_today_result(self.competition_data, day)
        return {
            "day": day,
            "comp": comp,
            "difficulty": difficulty,
            "fee": fee,
            "event_day": event_day,
            "days_left": competition.days_until_event(day),
            "entered": entered,
            "estimate": estimate,
            "est_grade": est_grade,
            "today_result": today_result,
        }

    def _can_enter(self):
        ctx = self._context()
        return (
            ctx["event_day"]
            and not ctx["entered"]
            and int(getattr(self.state, "money", 0)) >= ctx["fee"]
        )

    def draw(self):
        self.screen.fill(BG_COLOR)
        self._draw_top()
        ctx = self._context()
        self._draw_event_panel(ctx)
        self._draw_score_panel(ctx)
        self._draw_trophy_panel()
        self._draw_history_panel()
        pygame.display.flip()

    def _draw_top(self):
        title = self.big_font.render("고양이 대회", True, (0, 0, 0))
        self.screen.blit(title, (20, 20))

        day = max(1, int(getattr(self.state, "day", 1)))
        difficulty = game_state.get_difficulty_label(getattr(self.state, "difficulty", "normal"))
        meta = self.font.render(f"{day}일차 / 난이도 {difficulty}", True, (70, 70, 70))
        self.screen.blit(meta, (20, 52))

        pygame.draw.rect(self.screen, PANEL_COLOR, self.close_rect)
        pygame.draw.rect(self.screen, BORDER, self.close_rect, 1)
        x_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))

    def _draw_event_panel(self, ctx):
        rect = pygame.Rect(20, 88, 360, 126)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        comp = ctx["comp"]
        title = self.big_font.render(comp["name"], True, (0, 0, 0))
        self.screen.blit(title, (rect.x + 14, rect.y + 12))

        if ctx["event_day"]:
            status = "오늘 개최"
            color = (40, 130, 70)
        else:
            status = f"{ctx['days_left']}일 뒤 개최"
            color = (90, 90, 90)
        self.screen.blit(self.font.render(status, True, color), (rect.x + 14, rect.y + 44))
        self.screen.blit(self.small_font.render(comp["desc"], True, (60, 60, 60)), (rect.x + 14, rect.y + 72))
        self.screen.blit(self.font.render(f"참가비: {ctx['fee']} 코인", True, (70, 70, 70)), (rect.x + 14, rect.y + 94))

    def _draw_score_panel(self, ctx):
        rect = pygame.Rect(20, 226, 360, 82)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        score_text = self.font.render(f"예상 점수 {ctx['estimate']}점 / 예상 등급 {ctx['est_grade']}", True, (0, 0, 0))
        self.screen.blit(score_text, (rect.x + 14, rect.y + 12))

        if ctx["today_result"]:
            result = ctx["today_result"]
            msg = f"오늘 결과: {result['grade']}등급 / {result['score']}점 / +{result['reward']}코인"
        elif not ctx["event_day"]:
            msg = "대회 당일에 참가할 수 있습니다."
        elif ctx["entered"]:
            msg = "오늘은 이미 참가했습니다."
        elif int(getattr(self.state, "money", 0)) < ctx["fee"]:
            msg = "참가비가 부족합니다."
        else:
            msg = self.message or "참가하면 실제 점수와 보상이 결정됩니다."

        self.screen.blit(self.small_font.render(msg, True, (90, 60, 60) if "부족" in msg else (60, 60, 60)), (rect.x + 14, rect.y + 43))

        enabled = self._can_enter()
        self._draw_button(self.enter_rect, "참가하기", enabled=enabled)

    def _draw_trophy_panel(self):
        rect = pygame.Rect(20, 326, 360, 104)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        self.screen.blit(self.font.render("트로피", True, (0, 0, 0)), (rect.x + 14, rect.y + 10))
        trophies = self.competition_data.get("trophies", {})
        if not trophies:
            self.screen.blit(self.small_font.render("아직 획득한 트로피가 없습니다.", True, (80, 80, 80)), (rect.x + 14, rect.y + 42))
            return

        lines = []
        for comp in competition.COMPETITIONS:
            trophy = trophies.get(comp["id"])
            if not trophy:
                continue
            lines.append(f"{comp['name']}: 최고 {trophy.get('best_grade', '-')} / {trophy.get('count', 0)}회")

        for index, line in enumerate(lines[:3]):
            self.screen.blit(self.small_font.render(line, True, (55, 55, 55)), (rect.x + 14, rect.y + 38 + index * 20))

    def _draw_history_panel(self):
        rect = pygame.Rect(20, 448, 360, 124)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        self.screen.blit(self.font.render("최근 참가 기록", True, (0, 0, 0)), (rect.x + 14, rect.y + 10))
        history = list(reversed(self.competition_data.get("history", [])))
        if not history:
            self.screen.blit(self.small_font.render("대회 참가 기록이 없습니다.", True, (80, 80, 80)), (rect.x + 14, rect.y + 42))
            return

        for index, entry in enumerate(history[:4]):
            line = f"{entry['day']}일차 {entry['name']} {entry['grade']} / {entry['score']}점"
            self.screen.blit(self.small_font.render(line, True, (55, 55, 55)), (rect.x + 14, rect.y + 38 + index * 20))

    def _draw_button(self, rect, text, *, enabled=True):
        fill = (210, 230, 210) if enabled else (215, 215, 215)
        text_color = (0, 0, 0) if enabled else (130, 130, 130)
        pygame.draw.rect(self.screen, fill, rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)
        label = self.font.render(text, True, text_color)
        self.screen.blit(label, label.get_rect(center=rect.center))
