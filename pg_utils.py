from __future__ import annotations

from typing import Optional, Tuple
from functools import lru_cache
import os

import pygame


class GameQuit(Exception):
    pass


def screen_events():
    events = pygame.event.get()
    quit_events = [event for event in events if event.type == pygame.QUIT]
    return quit_events[:1] or events


Size = Tuple[int, int]


def load_font(font_path: Optional[str], size: int) -> pygame.font.Font:
    try:
        if font_path:
            return pygame.font.Font(font_path, int(size))
    except (OSError, TypeError, ValueError, pygame.error):
        pass
    return pygame.font.Font(None, int(size))


def load_image(
    path: str,
    *,
    size: Optional[Size] = None,
    smooth: bool = True,
    alpha: bool = True,
) -> Optional[pygame.Surface]:
    try:
        surf = pygame.image.load(path)
        surf = surf.convert_alpha() if alpha else surf.convert()
        if size is not None:
            surf = pygame.transform.smoothscale(surf, size) if smooth else pygame.transform.scale(surf, size)
        return surf
    except (OSError, TypeError, ValueError, pygame.error):
        return None


@lru_cache(maxsize=64)
def _cached_image(path, size, smooth, alpha, display_format):
    return load_image(path, size=size, smooth=smooth, alpha=alpha)


def cached_image(path, *, size=None, smooth=True, alpha=True):
    """정적 에셋을 공유합니다. Surface를 수정할 때는 copy()를 사용하세요."""
    display = pygame.display.get_surface()
    display_format = (display.get_bitsize(), display.get_masks()) if display is not None else None
    return _cached_image(os.path.abspath(path), tuple(size) if size is not None else None,
                         smooth, alpha, display_format)


def clear_image_cache():
    _cached_image.cache_clear()


def solid_surface(size: Size, color: Tuple[int, int, int], *, alpha: bool = False) -> pygame.Surface:
    flags = pygame.SRCALPHA if alpha else 0
    surf = pygame.Surface(size, flags)
    surf.fill(color)
    return surf


def load_sound(path: str, *, volume: Optional[float] = None) -> Optional[pygame.mixer.Sound]:
    try:
        s = pygame.mixer.Sound(path)
        if volume is not None:
            s.set_volume(float(volume))
        return s
    except (OSError, TypeError, ValueError, pygame.error):
        return None


def play_music(path: str, *, volume: Optional[float] = None, loops: int = -1) -> bool:
    try:
        pygame.mixer.music.load(path)
        if volume is not None:
            pygame.mixer.music.set_volume(float(volume))
        pygame.mixer.music.play(loops)
        return True
    except (OSError, TypeError, ValueError, pygame.error):
        return False
