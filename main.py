import calendar
import datetime
import jpholiday
import argparse
import os
from draw import Draw


def draw_sub_calendar(draw: Draw, year: int, month: int, x: int, y: int, w: int, h: int):
    cal_w = w // 7

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    len_weeks = 5 if len(weeks) <= 5 else 6
    date_h = h // (1 + len_weeks)
    weekdays_h = h - date_h * len_weeks

    # 曜日部分のグリッド
    weekdays = ["S", "M", "T", "W", "T", "F", "S"]

    for c, text in enumerate(weekdays):
        reverse = (c == 0)
        draw.draw_text(
            x=x + c * cal_w,
            y=y,
            w=cal_w,
            h=weekdays_h,
            text=text,
            text_size=12,
            red=reverse
        )

    # 日付部分のグリッド
    for r, row in enumerate(weeks):
        for c, day in enumerate(row):
            # 祝日判定
            is_holiday = False
            if day != 0:
                d = datetime.date(year, month, day)
                is_holiday = jpholiday.is_holiday(d)
            reverse = (c == 0) or is_holiday

            draw.draw_text(
                x=x + c * cal_w,
                y=y + weekdays_h + r * date_h,
                w=cal_w,
                h=date_h,
                text="" if day == 0 else str(day),
                text_size=12,
                red=reverse
            )


def draw_main_calendar(draw: Draw, year: int, month: int, x: int, y: int, w: int, h: int):
    cal_w = w // 7

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    len_weeks = 5 if len(weeks) <= 5 else 6
    date_h = h * 3 // (2 + len_weeks * 3)
    weekdays_h = h - date_h * len_weeks

    # 曜日部分のグリッド
    weekdays = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    for c, text in enumerate(weekdays):
        cx = x + c * cal_w
        cy = y
        cw = cal_w
        ch = weekdays_h

        draw.draw_cell_line(
            x=cx, y=cy, w=cw, h=ch,
            top=True,
            right=(c != 6)
        )

        reverse = (c == 0)
        draw.draw_text(
            x=cx, y=cy, w=cw, h=ch,
            text=text,
            text_size=16,
            red=reverse
        )

    # 日付部分のグリッド
    for r, row in enumerate(weeks):
        for c, day in enumerate(row):
            cx = x + c * cal_w
            cy = y + weekdays_h + r * date_h
            cw = cal_w
            ch = date_h

            draw.draw_cell_line(
                x=cx, y=cy, w=cw, h=ch,
                top=True,
                right=(c != 6)
            )

            # 祝日判定
            is_holiday = False
            if day != 0:
                d = datetime.date(year, month, day)
                is_holiday = jpholiday.is_holiday(d)
            reverse = (c == 0) or is_holiday

            draw.draw_text(
                x=cx, y=cy, w=cw, h=ch,
                text="" if day == 0 else str(day),
                text_size=28,
                red=reverse
            )


def make_calendar(year: int, month: int) -> None:
    width = 400
    height = 300

    # 次の月
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    # 高さ指定
    # 5週以下なら5週分、6週以上なら6週分の高さを確保
    header_h = 90
    main_cal_h = height - header_h


    sub_cal_h = header_h - 10
    sub_cal_w = 16*7

    draw = Draw(width, height)

    # 年月表示
    text = str(month)
    draw.draw_text(
        x=0,
        y=0,
        w=width * 2 // 7,
        h=header_h,
        text=text,
        text_size=72
    )

    # サブカレンダー
    draw_sub_calendar(
        draw=draw,
        year=next_year,
        month=next_month,
        x=width - sub_cal_w - 5,
        y=5,
        w=sub_cal_w,
        h=sub_cal_h
    )

    # メインカレンダー
    draw_main_calendar(
        draw=draw,
        year=year,
        month=month,
        x=0,
        y=header_h,
        w=width,
        h=main_cal_h
    )

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
