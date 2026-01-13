from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple
import json
from pathlib import Path
import time

@dataclass(frozen=True)
class AchievementDef:
    aid: str
    title: str
    desc: str
    a_type: str
    target_key: Optional[str] = None     # counter/stat/evolve에서 사용할 키
    target_value: Optional[int] = None   # counter 목표치
    hidden: bool = False                 # 숨김 업적(해금 전까지 ??? 표시)
    points: int = 10                     # 점수(선택)


def default_achievements() -> List[AchievementDef]:
    # 너 게임 콘텐츠에 맞춘 기본 업적 세트 (원하는 만큼 추가 가능)
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

        # 스탯 기반 업적(하루 종료 시 평가)
        AchievementDef("A050", "깔끔한 고양이", "청결도 90 이상으로 하루를 마무리했다.", "stat", "cleanliness_90"),
        AchievementDef("A051", "행복 만땅", "행복도 90 이상으로 하루를 마무리했다.", "stat", "happiness_90"),
        AchievementDef("A052", "완벽한 하루", "행복/청결 80↑, 배고픔/피로 30↓로 하루를 마무리했다.", "stat", "perfect_day", points=50),

        # 숨김 업적(해금 전까지 ???로 보여주기 좋음)
        AchievementDef("A060", "고양이도 잠수함을 탄다", "…뭔가 이상한 일이 있었다.", "once", "weird_event", hidden=True, points=70),
    ]


# ─────────────────────────────────────────────────────────────
# 저장 포맷
#  - unlocked: 해금된 업적 id 목록
#  - counters: 누적 카운터 (코인/승리/구매 등)
# ─────────────────────────────────────────────────────────────

class AchievementsManager:
    def __init__(self, save_path: str = "achievements_save.json"):
        self.save_path = Path(save_path)
        self.defs: List[AchievementDef] = default_achievements()
        self.def_map: Dict[str, AchievementDef] = {d.aid: d for d in self.defs}

        # 진행도
        self.unlocked: Dict[str, float] = {}  # aid -> unix time (해금 시간)
        self.counters: Dict[str, int] = {
            "days_survived": 0,
            "coins_total": 0,
            "items_bought": 0,
            "minigame_play_count": 0,
            "minigame_win_count": 0,
        }

        # 토스트(화면에 잠깐 뜨는 알림)
        self.toast_queue: List[Tuple[str, str, float]] = []  # (title, desc, expire_time)

        self.load()

    # ───────────── 저장/로드 ─────────────
    def load(self) -> None:
        if not self.save_path.exists():
            return
        try:
            data = json.loads(self.save_path.read_text(encoding="utf-8"))
            self.unlocked = {k: float(v) for k, v in data.get("unlocked", {}).items()}
            self.counters.update({k: int(v) for k, v in data.get("counters", {}).items()})
        except Exception:
            # 저장 파일이 깨진 경우: 그냥 초기값 유지
            pass

    def save(self) -> None:
        data = {
            "unlocked": self.unlocked,
            "counters": self.counters,
        }
        self.save_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    # ───────────── 내부 유틸 ─────────────
    def is_unlocked(self, aid: str) -> bool:
        return aid in self.unlocked

    def _unlock(self, aid: str) -> None:
        if self.is_unlocked(aid):
            return
        d = self.def_map.get(aid)
        if not d:
            return

        self.unlocked[aid] = time.time()
        # 토스트 메시지 추가
        self.toast_queue.append((f"업적 해금! {d.title}", d.desc, time.time() + 2.5))
        self.save()

    def _unlock_by_def(self, d: AchievementDef) -> None:
        self._unlock(d.aid)

    # ───────────── 외부에서 호출하는 이벤트 API ─────────────
    def on_event(self, event: str, **payload: Any) -> None:
        """
        게임 코드에서 상황별로 호출하면 됨.
        예)
          ach.on_event("day_end")
          ach.on_event("coins_earned", amount=50)
          ach.on_event("minigame_won")
          ach.on_event("evolved", stage="adult")
        """
        # once 타입 업적(이벤트 1회)
        for d in self.defs:
            if d.a_type == "once" and d.target_key == event:
                self._unlock_by_def(d)

        # 이벤트별 카운터 갱신
        if event == "day_end":
            self.counters["days_survived"] += 1

        elif event == "coins_earned":
            amt = int(payload.get("amount", 0))
            if amt > 0:
                self.counters["coins_total"] += amt

        elif event == "item_bought":
            self.counters["items_bought"] += 1

        elif event == "minigame_played":
            self.counters["minigame_play_count"] += 1

        elif event == "minigame_won":
            self.counters["minigame_win_count"] += 1

        elif event == "evolved":
            # stage 예: "adult", "lion", "dino"
            stage = str(payload.get("stage", "")).strip()
            if stage:
                # evolve 타입 업적 체크
                for d in self.defs:
                    if d.a_type == "evolve" and d.target_key == stage:
                        self._unlock_by_def(d)

        # counter 업적 체크
        self._check_counters()
        self.save()

    def check_stats_on_day_end(self, stats: Dict[str, int]) -> None:
        """
        하루 종료 직후에 한 번 호출하면 스탯 업적이 평가됨.
        stats 예:
          {"happiness": 85, "cleanliness": 92, "hunger": 20, "fatigue": 15}
        """
        h = int(stats.get("happiness", 0))
        c = int(stats.get("cleanliness", 0))
        hu = int(stats.get("hunger", 0))
        f = int(stats.get("fatigue", 0))

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

    # ───────────── UI용: 업적 목록 가져오기 ─────────────
    def get_list(self) -> List[Dict[str, Any]]:
        """
        UI에서 쓰기 좋은 형태로 반환
        """
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

    # ───────────── UI용: 토스트(팝업) 처리 ─────────────
    def pop_active_toasts(self) -> List[Tuple[str, str]]:
        """
        현재 표시할 토스트 목록(만료 전)을 반환.
        게임 루프에서 매 프레임 호출해서 draw에 사용.
        """
        now = time.time()
        self.toast_queue = [(t, d, exp) for (t, d, exp) in self.toast_queue if exp > now]
        return [(t, d) for (t, d, exp) in self.toast_queue]


# ─────────────────────────────────────────────────────────────
# (선택) 업적 화면 렌더링 헬퍼
# - 아주 단순한 리스트 화면. 너 UI 스타일에 맞게 꾸미면 됨.
# ─────────────────────────────────────────────────────────────

def draw_toasts(screen, font, ach: AchievementsManager) -> None:
    """
    화면 좌상단에 해금 토스트 표시 (2~3초)
    """
    import pygame

    toasts = ach.pop_active_toasts()
    if not toasts:
        return

    pad = 10
    x, y = 15, 15
    for title, desc in toasts[:3]:
        # 배경 박스
        w = 420
        h = 64
        box = pygame.Surface((w, h), pygame.SRCALPHA)
        box.fill((0, 0, 0, 170))  # 반투명
        screen.blit(box, (x, y))

        # 텍스트
        t_surf = font.render(title, True, (255, 255, 255))
        d_surf = font.render(desc, True, (220, 220, 220))
        screen.blit(t_surf, (x + pad, y + 8))
        screen.blit(d_surf, (x + pad, y + 34))

        y += h + 8



def draw_achievements_panel(screen, font, ach: AchievementsManager, scroll: int = 0) -> None:
    """
    업적 목록 패널(전체 화면 오버레이)
    - A 키로 열었다는 가정
    - scroll은 위/아래 스크롤 값(픽셀 단위)
    """
    import pygame

    W, H = screen.get_size()
    overlay = pygame.Surface((W, H), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    screen.blit(overlay, (0, 0))

    title = font.render("업적", True, (255, 255, 255))
    screen.blit(title, (30, 20))

    items = ach.get_list()
    y = 70 - scroll
    line_h = 56

    for it in items:
        if y < -line_h:
            y += line_h
            continue
        if y > H + line_h:
            break

        # 한 줄 박스
        box = pygame.Surface((W - 60, line_h - 8), pygame.SRCALPHA)
        if it["unlocked"]:
            box.fill((40, 120, 60, 160))
        else:
            box.fill((80, 80, 80, 120))
        screen.blit(box, (30, y))

        t = font.render(f'{it["title"]}  (+{it["points"]})', True, (255, 255, 255))
        d = font.render(it["desc"], True, (230, 230, 230))
        screen.blit(t, (45, y + 6))
        screen.blit(d, (45, y + 30))

        y += line_h

    hint = font.render("ESC: 닫기 / ↑↓: 스크롤", True, (200, 200, 200))
    screen.blit(hint, (30, H - 40))
