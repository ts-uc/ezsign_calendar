from PIL import Image, ImageDraw
import read_font


class Draw:
    def __init__(self, w, h):
        self.img = Image.new("RGB", (w, h), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.img)

    def draw_cell(self, x: int, y: int, w: int, h: int, text: str, text_size: int, red: bool = False):
        font = read_font.read_font(text_size)

        bbox = self.draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        tx = x + (w - text_w) // 2 - bbox[0]
        ty = y + (h - text_h) // 2 - bbox[1]

        self.draw.text(
            (tx, ty),
            text,
            font=font,
            fill=(255, 0, 0) if red else (0, 0, 0)
        )

    def save(self, out: str):
        self.img.save(out)
