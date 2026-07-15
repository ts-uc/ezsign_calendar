"""EZ Sign 用カレンダーの描画処理。"""

import calendar
import datetime
from functools import partial
from pathlib import Path

from draw import Draw
from calendar_meta import (
    get_eto,
    get_jp_era,
    get_moon_phase_type,
    get_national_holiday,
    get_sekki,
    get_traditional_month,
    get_zassetsu,
    is_national_holiday,
    next_month_year,
    previous_month_year,
)

WIDTH = 400
HEIGHT = 300
CAL_W = 57
CAL_W_SATURDAY = 58
DATE_H_5W = 40
DATE_H_6W = 34
WEEKDAYS_H = 17
SUB_DATE_W = 16
SUB_DATE_H_5W = 12
SUB_DATE_H_6W = 11
BLACK = (0, 0, 0)
RED = (255, 0, 0)


def draw_header(draw: Draw, year: int, month: int) -> None:
    draw.draw_text(x=WIDTH // 2, y= 4, text=str(month), font_key=draw.FontKey.J25D, anchor="mt")
    draw.draw_dashed_line(150, 58, 250, 58)
    draw.draw_text(x=WIDTH // 2, y= 62, text=str(year), font_key=draw.FontKey.J15, anchor="mt")

def draw_weekday_cell(draw: Draw, x: int, y: int, width: int, height: int, text: str, right: bool, sunday: bool) -> None:
    draw.draw_cell_line(x=x, y=y, w=width, h=height, top=True, right=right)
    draw.draw_text(x=x + 20, y=y + 4, text=text, font_key=draw.FontKey.J10, color=RED if sunday else BLACK, anchor="mt")


def holiday_name_shift(cell_width: int, text_width: int) -> int:
    if text_width <= 29:
        return 5 + (29 - text_width + 1) // 2
    if text_width < cell_width - 10:
        return 5
    return (cell_width - text_width + 1) // 2


def draw_date_cell(draw: Draw, x: int, y: int, width: int, height: int, date: datetime.date, target_month: int, right: bool, sunday: bool = False) -> None:
    draw.draw_cell_line(x=x, y=y, w=width, h=height, top=True, right=right)
    other_month = date.month != target_month
    holiday = is_national_holiday(date)
    draw.draw_text(
        x=x + 20, y=y + 4, text=str(date.day),
        font_key=draw.FontKey.J10D if other_month else draw.FontKey.J20,
        color=RED if sunday or holiday else BLACK, hatched=other_month, anchor="mt",
    )
    if other_month:
        return

    parts = []
    holiday_name = get_national_holiday(date)
    if holiday_name:
        parts.append((holiday_name, RED))
    sekki = get_sekki(date)
    if sekki and not sekki.startswith(("春分", "秋分")):
        parts.append((sekki, BLACK))
    zassetsu = get_zassetsu(date)
    if zassetsu:
        parts.append((zassetsu, BLACK))
    draw.draw_rich_text(
        x=x, y=y + (26 if height == DATE_H_5W else 25), parts=parts,
        font_key=draw.FontKey.MISAKI, anchor="lt",
        shift_func=partial(holiday_name_shift, width) if parts else None,
    )
    moon = get_moon_phase_type(date)
    if moon is not None:
        draw.draw_moon_phase(x=x + 40, y=y + 10, w=12, h=12, phase=moon)


def draw_previous_calendar(draw: Draw, year: int, month: int) -> None:
    x = 5
    draw_sub_calendar(draw, year, month, x)


def draw_next_calendar(draw: Draw, year: int, month: int) -> None:
    x = WIDTH - SUB_DATE_W * 7 - 5 - 17
    draw_sub_calendar(draw, year, month, x)

def draw_sub_calendar(draw: Draw, year: int, month: int, x: int) -> None:
    weeks = calendar.Calendar(firstweekday=6).monthdatescalendar(year, month)
    rows = 5 if len(weeks) <= 5 else 6
    date_height = SUB_DATE_H_5W if rows == 5 else SUB_DATE_H_6W
    y = 4
    draw.draw_text(x=x + 9, y=y, text=str(month), font_key=draw.FontKey.J15, anchor="mt")
    for column, text in enumerate(("S", "M", "T", "W", "T", "F", "S")):
        draw.draw_text(x=x + 17 + column * SUB_DATE_W + SUB_DATE_W // 2, y=y, text=text, font_key=draw.FontKey.J10, color=RED if column == 0 else BLACK, anchor="mt")
    for row, dates in enumerate(weeks):
        for column, date in enumerate(dates):
            if date.month != month:
                continue
            draw.draw_text(x=x + 17  + column * SUB_DATE_W + SUB_DATE_W // 2, y=y + date_height + row * date_height, text=str(date.day), font_key=draw.FontKey.J10, color=RED if column == 0 or is_national_holiday(date) else BLACK, anchor="mt")

def draw_main_calendar(draw: Draw, year: int, month: int) -> int:
    calendar_obj = calendar.Calendar(firstweekday=6)
    weeks = calendar_obj.monthdatescalendar(year, month)
    if len(weeks) == 4:
        next_year, next_month = next_month_year(year, month)
        weeks.extend(calendar_obj.monthdatescalendar(next_year, next_month)[:1])
    date_height = DATE_H_5W if len(weeks) == 5 else DATE_H_6W
    main_height = WEEKDAYS_H + date_height * len(weeks)
    y = HEIGHT - main_height
    for column, text in enumerate(("SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT")):
        width = CAL_W_SATURDAY if column == 6 else CAL_W
        draw_weekday_cell(draw, column * CAL_W, y, width, WEEKDAYS_H, text, column != 6, column == 0)
    for row, dates in enumerate(weeks):
        for column, date in enumerate(dates):
            width = CAL_W_SATURDAY if column == 6 else CAL_W
            draw_date_cell(draw, column * CAL_W, y + WEEKDAYS_H + row * date_height, width, date_height, date, month, column != 6, column == 0)
    return main_height


def render(year: int, month: int, output: str | Path) -> Path:
    """EZ Sign 用カレンダーを1枚生成して保存する。"""
    draw = Draw(WIDTH, HEIGHT)
    draw_main_calendar(draw, year, month)
    draw_header(draw, year, month)
    previous_year, previous_month = previous_month_year(year, month)
    draw_previous_calendar(draw, previous_year, previous_month)
    next_year, next_month = next_month_year(year, month)
    draw_next_calendar(draw, next_year, next_month)
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    draw.save(str(path), scale=8)
    return path


def make_calendar(year: int, month: int, output_dir: str | Path = "calendars") -> Path:
    """従来 API 互換のラッパー。"""
    return render(year, month, Path(output_dir) / f"{year:04}_{month:02}.png")
