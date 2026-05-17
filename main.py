import calendar
import datetime
import argparse
import os

from draw import Draw
from calendar_meta import (
    get_jp_era,
    get_eto,
    get_traditional_month,
    get_moon_phase_type,
    is_holiday,
    get_holiday,
    get_rokuyou,
    get_sekki,
    next_month_year,
)

WIDTH = 400
HEIGHT = 300
HEADER_H = 90

# レイアウト定数
CAL_W = WIDTH // 7
DATE_H_5W = 40
DATE_H_6W = 34
WEEKDAYS_H = 16

# サブカレンダー定数
SUB_CAL_W = 18
SUB_DATE_H_5W = 12
SUB_DATE_H_6W = 11


def next_month_year(year: int, month: int) -> tuple[int, int]:
    nm = month + 1
    ny = year
    if nm > 12:
        nm = 1
        ny += 1
    return ny, nm


def draw_header(draw: Draw, year: int, month: int) -> None:
    # 年表示と和暦等のヘッダ描画をまとめた関数
    draw.draw_text(x=80, y=65, text=str(year), text_size=20, anchor="rb")

    d = datetime.date(year, month, 1)
    jp_era = get_jp_era(d)
    ETO = get_eto(d)
    month_name = get_traditional_month(month)

    draw.draw_text(x=80, y=75, text=f"{jp_era}年{ETO}", text_size=8, anchor="rb")
    draw.draw_text(x=120, y=75, text=str(month), text_size=50, anchor="mb")
    draw.draw_text(x=160, y=65, text=calendar.month_abbr[month].upper(), text_size=20, anchor="lb")
    draw.draw_text(x=160, y=75, text=month_name, text_size=8, anchor="lb")

def draw_weekday_cell(draw: Draw, cx: int, cy: int, cw: int, ch: int, text: str, right: bool, is_sunday: bool):
    draw.draw_cell_line(x=cx, y=cy, w=cw, h=ch, top=True, right=right)
    draw.draw_text(x=cx + 3, y=cy + 4, text=text, text_size=10, red=is_sunday, anchor="lt")


def draw_date_cell(
    draw: Draw,
    cx: int,
    cy: int,
    cw: int,
    ch: int,
    day: int,
    year: int,
    month: int,
    right: bool,
    is_sunday: bool = False,
):
    # 罫線
    draw.draw_cell_line(x=cx, y=cy, w=cw, h=ch, top=True, right=right)

    if day == 0:
        return

    d = datetime.date(year, month, day)
    holiday = is_holiday(d)
    red = is_sunday or holiday

    # 日付表示
    draw.draw_text(x=cx + 3 + 15, y=cy + 4, text=str(day), text_size=20, red=red, anchor="mt")

    # 月相
    mp = get_moon_phase_type(d)
    if mp is not None:
        draw.draw_moon_phase(x=cx + cw - 2 - 12, y=cy + ch - 2 - 12, w=12, h=12, phase=mp)

    # 六曜
    draw.draw_text(x=cx + cw - 3, y=cy + 4, text=get_rokuyou(d), text_size=8, anchor="rt")

    # 二十四節気
    jieqi = get_sekki(d)
    if jieqi:
        draw.draw_text(x=cx + cw - 3, y=cy + 4 + 10, text=jieqi, text_size=8, anchor="rt")

    # 祝日名
    holiday_name = get_holiday(d)
    if holiday_name:
        draw.draw_text(x=cx + 3, y=cy + 4 + 21, text=holiday_name, text_size=8, anchor="lt", red=True)

def draw_sub_calendar(draw: Draw, year: int, month: int, main_cal_h: int) -> None:
    cal_w = SUB_CAL_W
    x = WIDTH - cal_w * 7 - 5

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    len_weeks = 5 if len(weeks) <= 5 else 6
    date_h = SUB_DATE_H_5W if len_weeks == 5 else SUB_DATE_H_6W
    weekdays_h = date_h

    h = weekdays_h + date_h * len_weeks
    y = (HEIGHT - main_cal_h - h + 1) // 2

    # 月表示
    draw.draw_text(x=x - 3, y=y, text=str(month), text_size=15, anchor="rt")

    # 曜日部分のグリッド
    weekdays = ["S", "M", "T", "W", "T", "F", "S"]
    for c, text in enumerate(weekdays):
        draw.draw_text(x=x + c * cal_w + cal_w // 2, y=y, text=text, text_size=10, red=(c == 0), anchor="mt")

    # 日付部分のグリッド
    for r, row in enumerate(weeks):
        for c, day in enumerate(row):
            draw.draw_text(x=x + c * cal_w + cal_w // 2, y=y + weekdays_h + r * date_h, text="" if day == 0 else str(day), text_size=10, red=(c == 0), anchor="mt")


def draw_main_calendar(draw: Draw, year: int, month: int) -> int:
    cal_w = WIDTH // 7

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    len_weeks = 5 if len(weeks) <= 5 else 6
    date_h = 40 if len_weeks == 5 else 34
    weekdays_h = 16

    main_cal_h = weekdays_h + date_h * len_weeks

    y = HEIGHT - main_cal_h

    # 曜日部分のグリッド
    weekdays = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    for c, text in enumerate(weekdays):
        cx = c * cal_w
        cy = y
        cw = cal_w
        ch = weekdays_h
        draw_weekday_cell(draw, cx, cy, cw, ch, text, right=(c != 6), is_sunday=(c == 0))

    # 日付部分のグリッド
    for r, row in enumerate(weeks):
        for c, day in enumerate(row):
            cx = c * cal_w
            cy = y + weekdays_h + r * date_h
            cw = cal_w
            ch = date_h

            draw_date_cell(
                draw,
                cx,
                cy,
                cw,
                ch,
                day,
                year,
                month,
                right=(c != 6),
                is_sunday=(c == 0),
            )

    return main_cal_h


def make_calendar(year: int, month: int) -> None:
    next_year, next_month = next_month_year(year, month)

    draw = Draw(WIDTH, HEIGHT)

    # ヘッダ描画
    draw_header(draw, year, month)

    # メインカレンダー
    main_cal_h = draw_main_calendar(draw=draw, year=year, month=month)

    # サブカレンダー
    draw_sub_calendar(draw=draw, year=next_year, month=next_month, main_cal_h=main_cal_h)

    output_dir = os.path.join(os.path.dirname(__file__), "calendars")
    os.makedirs(output_dir, exist_ok=True)

    out = os.path.join(output_dir, f"{year:04}_{month:02}.png")
    draw.save(out)
    print(out)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("begin", type=int)
    p.add_argument("end", type=int)
    a = p.parse_args()

    for year in range(a.begin, a.end+1):
        for month in range(1, 13):
            make_calendar(year, month)
