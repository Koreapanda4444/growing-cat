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


def run_laser_chase(screen: pygame.Surface, ach=None) -> dict:
    if not pygame.font.get_init():
        pygame.font.init()

    clock = pygame.time.Clock()
    W, H = screen.get_size()
    font_hud = _get_font(_clamp_int(H * 0.030, 14, 18))
    font_tip = _get_font(_clamp_int(H * 0.032, 14, 19))
    font_big = _get_font(_clamp_int(H * 0.060, 22, 34))
    font_result = _get_font(_clamp_int(H * 0.038, 16, 22))

    TIME_LIMIT = 32.0

    TARGET_SCORE = 480

    BASE_RADIUS = 30
    MIN_RADIUS = 18

    BASE_SPEED = 320.0
    MAX_SPEED = 720.0

    COMBO_GRACE = 1.5

    MISS_PENALTY = 4

    def coins_from(score_val: int, won_flag: bool) -> int:
        base = max(8, score_val // 45)
        if won_flag:
            base += 25
        return base

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
    result_event_sent = False

    particles = []

    def spawn_hit_particles(px, py, n=10):
        for _ in range(n):
            a = random.uniform(0, math.tau)
            s = random.uniform(140.0, 360.0)
            particles.append([px, py, math.cos(a) * s, math.sin(a) * s, random.uniform(0.25, 0.45)])

    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        W, H = screen.get_size()
        font_hud = _get_font(_clamp_int(H * 0.030, 14, 18))
        font_tip = _get_font(_clamp_int(H * 0.032, 14, 19))
        font_big = _get_font(_clamp_int(H * 0.060, 22, 34))
        font_result = _get_font(_clamp_int(H * 0.038, 16, 22))

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

                        spawn_hit_particles(x, y, n=12)

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

            for p in particles:
                p[0] += p[2] * dt
                p[1] += p[3] * dt
                p[4] -= dt
            particles[:] = [p for p in particles if p[4] > 0]

        if phase == "RESULT" and (not result_event_sent):
            result_event_sent = True

        screen.fill((18, 18, 22))

        hud1 = font_hud.render(f"SCORE {score}/{TARGET_SCORE}", True, (230, 230, 230))
        hud2 = font_hud.render(f"TIME {time_left:0.1f}s   COMBO x{best_combo}", True, (230, 230, 230))
        screen.blit(hud1, (16, 12))
        screen.blit(hud2, (16, 12 + hud1.get_height() + 4))

        for px, py, _, __, life in particles:
            a = max(0, min(255, int(255 * (life / 0.45))))
            pygame.draw.circle(screen, (255, 220, 220, a), (int(px), int(py)), 3)

        pygame.draw.circle(screen, (255, 60, 60), (int(x), int(y)), int(radius))
        pygame.draw.circle(screen, (0, 0, 0), (int(x), int(y)), int(radius), 2)
        pygame.draw.circle(screen, (255, 200, 200), (int(x), int(y)), max(3, int(radius * 0.22)))

        if toast_timer > 0 and toast_text:
            t = font_hud.render(toast_text, True, (255, 255, 255))
            bg = pygame.Surface((t.get_width() + 18, t.get_height() + 12), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 160))
            bg.blit(t, (9, 6))
            screen.blit(bg, (20, H - bg.get_height() - 20))

        if phase == "RESULT":
            overlay = pygame.Surface((W, H), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            msg = "성공!" if won else "실패!"
            m = font_big.render(msg, True, (255, 255, 255))
            screen.blit(m, m.get_rect(center=(W // 2, int(H * 0.45))))

            coins = coins_from(score, won)
            sub = font_result.render(f"SCORE {score}  /  COINS +{coins}", True, (230, 230, 230))
            screen.blit(sub, sub.get_rect(center=(W // 2, int(H * 0.55))))

            hint = font_result.render("ENTER를 누르면 돌아갑니다", True, (210, 210, 210))
            screen.blit(hint, hint.get_rect(center=(W // 2, int(H * 0.66))))

        pygame.display.flip()

    coins = coins_from(score, won)
    return {"won": won, "score": score, "coins": coins}
