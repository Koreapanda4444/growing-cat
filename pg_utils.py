from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Tuple

import pygame


Size = Tuple[int, int]


def load_font(font_path: Optional[str], size: int) -> pygame.font.Font:
    try:
        if font_path:
            return pygame.font.Font(font_path, int(size))
    except Exception:
        pass
    return pygame.font.Font(None, int(size))


def load_image(path: str, *, size: Optional[Size] = None, smooth: bool = True, alpha: bool = True) -> Optional[pygame.Surface]:
    try:
        surf = pygame.image.load(path)
        surf = surf.convert_alpha() if alpha else surf.convert()
        if size is not None:
            surf = pygame.transform.smoothscale(surf, size) if smooth else pygame.transform.scale(surf, size)
        return surf
    except Exception:
        return None


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
    except Exception:
        return None


def play_music(path: str, *, volume: Optional[float] = None, loops: int = -1) -> bool:
    try:
        pygame.mixer.music.load(path)
        if volume is not None:
            pygame.mixer.music.set_volume(float(volume))
        pygame.mixer.music.play(loops)
        return True
    except Exception:
        return False
