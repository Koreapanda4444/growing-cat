import os
import sys


def base_path() -> str:
	return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def asset_path(*parts: str) -> str:
	return os.path.join(base_path(), "assets", *parts)

