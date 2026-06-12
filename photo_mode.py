import os
import datetime
from pathlib import Path
import pygame

PHOTO_EXTENSIONS = {".png", ".jpg", ".jpeg"}
_DATA_DIR = Path(os.getenv("APPDATA") or str(Path.home())) / "growing-cat"
_ALBUM_DIR = _DATA_DIR / "album"


def _font(size: int) -> pygame.font.Font:
    for name in ("malgungothic", "AppleGothic", "NanumGothic", "Noto Sans CJK KR"):
        f = pygame.font.SysFont(name, size)
        if f:
            return f
    return pygame.font.SysFont(None, size)


def _render_fit_text(text: str, color, max_width: int) -> pygame.Surface:
    for size in range(18, 11, -1):
        font = _font(size)
        label = font.render(text, True, color)
        if label.get_width() <= max_width:
            return label

    font = _font(12)
    clipped = str(text)
    while len(clipped) > 3:
        clipped = clipped[:-1]
        label = font.render(clipped + "...", True, color)
        if label.get_width() <= max_width:
            return label
    return font.render("...", True, color)


def album_folder() -> str:
    return str(_ALBUM_DIR)


def list_photos(folder: str | os.PathLike | None = None) -> list[str]:
    target = Path(folder) if folder is not None else _ALBUM_DIR
    if not target.exists() or not target.is_dir():
        return []

    photos = [
        path
        for path in target.iterdir()
        if path.is_file() and path.suffix.lower() in PHOTO_EXTENSIONS
    ]
    photos.sort(key=lambda path: (path.stat().st_mtime, path.name), reverse=True)
    return [str(path) for path in photos]


def take_photo(
    surface: pygame.Surface,
    *,
    player_name: str = "player",
    day: int | None = None,
    stage: str | None = None,
    folder: str | os.PathLike | None = None,
) -> str:
    target = Path(folder) if folder is not None else _ALBUM_DIR
    target.mkdir(parents=True, exist_ok=True)

    now = datetime.datetime.now()
    file_ts = now.strftime("%Y%m%d_%H%M%S_%f")[:-3]
    label_ts = now.strftime("%Y-%m-%d %H:%M:%S")
    safe_name = "".join(ch for ch in player_name if ch.isalnum() or ch in ("_", "-")) or "player"

    parts = [safe_name]
    if day is not None:
        parts.append(f"day{day}")
    parts.append(file_ts)
    filename = "_".join(parts) + ".png"
    path = target / filename

    shot = surface.copy()

    text_parts = [safe_name]
    if day is not None:
        text_parts.append(f"Day {day}")
    if stage:
        text_parts.append(f"Stage {stage}")
    text_parts.append(label_ts)
    text = " | ".join(text_parts)

    pad = 10
    max_label_w = max(40, shot.get_width() - 24 - pad * 2)
    label = _render_fit_text(text, (255, 255, 255), max_label_w)
    bg = pygame.Surface((label.get_width() + pad * 2, label.get_height() + pad * 2), pygame.SRCALPHA)
    bg.fill((0, 0, 0, 160))
    bg.blit(label, (pad, pad))

    shot.blit(bg, (12, shot.get_height() - bg.get_height() - 12))

    pygame.image.save(shot, str(path))
    return str(path)
