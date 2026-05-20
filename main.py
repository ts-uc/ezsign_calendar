import calendar
import datetime
import argparse
import os

from draw import Draw
from calendar_meta import (
    get_jp_era,
    get_eto,
    get_traditional_month,
    is_national_holiday,
    next_month_year,
)

WIDTH = 400
HEIGHT = 300

# レイアウト定数
CAL_W = 57
CAL_W_SATURDAY = 58
DATE_H_5W = 40
DATE_H_6W = 34
WEEKDAYS_H = 17

# サブカレンダー定数
SUB_CAL_W = 18
SUB_DATE_H_5W = 12
SUB_DATE_H_6W = 11

# 色
BLACK = (0, 0, 0)
RED = (255, 0, 0)


def next_month_year(year: int, month: int) -> tuple[int, int]:
    nm = month + 1
    ny = year
    if nm > 12:
        nm = 1
        ny += 1
    return ny, nm


def draw_header(draw: Draw, year: int, month: int, main_cal_h: int) -> None:
    # 年表示と和暦等のヘッダ描画をまとめた関数
    header_h = HEIGHT - main_cal_h
    d = datetime.date(year, month, 1)
    jp_era = get_jp_era(d)
    eto = get_eto(d)
    month_name = get_traditional_month(month)

    draw.draw_text(x=80, y= header_h // 2, text=str(year), font_key=draw.FontKey.J20, anchor="rm")
    draw.draw_text(x=80, y= header_h // 2 + 16, text=f"{jp_era}年{eto}", font_key=draw.FontKey.MISAKI, anchor="rm")

    draw.draw_text(x=120, y= header_h // 2, text=str(month), font_key=draw.FontKey.J25D, anchor="mm")

    draw.draw_text(x=160, y= header_h // 2, text=calendar.month_abbr[month].upper(), font_key=draw.FontKey.J20, anchor="lm")
    draw.draw_text(x=160, y= header_h // 2 + 16, text=month_name, font_key=draw.FontKey.MISAKI, anchor="lm")


def draw_weekday_cell(draw: Draw, cx: int, cy: int, cw: int, ch: int, text: str, right: bool, is_sunday: bool):
    draw.draw_cell_line(x=cx, y=cy, w=cw, h=ch, top=True, right=right)
    draw.draw_text(x=cx + 20, y=cy + 4, text=text, font_key=draw.FontKey.J10, color=RED if is_sunday else BLACK, anchor="mt")


def draw_date_cell(
    draw: Draw,
    cx: int,
    cy: int,
    cw: int,
    ch: int,
    date_obj: datetime.date,
    target_month: int,
    right: bool,
    is_sunday: bool = False,
):
    # 罫線
    draw.draw_cell_line(x=cx, y=cy, w=cw, h=ch, top=True, right=right)

    # 隣接月の日付は薄く表示するため、チェック
    is_other_month = date_obj.month != target_month

    day = date_obj.day

    national_holiday = is_national_holiday(date_obj)
    red = is_sunday or national_holiday

    # 日付表示
    draw.draw_text(x=cx + 20, y=cy + 4, text=str(day), font_key=draw.FontKey.J10D if is_other_month else draw.FontKey.J20, color=RED if red else BLACK, hatched=is_other_month, anchor="mt")

    if is_other_month:
        return

def draw_sub_calendar(draw: Draw, year: int, month: int, main_cal_h: int) -> None:
    cal_w = SUB_CAL_W
    x = WIDTH - cal_w * 7 - 5

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)
    len_weeks = 5 if len(weeks) <= 5 else 6
    date_h = SUB_DATE_H_5W if len_weeks == 5 else SUB_DATE_H_6W
    weekdays_h = date_h

    h = weekdays_h + date_h * len_weeks
    y = (HEIGHT - main_cal_h - h + 1) // 2

    # 月表示
    draw.draw_text(x=x - 3, y=y, text=str(month), font_key=draw.FontKey.J15, anchor="rt")

    # 曜日部分のグリッド
    weekdays = ["S", "M", "T", "W", "T", "F", "S"]
    for c, text in enumerate(weekdays):
        draw.draw_text(x=x + c * cal_w + cal_w // 2, y=y, text=text, font_key=draw.FontKey.J10, color=RED if (c == 0) else BLACK, anchor="mt")

    # 日付部分のグリッド
    for r, row in enumerate(weeks):
        for c, date_obj in enumerate(row):
            # 隣接月の日付のみ表示
            if date_obj.month != month:
                continue
            day_text = str(date_obj.day)

            is_sunday = (c == 0)
            holiday = is_national_holiday(date_obj)
            red = is_sunday or holiday

            draw.draw_text(x=x + c * cal_w + cal_w // 2, y=y + weekdays_h + r * date_h, text=day_text, font_key=draw.FontKey.J10, color=RED if red else BLACK, anchor="mt")


def draw_main_calendar(draw: Draw, year: int, month: int) -> int:
    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdatescalendar(year, month)
    
    # 4週の場合、次の月の最初の週を追加して5週にする
    if len(weeks) == 4:
        next_year, next_month = next_month_year(year, month)
        next_weeks = cal.monthdatescalendar(next_year, next_month)
        if next_weeks:
            weeks.append(next_weeks[0])
    
    len_weeks = len(weeks)
    date_h = DATE_H_5W if len_weeks == 5 else DATE_H_6W
    weekdays_h = WEEKDAYS_H

    main_cal_h = weekdays_h + date_h * len_weeks

    y = HEIGHT - main_cal_h

    # 曜日部分のグリッド
    weekdays = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    for c, text in enumerate(weekdays):
        cx = c * CAL_W
        cy = y
        cw = CAL_W_SATURDAY if c == 6 else CAL_W
        ch = weekdays_h
        draw_weekday_cell(draw, cx, cy, cw, ch, text, right=(c != 6), is_sunday=(c == 0))

    # 日付部分のグリッド
    for r, row in enumerate(weeks):
        for c, date_obj in enumerate(row):
            cx = c * CAL_W
            cy = y + weekdays_h + r * date_h
            cw = CAL_W_SATURDAY if c == 6 else CAL_W
            ch = date_h

            draw_date_cell(
                draw,
                cx,
                cy,
                cw,
                ch,
                date_obj,
                month,
                right=(c != 6),
                is_sunday=(c == 0),
            )

    return main_cal_h


def make_calendar(year: int, month: int) -> None:
    next_year, next_month = next_month_year(year, month)

    draw = Draw(WIDTH, HEIGHT)

    # メインカレンダー
    main_cal_h = draw_main_calendar(draw=draw, year=year, month=month)

    # ヘッダ描画
    draw_header(draw, year, month, main_cal_h)

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
