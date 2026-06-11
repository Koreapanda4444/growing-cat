import random
import math
import pygame


def _get_font(size: int) -> pygame.font.Font:
    for name in ("malgungothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"):
        f = pygame.font.SysFont(name, size)
        if f:
            return f
    return pygame.font.SysFont(None, size)


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


def _draw_result(screen, fonts, screen_w, screen_h, won, score):
    overlay = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    msg = "성공!" if won else "실패!"
    title = fonts["big"].render(msg, True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen_w // 2, int(screen_h * 0.45))))

    coins = _coins_from_score(score, won)
    score_text = fonts["result"].render(f"SCORE {score}  /  COINS +{coins}", True, (230, 230, 230))
    screen.blit(score_text, score_text.get_rect(center=(screen_w // 2, int(screen_h * 0.55))))

    hint = fonts["result"].render("ENTER를 누르면 돌아갑니다", True, (210, 210, 210))
    screen.blit(hint, hint.get_rect(center=(screen_w // 2, int(screen_h * 0.66))))


def run_laser_chase(screen: pygame.Surface, ach=None) -> dict:
    if not pygame.font.get_init():
        pygame.font.init()

    clock = pygame.time.Clock()
    W, H = screen.get_size()
    fonts = _get_laser_fonts(H)

    TIME_LIMIT = 32.0

    TARGET_SCORE = 480

    BASE_RADIUS = 30
    MIN_RADIUS = 18

    BASE_SPEED = 320.0
    MAX_SPEED = 720.0

    COMBO_GRACE = 1.5

    MISS_PENALTY = 4

    x = random.uniform(W * 0.25, W * 0.75)
    y = random.uniform(H * 0.30, H * 0.70)

    angle = random.uniform(0, math.tau)
    vx = math.cos(angle) * BASE_SPEED
    vy = math.sin(angle) * BASE_SPEED

    radius = BASE_RADIUS

    score = 0
    combo = 0
    best_combo = 0
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
        fonts = _get_laser_fonts(H)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return {"won": False, "score": score, "coins": 0}

            if phase == "RESULT":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    running = False
                continue

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                phase = "RESULT"
                won = False

            if phase == "PLAY":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos
                    dx = mx - x
                    dy = my - y
                    hit = (dx * dx + dy * dy) <= (radius * radius)

                    if hit:
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
                        if MISS_PENALTY > 0:
                            score = max(0, score - MISS_PENALTY)
                        combo_timer = 0.0
                        combo = 0
                        toast_text = f"-{MISS_PENALTY} (미스)"
                        toast_timer = 0.55

        if phase == "PLAY":
            time_left -= dt
            if time_left <= 0:
                time_left = 0
                phase = "RESULT"
                won = score >= TARGET_SCORE

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

            if y - radius < 0:
                y = radius
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
        _draw_particles(screen, particles)
        _draw_target(screen, x, y, radius)
        if toast_timer > 0 and toast_text:
            _draw_toast(screen, fonts["hud"], toast_text, H)

        if phase == "RESULT":
            _draw_result(screen, fonts, W, H, won, score)

        pygame.display.flip()

    coins = _coins_from_score(score, won)
    return {"won": won, "score": score, "coins": coins}
