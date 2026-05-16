from PIL import Image, ImageDraw
import read_font


class Draw:
    def __init__(self, w, h):
        self.img = Image.new("RGB", (w, h), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.img)

    def draw_cell(self, x: int, y: int, w: int, h: int, text: str, text_size: int, red: bool = False):
        font = read_font.read_font(text_size)

        # セルの中央座標
        cx = x + w // 2
        cy = y + h // 2

        # anchor="mm" で見えているサイズの中央に配置
        self.draw.text(
            (cx, cy),
            text,
            font=font,
            fill=(255, 0, 0) if red else (0, 0, 0),
            anchor="mm"
        )

    def save(self, out: str):
        self.img.save(out)
