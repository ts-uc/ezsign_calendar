"""テプラ用の小型カレンダー描画。"""

import calendar
import datetime
from pathlib import Path

import jpholiday
from PIL import Image, ImageDraw, ImageFont


CELL_W = 20
WIDTH = CELL_W * 7
HEIGHT = 96
HEADER_H = 12
WEEKDAYS = ("SU", "MO", "TU", "WE", "TH", "FR", "SA")


def _font() -> ImageFont.FreeTypeFont:
    path = Path(__file__).parent / "fonts" / "Jersey10-Regular.ttf"
    try:
        return ImageFont.truetype(str(path), 19)
    except (OSError, IOError):
        return ImageFont.load_default()


def _cell(draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont, *, x: int,
          y: int, width: int, height: int, text: str, reverse: bool = False) -> None:
    if reverse:
        draw.rectangle((x, y, x + width - 1, y + height - 1), fill=0)

    bbox = draw.textbbox((0, 0), text, font=font)
    tx = x + (width - (bbox[2] - bbox[0]) + 1) // 2
    ty = y - (11 - height // 2)
    draw.text((tx, ty), text, font=font, fill=1 if reverse else 0)


def render(year: int, month: int, output: str | Path) -> Path:
    """テプラ版カレンダーを1枚生成して、保存先を返す。"""
    weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
    row_height = 14 if len(weeks) <= 5 else 12
    weekdays_height = row_height

    image = Image.new("1", (WIDTH, HEIGHT), 1)
    draw = ImageDraw.Draw(image)
    font = _font()

    _cell(draw, font, x=0, y=0, width=WIDTH, height=HEADER_H,
          text=f"{year:04}-{month:02}")

    for column, weekday in enumerate(WEEKDAYS):
        _cell(draw, font, x=column * CELL_W, y=HEADER_H, width=CELL_W,
              height=weekdays_height, text=weekday, reverse=column == 0)

    for row, days in enumerate(weeks):
        for column, day in enumerate(days):
            holiday = day != 0 and jpholiday.is_holiday(
                datetime.date(year, month, day)
            )
            _cell(
                draw,
                font,
                x=column * CELL_W,
                y=HEADER_H + weekdays_height + row * row_height,
                width=CELL_W,
                height=row_height,
                text="" if day == 0 else str(day),
                reverse=column == 0 or holiday,
            )

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path)
    return path
