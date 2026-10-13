from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path
import time


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class AchievementDef:
    aid: str
    title: str
    desc: str
    a_type: str
    target_key: Optional[str] = None
    target_value: Optional[int] = None
    hidden: bool = False
    points: int = 10


def default_achievements() -> List[AchievementDef]:
    return [
        AchievementDef("A001", "첫 하루", "하루를 무사히 넘겼다.", "once", "day_end"),
        AchievementDef("A002", "일주일 생존", "7일을 생존했다.", "counter", "days_survived", 7, points=20),
        AchievementDef("A003", "한 달 생존", "30일을 생존했다.", "counter", "days_survived", 30, points=40),

        AchievementDef("A010", "코인 첫 수확", "코인을 처음 벌었다.", "once", "coins_earned"),
        AchievementDef("A011", "코인 부자", "누적 코인 획득 1,000을 달성했다.", "counter", "coins_total", 1000, points=30),
        AchievementDef("A012", "코인 재벌", "누적 코인 획득 10,000을 달성했다.", "counter", "coins_total", 10000, points=80),

        AchievementDef("A020", "첫 구매", "상점에서 아이템을 처음 구매했다.", "once", "item_bought"),
        AchievementDef("A021", "쇼핑 중독", "아이템을 20회 구매했다.", "counter", "items_bought", 20, points=30),

        AchievementDef("A030", "미니게임 데뷔", "미니게임을 1회 플레이했다.", "once", "minigame_played"),
        AchievementDef("A031", "미니게임 러너", "미니게임을 30회 플레이했다.", "counter", "minigame_play_count", 30, points=40),
        AchievementDef("A032", "첫 승리", "미니게임에서 1회 승리했다.", "once", "minigame_won"),
        AchievementDef("A033", "승리의 발톱", "미니게임 20승을 달성했다.", "counter", "minigame_win_count", 20, points=60),

        AchievementDef("A040", "첫 진화", "처음으로 진화했다.", "once", "evolved"),
        AchievementDef("A041", "성묘", "성묘 단계에 도달했다.", "evolve", "adult", points=30),
        AchievementDef("A042", "사자", "사자 단계에 도달했다.", "evolve", "lion", points=60),
        AchievementDef("A043", "공룡", "공룡 단계에 도달했다.", "evolve", "dino", points=100),

        AchievementDef("A050", "깔끔한 고양이", "청결도 90 이상으로 하루를 마무리했다.", "stat", "cleanliness_90"),
        AchievementDef("A051", "행복 만땅", "행복도 90 이상으로 하루를 마무리했다.", "stat", "happiness_90"),
        AchievementDef("A052", "완벽한 하루", "행복/청결 80↑, 배고픔/피로 30↓로 하루를 마무리했다.", "stat", "perfect_day", points=50),

        AchievementDef("A060", "고양이도 잠수함을 탄다", "…뭔가 이상한 일이 있었다.", "once", "weird_event", hidden=True, points=70),

        AchievementDef("A080", "익숙한 손길", "친밀도 100에 도달했다.", "counter", "friendship_best", 100),
        AchievementDef("A081", "마음의 친구", "친밀도 300에 도달했다.", "counter", "friendship_best", 300, points=30),
        AchievementDef("A082", "우리 가족", "친밀도 1,000에 도달했다.", "counter", "friendship_best", 1000, points=80),
        AchievementDef("A090", "작은 사건", "랜덤 이벤트를 처음 해결했다.", "counter", "events_completed", 1),
        AchievementDef("A091", "추억 수집가", "랜덤 이벤트 10개를 해결했다.", "counter", "events_completed", 10, points=30),
        AchievementDef("A100", "오늘도 성실하게", "일일 미션 전체 보상을 받았다.", "counter", "missions_completed", 1),
        AchievementDef("A101", "일상의 습관", "일일 미션을 누적 7일 완수했다.", "counter", "missions_completed", 7, points=30),
        AchievementDef("A102", "끊이지 않는 돌봄", "일일 미션을 7일 연속 완수했다.", "counter", "mission_streak", 7, points=50),
        AchievementDef("A110", "도전을 넘어서", "미니게임 도전 모드를 완수했다.", "counter", "challenge_wins", 1, points=20),
        AchievementDef("A111", "도전의 발톱", "미니게임 도전 모드 5승을 달성했다.", "counter", "challenge_wins", 5, points=40),
        AchievementDef("A112", "만능 놀이 친구", "미니게임 5종에서 모두 승리했다.", "counter", "games_won", 5, points=50),
        AchievementDef("A120", "우승의 주인공", "대회에서 S등급을 5회 받았다.", "counter", "competition_wins", 5, points=40),
        AchievementDef("A121", "연승 행진", "대회 3연승을 달성했다.", "counter", "competition_streak", 3, points=40),
        AchievementDef("A122", "골드 무대", "골드 리그에 진입했다.", "counter", "league_level", 2, points=50),
        AchievementDef("A123", "마스터 고양이", "마스터 리그에 진입했다.", "counter", "league_level", 4, points=100),

        AchievementDef("A070", "첫 출전", "고양이 대회에 처음 참가했다.", "once", "competition_entered"),
        AchievementDef("A071", "무대 체질", "고양이 대회에서 S등급을 받았다.", "once", "competition_s_grade", points=30),
        AchievementDef("A072", "대회 단골", "고양이 대회에 10회 참가했다.", "counter", "competition_count", 10, points=50),
    ]

class AchievementsManager:
    def __init__(self, save_path: str = "achievements_save.json"):
        self.save_path = Path(save_path)
        self.defs: List[AchievementDef] = default_achievements()
        self.def_map: Dict[str, AchievementDef] = {d.aid: d for d in self.defs}

        self.unlocked: Dict[str, float] = {}
        self.counters: Dict[str, int] = {
            "days_survived": 0,
            "coins_total": 0,
            "items_bought": 0,
            "minigame_play_count": 0,
            "minigame_win_count": 0,
            "competition_count": 0,
        }

        self.toast_queue: List[Tuple[str, str, float]] = []

        self.load()

    def load(self) -> None:
        if not self.save_path.exists():
            return
        try:
            data = json.loads(self.save_path.read_text(encoding="utf-8"))
            self.unlocked = {k: float(v) for k, v in data.get("unlocked", {}).items()}
            self.counters.update({k: int(v) for k, v in data.get("counters", {}).items()})
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass

    def save(self) -> None:
        data = {
            "unlocked": self.unlocked,
            "counters": self.counters,
        }
        try:
            self.save_path.parent.mkdir(parents=True, exist_ok=True)
            self.save_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, TypeError, ValueError):
            pass

    def is_unlocked(self, aid: str) -> bool:
        return aid in self.unlocked

    def _unlock(self, aid: str) -> None:
        if self.is_unlocked(aid):
            return
        d = self.def_map.get(aid)
        if not d:
            return

        self.unlocked[aid] = time.time()
        self.toast_queue.append((f"업적 해금! {d.title}", d.desc, time.time() + 2.5))

    def _unlock_by_def(self, d: AchievementDef) -> None:
        self._unlock(d.aid)

    def on_event(self, event: str, **payload: Any) -> None:
        for d in self.defs:
            if d.a_type == "once" and d.target_key == event:
                self._unlock_by_def(d)

        if event == "day_end":
            self.counters["days_survived"] += 1

        elif event == "coins_earned":
            amt = _safe_int(payload.get("amount", 0))
            if amt > 0:
                self.counters["coins_total"] += amt

        elif event == "item_bought":
            self.counters["items_bought"] += 1

        elif event == "minigame_played":
            self.counters["minigame_play_count"] += 1

        elif event == "minigame_won":
            self.counters["minigame_win_count"] += 1

        elif event == "competition_entered":
            self.counters["competition_count"] += 1
            if str(payload.get("grade", "")).upper() == "S":
                for d in self.defs:
                    if d.a_type == "once" and d.target_key == "competition_s_grade":
                        self._unlock_by_def(d)

        elif event == "evolved":
            stage = str(payload.get("stage", "")).strip()
            if stage:
                for d in self.defs:
                    if d.a_type == "evolve" and d.target_key == stage:
                        self._unlock_by_def(d)

        self._check_counters()
        self.save()

    def check_progress(self, game_state, cat, contests, events, missions) -> None:
        import competition
        import minigame_records

        records = minigame_records.normalize(getattr(game_state, "minigame_records", None))
        summary = competition.totals(contests)
        values = {
            "friendship_best": getattr(cat, "friendship", 0),
            "events_completed": events.get("completed", 0),
            "missions_completed": missions.get("total_completed", 0),
            "mission_streak": missions.get("best_streak", 0),
            "challenge_wins": sum(entry["challenge_wins"] for entry in records.values()),
            "games_won": sum(entry["wins"] > 0 for entry in records.values()),
            "competition_wins": summary["wins"], "competition_streak": summary["best_streak"],
            "league_level": competition.league_info(contests)["index"],
        }
        before = (dict(self.counters), len(self.unlocked))
        for key, value in values.items():
            self.counters[key] = max(self.counters.get(key, 0), _safe_int(value))
        self._check_counters()
        if before != (self.counters, len(self.unlocked)):
            self.save()

    def check_stats_on_day_end(self, stats: Dict[str, int]) -> None:
        h = _safe_int(stats.get("happiness", 0))
        c = _safe_int(stats.get("cleanliness", 0))
        hu = _safe_int(stats.get("hunger", 0))
        f = _safe_int(stats.get("fatigue", 0))

        for d in self.defs:
            if d.a_type != "stat":
                continue

            if d.target_key == "cleanliness_90" and c >= 90:
                self._unlock_by_def(d)

            elif d.target_key == "happiness_90" and h >= 90:
                self._unlock_by_def(d)

            elif d.target_key == "perfect_day":
                if (h >= 80 and c >= 80 and hu <= 30 and f <= 30):
                    self._unlock_by_def(d)

        self.save()

    def _check_counters(self) -> None:
        for d in self.defs:
            if d.a_type != "counter":
                continue
            key = d.target_key
            target = d.target_value
            if not key or target is None:
                continue
            if self.counters.get(key, 0) >= target:
                self._unlock_by_def(d)

    def get_list(self) -> List[Dict[str, Any]]:
        out = []
        for d in self.defs:
            unlocked = self.is_unlocked(d.aid)
            title = d.title if (unlocked or not d.hidden) else "???"
            desc = d.desc if (unlocked or not d.hidden) else "숨겨진 업적"
            out.append({
                "id": d.aid,
                "title": title,
                "desc": desc,
                "unlocked": unlocked,
                "points": d.points,
            })
        return out

    def pop_active_toasts(self) -> List[Tuple[str, str]]:
        now = time.time()
        self.toast_queue = [(t, d, exp) for (t, d, exp) in self.toast_queue if exp > now]
        return [(t, d) for (t, d, exp) in self.toast_queue]

def draw_toasts(screen, font, ach: AchievementsManager) -> None:
    import pygame

    toasts = ach.pop_active_toasts()
    if not toasts:
        return

    pad = 10
    x, y = 15, 15
    for title, desc in toasts[:3]:
        w = 420
        h = 64
        box = pygame.Surface((w, h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 170))
        screen.blit(box, (x, y))

        t_surf = font.render(title, True, (255, 255, 255))
        d_surf = font.render(desc, True, (220, 220, 220))
        screen.blit(t_surf, (x + pad, y + 8))
        screen.blit(d_surf, (x + pad, y + 34))

        y += h + 8
