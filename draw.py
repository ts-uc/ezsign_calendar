from PIL import Image, ImageDraw
import read_font


class Draw:
    def __init__(self, w, h):
        self.img = Image.new("1", (w, h), 1)
        self.draw = ImageDraw.Draw(self.img)

    def draw_cell(self, x: int, y: int, w: int, h: int, text: str, text_size: int, reverse: bool = False):
        font = read_font.read_font(text_size)
        if reverse:
            self.draw.rectangle(
                (x, y, x + w - 1, y + h - 1),
                fill=0
            )
        bbox = self.draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        tx = x + (w - text_w) // 2 - bbox[0]
        ty = y + (h - text_h) // 2 - bbox[1]

        self.draw.text(
            (tx, ty),
            text,
            font=font,
            fill=1 if reverse else 0
        )

    def save(self, out: str):
        self.img.save(out)
