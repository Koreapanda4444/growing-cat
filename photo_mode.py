import os
import datetime
import pygame


def _font(size: int) -> pygame.font.Font:
    for name in ("malgungothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"):
        f = pygame.font.SysFont(name, size)
        if f:
            return f
    return pygame.font.SysFont(None, size)


def take_photo(
    surface: pygame.Surface,
    *,
    player_name: str = "player",
    day: int | None = None,
    stage: str | None = None,
    folder: str = "screenshots",
) -> str:
    os.makedirs(folder, exist_ok=True)

    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = "".join(ch for ch in player_name if ch.isalnum() or ch in ("_", "-")) or "player"

    parts = [safe_name]
    if day is not None:
        parts.append(f"day{day}")
    parts.append(ts)
    filename = "_".join(parts) + ".png"
    path = os.path.join(folder, filename)

    shot = surface.copy()

    text_parts = [safe_name]
    if day is not None:
        text_parts.append(f"Day {day}")
    if stage:
        text_parts.append(f"Stage {stage}")
    text_parts.append(ts)
    text = " | ".join(text_parts)

    font = _font(18)
    pad = 10
    label = font.render(text, True, (255, 255, 255))
    bg = pygame.Surface((label.get_width() + pad * 2, label.get_height() + pad * 2), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 160))
    bg.blit(label, (pad, pad))

    shot.blit(bg, (12, shot.get_height() - bg.get_height() - 12))

    pygame.image.save(shot, path)
    return path
