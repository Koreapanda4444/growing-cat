import random
import math
import pygame

from config import asset_path
from pg_utils import screen_events, load_font
import state as game_state


def _get_font(size: int) -> pygame.font.Font:
    return load_font(asset_path("fonts", "ThinDungGeunMo.ttf"), size)


def _clamp_int(v: float, lo: int, hi: int) -> int:
    return int(max(lo, min(hi, int(v))))


def _get_laser_fonts(height: int):
    return {
        "hud": _get_font(_clamp_int(height * 0.030, 14, 18)),
        "big": _get_font(_clamp_int(height * 0.060, 22, 34)),
        "result": _get_font(_clamp_int(height * 0.038, 16, 22)),
    }


def _coins_from_score(score_val: int, won_flag: bool) -> int:
    base = max(8, score_val // 45)
    if won_flag:
        base += 25
    return base


def _laser_settings(difficulty: str | None = "normal") -> dict:
    profile = game_state.get_minigame_profile(difficulty, "laser")
    return {
        "time_limit": float(profile["time_limit"]),
        "target_score": int(profile["target_score"]),
        "base_radius": int(profile["base_radius"]),
        "min_radius": int(profile["min_radius"]),
        "base_speed": float(profile["base_speed"]),
        "max_speed": float(profile["max_speed"]),
        "combo_grace": float(profile["combo_grace"]),
        "miss_penalty": int(profile["miss_penalty"]),
    }


def _spawn_hit_particles(particles, px, py, n=10):
    for _ in range(n):
        angle = random.uniform(0, math.tau)
        speed = random.uniform(140.0, 360.0)
        particles.append([
            px,
            py,
            math.cos(angle) * speed,
            math.sin(angle) * speed,
            random.uniform(0.25, 0.45),
        ])


def _update_particles(particles, dt: float):
    for particle in particles:
        particle[0] += particle[2] * dt
        particle[1] += particle[3] * dt
        particle[4] -= dt
    particles[:] = [particle for particle in particles if particle[4] > 0]


def _draw_hud(screen, font, score, target_score, time_left, best_combo):
    hud1 = font.render(f"SCORE {score}/{target_score}", True, (230, 230, 230))
    hud2 = font.render(f"TIME {time_left:0.1f}s   COMBO x{best_combo}", True, (230, 230, 230))
    screen.blit(hud1, (16, 12))
    screen.blit(hud2, (16, 12 + hud1.get_height() + 4))


def _draw_particles(screen, particles):
    for px, py, _, __, life in particles:
        alpha = max(0, min(255, int(255 * (life / 0.45))))
        pygame.draw.circle(screen, (255, 220, 220, alpha), (int(px), int(py)), 3)


def _draw_target(screen, x, y, radius):
    pygame.draw.circle(screen, (255, 60, 60), (int(x), int(y)), int(radius))
    pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), int(radius), 2)
    pygame.draw.circle(screen, (255, 200, 200), (int(x), int(y)), max(3, int(radius * 0.22)))


def _draw_toast(screen, font, text, screen_h):
    label = font.render(text, True, (255, 255, 255))
    bg = pygame.Surface((label.get_width() + 18, label.get_height() + 12), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 160))
    bg.blit(label, (9, 6))
    screen.blit(bg, (20, screen_h - bg.get_height() - 20))


def _draw_result(screen, fonts, screen_w, screen_h, won, score, best_combo=0, hits=0, misses=0, challenge=False):
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    msg = "성공!" if won else "실패!"
    title = fonts["big"].render(msg, True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen_w // 2, int(screen_h * 0.45))))

    coins = min(85, _coins_from_score(score, won) + (10 if won else 0)) if challenge else _coins_from_score(score, won)
    score_text = fonts["result"].render(f"SCORE {score}  /  COINS +{coins}", True, (230, 230, 230))
    screen.blit(score_text, score_text.get_rect(center=(screen_w // 2, int(screen_h * 0.55))))

    accuracy = hits * 100 // (hits + misses) if hits + misses else 0
    details = fonts["hud"].render(f"최고 콤보 {best_combo} / 정확도 {accuracy}% / 적중 {hits}", True, (230, 230, 230))
    screen.blit(details, details.get_rect(center=(screen_w // 2, int(screen_h * 0.61))))

    hint = fonts["result"].render("ENTER를 누르면 돌아갑니다", True, (210, 210, 210))
    screen.blit(hint, hint.get_rect(center=(screen_w // 2, int(screen_h * 0.66))))


def challenge_goals(difficulty):
    level = game_state.normalize_difficulty(difficulty)
    return {"easy": {"combo": 5, "accuracy": 65, "hits": 8},
            "normal": {"combo": 7, "accuracy": 75, "hits": 10},
            "hard": {"combo": 9, "accuracy": 85, "hits": 12}}[level]


def challenge_achieved(score, target_score, best_combo, hits, misses, goals):
    return (score >= target_score and best_combo >= goals["combo"] and hits >= goals["hits"]
            and hits * 100 >= goals["accuracy"] * (hits + misses))


def _build_result(won, score, best_combo, hits, misses, *, cancelled=False, quit_requested=False, challenge=False):
    coins = _coins_from_score(score, won)
    if challenge:
        coins = min(85, coins + (10 if won else 0))
    return {"won": won and not cancelled, "score": score, "best_combo": best_combo,
            "mode": "challenge" if challenge else "normal", "challenge_won": challenge and won and not cancelled,
            "hits": hits, "misses": misses, "accuracy": hits * 100 // (hits + misses) if hits + misses else 0,
            "coins": 0 if cancelled else coins,
            "cancelled": cancelled, "quit_requested": quit_requested}


def run_laser_chase(screen: pygame.Surface, ach=None, difficulty: str | None = "normal", challenge=False) -> dict:
    if not pygame.font.get_init():
        pygame.font.init()

    clock = pygame.time.Clock()
    W, H = screen.get_size()
    fonts = _get_laser_fonts(H)
    settings = _laser_settings(difficulty)
    font_height = H
    goals = challenge_goals(difficulty)

    TIME_LIMIT = settings["time_limit"]

    TARGET_SCORE = round(settings["target_score"] * (1.1 if challenge else 1.0))

    BASE_RADIUS = settings["base_radius"]
    MIN_RADIUS = settings["min_radius"]

    BASE_SPEED = settings["base_speed"] * (1.08 if challenge else 1.0)
    MAX_SPEED = settings["max_speed"]

    COMBO_GRACE = settings["combo_grace"]

    MISS_PENALTY = settings["miss_penalty"]

    x = random.uniform(W * 0.25, W * 0.75)
    y = random.uniform(H * 0.30, H * 0.70)

    angle = random.uniform(0, math.tau)
    vx = math.cos(angle) * BASE_SPEED
    vy = math.sin(angle) * BASE_SPEED

    radius = BASE_RADIUS

    score = 0
    combo = 0
    best_combo = 0
    hits = 0
    misses = 0
    time_left = TIME_LIMIT

    combo_timer = 0.0

    toast_text = ""
    toast_timer = 0.0

    phase = "PLAY"
    won = False

    particles = []

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        W, H = screen.get_size()
        if H != font_height:
            fonts = _get_laser_fonts(H)
            font_height = H

        for event in screen_events():
            if event.type == pygame.QUIT:
                return _build_result(won, score, best_combo, hits, misses, cancelled=phase != "RESULT", quit_requested=True, challenge=challenge)

            if phase == "RESULT":
                if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_ESCAPE):
                    running = False
                    break
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return _build_result(False, score, best_combo, hits, misses, cancelled=True, challenge=challenge)

            if phase == "PLAY":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    dx = mx - x
                    dy = my - y
                    hit = (dx * dx + dy * dy) <= (radius * radius)

                    if hit:
                        hits += 1
                        if combo_timer > 0:
                            combo += 1
                        else:
                            combo = 1
                        best_combo = max(best_combo, combo)
                        combo_timer = COMBO_GRACE

                        dist = math.sqrt(dx * dx + dy * dy)
                        accuracy = max(0.0, 1.0 - (dist / max(1.0, radius)))
                        gained = 34 + int(combo * 5) + int(accuracy * 16)
                        score += gained

                        toast_text = f"+{gained}  (콤보 x{combo})"
                        toast_timer = 0.8

                        _spawn_hit_particles(particles, x, y, n=12)

                        speed = math.hypot(vx, vy)
                        speed = min(MAX_SPEED, speed + 35.0)
                        if combo >= 2:
                            radius = max(MIN_RADIUS, radius - 1)

                        jitter = random.uniform(-0.25, 0.25)
                        ang = math.atan2(vy, vx) + jitter
                        vx = math.cos(ang) * speed
                        vy = math.sin(ang) * speed

                    else:
                        misses += 1
                        if MISS_PENALTY > 0:
                            score = max(0, score - MISS_PENALTY)
                        combo_timer = 0.0
                        combo = 0
                        toast_text = f"-{MISS_PENALTY} (미스)"
                        toast_timer = 0.55

        if not running:
            break

        if phase == "PLAY":
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                phase = "RESULT"
                won = challenge_achieved(score, TARGET_SCORE, best_combo, hits, misses, goals) if challenge else score >= TARGET_SCORE

            if combo_timer > 0:
                combo_timer -= dt
                if combo_timer <= 0:
                    combo_timer = 0
                    combo = 0

            x += vx * dt
            y += vy * dt

            if x - radius < 0:
                x = radius
                vx = abs(vx)
            elif x + radius > W:
                x = W - radius
                vx = -abs(vx)

            top = 110 if challenge else 0
            if y - radius < top:
                y = top + radius
                vy = abs(vy)
            elif y + radius > H:
                y = H - radius
                vy = -abs(vy)

            if toast_timer > 0:
                toast_timer -= dt
                if toast_timer <= 0:
                    toast_timer = 0
                    toast_text = ""

            _update_particles(particles, dt)

        screen.fill((18, 18, 22))
        _draw_hud(screen, fonts["hud"], score, TARGET_SCORE, time_left, best_combo)
        accuracy_pct = hits * 100 // (hits + misses) if hits + misses else 0
        detail = f"적중 {hits} / 미스 {misses} / 정확도 {accuracy_pct}%"
        screen.blit(fonts["hud"].render(detail, True, (225, 225, 225)), (16, 62))
        if challenge:
            text = f"도전: 콤보 {goals['combo']} / 적중 {goals['hits']} / 정확도 {goals['accuracy']}%"
            screen.blit(fonts["hud"].render(text, True, (240, 210, 150)), (16, 85))
        _draw_particles(screen, particles)
        _draw_target(screen, x, y, radius)
        if toast_timer > 0 and toast_text:
            _draw_toast(screen, fonts["hud"], toast_text, H)

        if phase == "RESULT":
            _draw_result(screen, fonts, W, H, won, score, best_combo, hits, misses, challenge)

        pygame.display.flip()

    return _build_result(won, score, best_combo, hits, misses, challenge=challenge)
