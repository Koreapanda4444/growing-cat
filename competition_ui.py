import pygame

import competition
import state as game_state
from config import asset_path
from pg_utils import screen_events, GameQuit, load_font


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
        self.enter_rect = pygame.Rect(245, 304, 120, 30)
        self.view = "event"
        self.page = 0
        self.tabs = {key: pygame.Rect(20 + i * 123, 80, 114, 26)
                     for i, key in enumerate(("event", "trophies", "history"))}
        self.prev_rect = pygame.Rect(35, 525, 95, 30)
        self.next_rect = pygame.Rect(270, 525, 95, 30)

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.handle_events()
            if self.running:
                self.draw()

    def _click(self):
        if self.play_click_sound:
            self.play_click_sound()

    def handle_events(self):
        for event in screen_events():
            if event.type == pygame.QUIT:
                raise GameQuit
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE) and self.view == "event":
                    self._try_enter()
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.change_page(-1 if event.key == pygame.K_LEFT else 1)
            elif event.type == pygame.MOUSEWHEEL:
                self.change_page(-event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for key, rect in self.tabs.items():
                    if rect.collidepoint(event.pos):
                        self.view, self.page = key, 0
                        return
                if self.view != "event":
                    for rect, delta in ((self.prev_rect, -1), (self.next_rect, 1)):
                        if rect.collidepoint(event.pos):
                            self.change_page(delta)
                            return
                if self.close_rect.collidepoint(event.pos):
                    self._click()
                    self.running = False
                    return
                if self.view == "event" and self.enter_rect.collidepoint(event.pos):
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
        for key, label in (("event", "대회·결과"), ("trophies", "트로피 도감"), ("history", "전체 기록")):
            self._draw_button(self.tabs[key], "대회·결과" if key == "event" else label, enabled=self.view == key)
        if self.view == "event":
            ctx = self._context()
            self._draw_event_panel(ctx)
            self._draw_score_panel(ctx)
            self._draw_trophy_panel()
            self._draw_history_panel()
        else:
            self._draw_records()
        league = competition.league_info(self.competition_data)
        level = league["next"]
        text = f"다음 {level[0]}: {level[1]}P · {level[2]}승 / 우승=S등급" if level else "마스터 리그 달성! / 우승=S등급"
        self.screen.blit(self.small_font.render(text, True, (70, 70, 70)), (20, 579))
        pygame.display.flip()

    def _draw_top(self):
        title = self.big_font.render("고양이 대회", True, (0, 0, 0))
        self.screen.blit(title, (20, 20))

        day = max(1, int(getattr(self.state, "day", 1)))
        league = competition.league_info(self.competition_data)
        difficulty = game_state.get_difficulty_label(getattr(self.state, "difficulty", "normal"))
        meta = self.font.render(f"{day}일차 / {difficulty} / {league['name']} {league['points']}P", True, (70, 70, 70))
        self.screen.blit(meta, (20, 52))

        pygame.draw.rect(self.screen, PANEL_COLOR, self.close_rect)
        pygame.draw.rect(self.screen, BORDER, self.close_rect, 1)
        x_text = self.font.render("X", True, (0, 0, 0))
        self.screen.blit(x_text, x_text.get_rect(center=self.close_rect.center))

    def _draw_event_panel(self, ctx):
        rect = pygame.Rect(20, 112, 360, 126)
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
        rect = pygame.Rect(20, 250, 360, 94)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        score_text = self.font.render(f"예상 점수 {ctx['estimate']}점 / 예상 등급 {ctx['est_grade']}", True, (0, 0, 0))
        self.screen.blit(score_text, (rect.x + 14, rect.y + 12))

        if self.message:
            msg = self.message
        elif ctx["today_result"]:
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
        rect = pygame.Rect(20, 356, 360, 98)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        summary = competition.totals(self.competition_data)
        self.screen.blit(self.small_font.render(f"트로피 · {summary['wins']}승 / 연승 {summary['streak']} (최고 {summary['best_streak']})", True, (0, 0, 0)), (rect.x + 14, rect.y + 10))
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
        rect = pygame.Rect(20, 466, 360, 104)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)

        self.screen.blit(self.font.render("최근 참가 기록", True, (0, 0, 0)), (rect.x + 14, rect.y + 10))
        history = list(reversed(self.competition_data.get("history", [])))
        if not history:
            self.screen.blit(self.small_font.render("대회 참가 기록이 없습니다.", True, (80, 80, 80)), (rect.x + 14, rect.y + 42))
            return

        for index, entry in enumerate(history[:3]):
            line = f"{entry['day']}일차 {entry['name']} {entry['grade']} / {entry['score']}점"
            self.screen.blit(self.small_font.render(line, True, (55, 55, 55)), (rect.x + 14, rect.y + 38 + index * 20))

    def _draw_button(self, rect, text, *, enabled=True):
        fill = (210, 230, 210) if enabled else (215, 215, 215)
        text_color = (0, 0, 0) if enabled else (130, 130, 130)
        pygame.draw.rect(self.screen, fill, rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)
        label = self.font.render(text, True, text_color)
        self.screen.blit(label, label.get_rect(center=rect.center))


    def page_count(self):
        if self.view == "trophies":
            return (len(competition.COMPETITIONS) + 2) // 3
        return max(1, (len(self.competition_data["history"]) + 3) // 4)

    def change_page(self, delta):
        if self.view != "event":
            self.page = max(0, min(self.page_count() - 1, self.page + delta))

    def _record_card(self, y, lines):
        rect = pygame.Rect(20, y, 360, 82)
        pygame.draw.rect(self.screen, (252, 252, 252), rect)
        pygame.draw.rect(self.screen, BORDER, rect, 1)
        for index, line in enumerate(lines):
            font = self.font if index == 0 else self.small_font
            self.screen.blit(font.render(line, True, (40, 40, 40)), (34, y + 10 + index * 22))

    def _draw_records(self):
        self.change_page(0)
        total = competition.totals(self.competition_data)
        self.screen.blit(self.font.render(f"총 {total['entries']}회 참가 · {total['wins']}승 (S등급)", True, BORDER), (20, 119))
        if self.view == "trophies":
            for i, comp in enumerate(competition.COMPETITIONS[self.page * 3:(self.page + 1) * 3]):
                trophy = self.competition_data["trophies"].get(comp["id"], {})
                recent = next((e for e in reversed(self.competition_data["history"]) if e["id"] == comp["id"]), None)
                lines = [f"{comp['name']} · 최고 {trophy.get('best_grade') or '-'}",
                         f"참가 {trophy.get('count', 0)}회 / 우승 {trophy.get('wins', 0)}회 / 최고 {trophy.get('best_score', 0)}점",
                         f"최근: {recent['day']}일 {recent['grade']}등급 {recent['score']}점" if recent else "최근 저장 이력 없음"]
                self._record_card(155 + i * 98, lines)
            goals = " · ".join(self.competition_data["goals"]) or "아직 달성한 목표가 없습니다."
            self.screen.blit(self.small_font.render("누적 목표: 5/10승 · 연승 목표: 3/5승", True, BORDER), (20, 462))
            self.screen.blit(self.small_font.render(goals, True, (40, 110, 65)), (20, 488))
        else:
            history = list(reversed(self.competition_data["history"]))
            for i, entry in enumerate(history[self.page * 4:(self.page + 1) * 4]):
                self._record_card(145 + i * 90, [f"{entry['day']}일 · {entry['name']}",
                    f"{entry['grade']}등급 / {entry['score']}점 / 일반 보상 {entry['reward']}코인"])
            if not history:
                self.screen.blit(self.font.render("참가 기록이 없습니다.", True, (80, 80, 80)), (20, 170))
        self._draw_button(self.prev_rect, "이전", enabled=self.page > 0)
        self._draw_button(self.next_rect, "다음", enabled=self.page + 1 < self.page_count())
        caption = self.font.render(f"{self.page + 1}/{self.page_count()}", True, BORDER)
        self.screen.blit(caption, caption.get_rect(center=(200, 540)))
