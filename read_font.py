from pathlib import Path
from PIL import ImageFont


def read_font(size: int) -> ImageFont.FreeTypeFont:
    """
    優先順位:
    1. Futura Medium 系フォント (macOS / Windows)
    2. ./fonts/Jost-VariableFont_wght.ttf
    3. PIL default font
    """

    futura_candidates = [
        # macOS
        "/System/Library/Fonts/Supplemental/Futura.ttc",
        "/Library/Fonts/Futura.ttc",
        "/System/Library/Fonts/Futura.ttc",

        # Windows
        "C:/Windows/Fonts/Futura.ttc",
        "C:/Windows/Fonts/FUTURA.TTF",
        "C:/Windows/Fonts/futura medium bt.ttf",

        # Linux (もし手動導入されている場合)
        "/usr/share/fonts/truetype/futura/Futura.ttc",
        "/usr/local/share/fonts/Futura.ttc",
    ]

    # Futura を優先
    for path in futura_candidates:
        try:
            if Path(path).exists():
                return ImageFont.truetype(path, size)
        except (IOError, OSError):
            pass

    # fallback: local Jost Variable Font
    jost_path = Path("./fonts/Jost-VariableFont_wght.ttf")

    if jost_path.exists():
        try:
            return ImageFont.truetype(str(jost_path), size)
        except (IOError, OSError):
            pass

    print("Warning: Failed to load Futura and Jost fonts. Using default font.")
    return ImageFont.load_default()