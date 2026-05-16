from PIL import Image, ImageDraw
import read_font


class Draw:
    def __init__(self, w, h):
        self.img = Image.new("RGB", (w, h), (255, 255, 255))
        self.draw = ImageDraw.Draw(self.img)

    def draw_text(self, x: int, y: int, w: int, h: int, text: str, text_size: int, red: bool = False):
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
                if(x1 % 2 == pos % 2):
                    self.draw.point((x1, pos), fill=(0, 0, 0))
        elif y1 == y2:
            start, end = sorted((x1, x2))
            for pos in range(start, end + 1):
                if(pos % 2 == y1 % 2):
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

    def save(self, out: str):
        self.img.save(out)
