import pygame

import competition
import evolution
import minigame_records
import state
from config import asset_path
from pg_utils import GameQuit, load_font, screen_events


ACTIVITIES = {"feed": "먹이", "play": "놀기", "clean": "청소", "sleep": "수면",
              "special": "특별 돌봄", "pet": "고양이 클릭", "buy": "상점 구매"}
HISTORY_LIMIT = 60


def _int(value):
    try:
        return max(0, int(value))
    except (TypeError, ValueError, OverflowError):
        return 0


def normalize(value, day=1):
    value = value if isinstance(value, dict) else {}
    source = value.get("activities", {})
    source = source if isinstance(source, dict) else {}
    history = value.get("history", [])
    return {"started_day": max(1, _int(value.get("started_day", day))),
            "days_survived": _int(value.get("days_survived", max(0, day - 1))),
            "coins_earned": _int(value.get("coins_earned")),
            "activities": {key: _int(source.get(key)) for key in ACTIVITIES},
            "friendship_best": state.normalize_friendship(value.get("friendship_best")),
            "last_stage": value.get("last_stage") if value.get("last_stage") in evolution.EVOLUTION_ORDER else "",
            "history": [{"day": max(1, _int(e.get("day"))), "text": e["text"][:70]}
                        for e in (history if isinstance(history, list) else [])[-HISTORY_LIMIT:]
                        if isinstance(e, dict) and isinstance(e.get("text"), str)]}


def add_activity(game_state, activity):
    if activity in ACTIVITIES:
        data = normalize(game_state.growth_records, game_state.day)
        data["activities"][activity] += 1
        game_state.growth_records = data


def earn(game_state, coins):
    data = normalize(game_state.growth_records, game_state.day)
    data["coins_earned"] += _int(coins)
    game_state.growth_records = data


def sync(game_state, cat):
    data = normalize(game_state.growth_records, game_state.day)
    notes = []
    if cat.stage != data["last_stage"]:
        notes.append(("진화: " if data["last_stage"] else "기록 시작: ") + cat.stage)
        data["last_stage"] = cat.stage
    for threshold, label in state.FRIENDSHIP_LEVELS[1:]:
        if data["friendship_best"] < threshold <= cat.friendship:
            notes.append("친밀도: " + label)
    data["friendship_best"] = max(data["friendship_best"], cat.friendship)
    survived = max(0, game_state.day - 1)
    for target in (7, 21, 30, 35, 100):
        if data["days_survived"] < target <= survived:
            notes.append(f"{target}일 생존")
    data["days_survived"] = max(data["days_survived"], survived)
    data["history"].extend({"day": game_state.day, "text": note} for note in notes)
    data["history"] = data["history"][-HISTORY_LIMIT:]
    game_state.growth_records = data
    return data


class GrowthRecordsUI:
    def __init__(self, screen, game_state, cat, contests, events, missions):
        self.screen, self.state = screen, game_state
        self.data = sync(game_state, cat)
        records = minigame_records.normalize(game_state.minigame_records)
        total = competition.totals(contests)
        activities = self.data["activities"]
        self.rows = [("생존", f"{self.data['days_survived']}일 / 현재 {game_state.day}일차"),
                     ("누적 획득 코인", str(self.data["coins_earned"])),
                     ("돌봄 횟수", str(sum(activities[key] for key in ("feed", "play", "clean", "sleep", "special"))))]
        self.rows.extend((label, f"{activities[key]}회") for key, label in ACTIVITIES.items())
        self.rows.extend([(name, f"{records[key]['plays']}회 / {records[key]['wins']}승") for key, name in minigame_records.GAME_NAMES.items()])
        self.rows.extend([("대회", f"{total['entries']}회 / {total['wins']}승 / 최고 {total['best_streak']}연승"),
                          ("리그", competition.league_info(contests)["name"]),
                          ("이벤트 해결", f"{events['completed']}회"),
                          ("일일 미션 완수", f"{missions['total_completed']}일 / 최고 연속 {missions['best_streak']}일"),
                          ("최고 친밀도", str(self.data["friendship_best"]))])
        path = asset_path("fonts", "ThinDungGeunMo.ttf")
        self.font, self.small_font = load_font(path, 18), load_font(path, 13)
        self.big_font = load_font(path, 22)
        self.view, self.page, self.running = "stats", 0, True
        self.close_rect = pygame.Rect(360, 10, 30, 30)
        self.tabs = {"stats": pygame.Rect(20, 90, 170, 30), "history": pygame.Rect(210, 90, 170, 30)}
        self.prev_rect, self.next_rect = pygame.Rect(35, 530, 95, 32), pygame.Rect(270, 530, 95, 32)

    def entries(self):
        return self.rows if self.view == "stats" else [(f"{e['day']}일차", e["text"]) for e in reversed(self.data["history"])]

    def change_page(self, delta):
        self.page = max(0, min(max(0, (len(self.entries()) - 1) // 7), self.page + delta))

    def handle_events(self):
        for event in screen_events():
            if event.type == pygame.QUIT:
                raise GameQuit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    self.change_page(-1 if event.key == pygame.K_LEFT else 1)
            elif event.type == pygame.MOUSEWHEEL:
                self.change_page(-event.y)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.close_rect.collidepoint(event.pos):
                    self.running = False
                for key, rect in self.tabs.items():
                    if rect.collidepoint(event.pos):
                        self.view, self.page = key, 0
                for rect, delta in ((self.prev_rect, -1), (self.next_rect, 1)):
                    if rect.collidepoint(event.pos):
                        self.change_page(delta)

    def _button(self, rect, label):
        pygame.draw.rect(self.screen, (230, 230, 230), rect)
        pygame.draw.rect(self.screen, (0, 0, 0), rect, 1)
        text = self.font.render(label, True, (0, 0, 0))
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw(self):
        self.screen.fill((245, 245, 245))
        self.screen.blit(self.big_font.render("육성 통계 · 성장 기록", True, (0, 0, 0)), (20, 20))
        self.screen.blit(self.small_font.render(f"행동·코인 통계는 {self.data['started_day']}일차부터 기록", True, (80, 80, 80)), (20, 60))
        self._button(self.close_rect, "X")
        for key, label in (("stats", "통계"), ("history", "성장 기록")):
            self._button(self.tabs[key], label + (" ·" if self.view == key else ""))
        for i, (label, value) in enumerate(self.entries()[self.page * 7:(self.page + 1) * 7]):
            rect = pygame.Rect(20, 138 + i * 52, 360, 46)
            pygame.draw.rect(self.screen, (230, 235, 230), rect)
            self.screen.blit(self.small_font.render(label, True, (80, 80, 80)), (30, rect.y + 4))
            self.screen.blit(self.font.render(value, True, (0, 0, 0)), (30, rect.y + 23))
        for rect, label in ((self.prev_rect, "이전"), (self.next_rect, "다음")):
            self._button(rect, label)
        text = self.font.render(f"{self.page + 1}/{max(1, (len(self.entries()) + 6) // 7)}", True, (0, 0, 0))
        self.screen.blit(text, text.get_rect(center=(200, 546)))
        pygame.display.flip()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(60)
            self.handle_events()
            if self.running:
                self.draw()
