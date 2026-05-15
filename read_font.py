from functools import lru_cache
from pathlib import Path
from PIL import ImageFont


def find_font_path() -> str | None:
    futura_candidates = [
        # macOS
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/Library/Fonts/Futura.ttc",
        "/System/Library/Fonts/Futura.ttc",

        # Windows
        "C:/Windows/Fonts/Futura.ttc",
        "C:/Windows/Fonts/FUTURA.TTF",
        "C:/Windows/Fonts/futura medium bt.ttf",

        # GNU/Linux
        "/usr/share/fonts/truetype/futura/Futura.ttc",
        "/usr/local/share/fonts/Futura.ttc",
    ]

    for path in futura_candidates:
        if Path(path).exists():
            return path

    jost_path = Path("./fonts/Jost-VariableFont_wght.ttf")
    if jost_path.exists():
        return str(jost_path)

    return None


@lru_cache(maxsize=None)
def read_font(size: int) -> ImageFont.FreeTypeFont:
    font_path = find_font_path()

    if font_path is None:
        print("Warning: Failed to load Futura and Jost fonts. Using default font.")
        return ImageFont.load_default()

    try:
        return ImageFont.truetype(font_path, size)
    except (IOError, OSError):
        print(f"Warning: Failed to load font from {font_path}. Using default font.")
        return ImageFont.load_default()