from PIL import Image, ImageDraw, ImageFont
import os
from enum import Enum


class Draw:
    def __init__(self, w, h):
        font_path_misaki = os.path.join(os.path.dirname(
            __file__), "fonts", "misaki_gothic_2nd.ttf")
        self.font_misaki = read_font(font_path_misaki, 8)
        font_path_j10 = os.path.join(os.path.dirname(
            __file__), "fonts", "Jersey10-Regular.ttf")
        self.font_j10 = read_font(font_path_j10, 19)
        font_path_j15 = os.path.join(os.path.dirname(
            __file__), "fonts", "Jersey15-Regular.ttf")
        self.font_j15 = read_font(font_path_j15, 27)
        font_path_j20 = os.path.join(os.path.dirname(
            __file__), "fonts", "Jersey20-Regular.ttf")
        self.font_j20 = read_font(font_path_j20, 34)
        font_path_j25 = os.path.join(os.path.dirname(
            __file__), "fonts", "Jersey25-Regular.ttf")
        self.font_j25 = read_font(font_path_j25, 41)
        self.font_j50 = read_font(font_path_j25, 82)

        # フォントキー列挙とマップ
        class FontKey(Enum):
            MISAKI = "misaki"
            J10 = "j10"
            J15 = "j15"
            J20 = "j20"
            J25 = "j25"
            J50 = "j50"

        self.FontKey = FontKey

        self.font_map = {
            FontKey.MISAKI: self.font_misaki,
            FontKey.J10: self.font_j10,
            FontKey.J15: self.font_j15,
            FontKey.J20: self.font_j20,
            FontKey.J25: self.font_j25,
            FontKey.J50: self.font_j50,
        }

        self.img = Image.new("RGB", (w, h), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.img)

    def draw_text_center(self, x: int, y: int, w: int, h: int, text: str, font_key: object | None = None, red: bool = False):
        cx = x + w // 2
        cy = y + h // 2
        self.draw_text(
            x=cx, y=cy,
            text=text, font_key=font_key, red=red
        )


    def draw_text(
        self,
        x: int,
        y: int,
        text: str,
        font_key: object | None = None,
        red: bool = False,
        anchor: str = "mm",
        hatched: bool = False,
        hatch_parity: int = 0,
    ):
        # フォント選択
        font = None

        # font_key が指定されていれば優先して選択
        if font_key is not None:
            if isinstance(font_key, str):
                k = font_key.lower()
                for fk in self.font_map:
                    if fk.value == k or fk.name.lower() == k:
                        font = self.font_map[fk]
                        break
            else:
                # Enum か既にキーオブジェクト
                try:
                    font = self.font_map[font_key]
                except Exception:
                    font = None

        # 指定がなければ既定フォントを使用 (J10)
        if font is None:
            font = self.font_j10

        color = (255, 0, 0) if red else (0, 0, 0)

        if not hatched:
            # 通常描画
            self.draw.text((x, y), text, font=font, fill=color, anchor=anchor)
            return

        # 網掛け描画: まずテキストをマスクに描画し、その領域で1pxごとの点を描く
        mask = Image.new("L", self.img.size, 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.text((x, y), text, font=font, fill=255, anchor=anchor)

        left, top, right, bottom = mask.getbbox() or (0, 0, 0, 0)
        img_pixels = self.img.load()
        mask_pixels = mask.load()

        for yy in range(top, bottom):
            for xx in range(left, right):
                if mask_pixels[xx, yy]:
                    if xx % 2 == 0 and yy % 2 == 0:
                        img_pixels[xx, yy] = color

    def _draw_dashed_line(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
    ) -> None:

        if x1 == x2:
            start, end = sorted((y1, y2))
            for pos in range(start, end):
                if (x1 % 2 == pos % 2):
                    self.draw.point((x1, pos), fill=(0, 0, 0))
        elif y1 == y2:
            start, end = sorted((x1, x2))
            for pos in range(start, end + 1):
                if (pos % 2 == y1 % 2):
                    self.draw.point((pos, y1), fill=(0, 0, 0))

    def draw_cell_line(
        self,
        x: int,
        y: int,
        w: int,
        h: int,
        top: bool = False,
        bottom: bool = False,
        left: bool = False,
        right: bool = False,
    ):
        lines = []
        if top:
            lines.append((x, y, x + w, y))
        if bottom:
            lines.append((x, y + h, x + w, y + h))
        if left:
            lines.append((x, y, x, y + h))
        if right:
            lines.append((x + w, y, x + w, y + h))

        for x1, y1, x2, y2 in lines:
            self._draw_dashed_line(x1, y1, x2, y2)


    def draw_moon_phase(self, x: int, y: int, w: int, h: int, phase: int):
        # 朔・上弦・望・下弦の4相だけを描画
        radius = min(w, h) // 2 - 2
        cx = x + w // 2
        cy = y + h // 2
        bbox = (cx - radius, cy - radius, cx + radius, cy + radius)

        if phase == 0:
            # 朔 (新月)
            self.draw.ellipse(bbox, fill=(0, 0, 0))
        elif phase == 1:
            # 上弦 (右半分が明るい)
            self.draw.ellipse(bbox, fill=(0, 0, 0))
            self.draw.pieslice(bbox, -90, 90, fill=(255, 255, 0))
        elif phase == 2:
            # 望 (満月)
            self.draw.ellipse(bbox, fill=(255, 255, 0))
        else:
            # 下弦 (左半分が明るい)
            self.draw.ellipse(bbox, fill=(0, 0, 0))
            self.draw.pieslice(bbox, 90, 270, fill=(255, 255, 0))
        self.draw.ellipse(bbox, outline=(0, 0, 0))


    def save(self, out: str):
        self.img.save(out)


def read_font(path: str, size: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(path, size)
    except (IOError, OSError):
        print(f"Warning: Failed to load font from {path}. Using default font.")
        return ImageFont.load_default()
