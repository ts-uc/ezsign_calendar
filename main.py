import calendar
import datetime
import jpholiday
import argparse
import os
import sxtwl
from draw import Draw
from qreki import Kyureki

WIDTH = 400
HEIGHT = 300
HEADER_H = 90

JQ = [
    "冬至", "小寒", "大寒", "立春", "雨水", "啓蟄", "春分", "清明",
    "穀雨", "立夏", "小満", "芒種", "夏至", "小暑", "大暑", "立秋",
    "処暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
]


def draw_sub_calendar(draw: Draw, year: int, month: int, main_cal_h: int) -> None:
    cal_w = 18
    x = WIDTH - cal_w * 7 - 5

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    len_weeks = 5 if len(weeks) <= 5 else 6
    date_h = 12 if len_weeks == 5 else 11
    weekdays_h = date_h

    h = weekdays_h + date_h * len_weeks
    y = (HEIGHT - main_cal_h - h + 1) // 2

    # 月表示
    text = str(month)
    draw.draw_text(
        x=x - 3,
        y=y,
        text=text,
        text_size=15,
        anchor="rt"
    )

    # 曜日部分のグリッド
    weekdays = ["S", "M", "T", "W", "T", "F", "S"]

    for c, text in enumerate(weekdays):
        reverse = (c == 0)
        draw.draw_text(
            x=x + c * cal_w + cal_w // 2,
            y=y,
            text=text,
            text_size=10,
            red=reverse,
            anchor="mt"
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
                x=x + c * cal_w + cal_w // 2,
                y=y + weekdays_h + r * date_h,
                text="" if day == 0 else str(day),
                text_size=10,
                red=reverse,
                anchor="mt"
            )


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

        draw.draw_cell_line(
            x=cx, y=cy, w=cw, h=ch,
            top=True,
            right=(c != 6)
        )

        reverse = (c == 0)
        draw.draw_text(
            x=cx+3, y=cy+4,
            text=text,
            text_size=10,
            red=reverse,
            anchor="lt"
        )

    # 日付部分のグリッド
    for r, row in enumerate(weeks):
        for c, day in enumerate(row):
            cx = c * cal_w
            cy = y + weekdays_h + r * date_h
            cw = cal_w
            ch = date_h

            # 罫線
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

            # 日付
            draw.draw_text(
                x=cx + 3 + 15, y=cy+4,
                text="" if day == 0 else str(day),
                text_size=20,
                red=reverse,
                anchor="mt"
            )

            if day != 0:
                # 六曜
                k = Kyureki.from_ymd(year, month, day)
                draw.draw_text(
                    x=cx + cw - 3, y=cy+4,
                    text=k.rokuyou,
                    text_size=8,
                    anchor="rt"
                )

                # 二十四節気
                sd = sxtwl.fromSolar(year, month, day)

                if sd.hasJieQi():
                    draw.draw_text(
                        x=cx + cw - 3, y=cy+4 + 10,
                        text=JQ[sd.getJieQi()],
                        text_size=8,
                        anchor="rt"
                    )

                # 祝日名
                d = datetime.date(year, month, day)
                if jpholiday.is_holiday(d):
                    holiday_name = jpholiday.is_holiday_name(d)
                    holiday_name = "振替休日" if "振替休日" in holiday_name else holiday_name
                    draw.draw_text(
                        x=cx + 3, y=cy+4 + 21,
                        text=holiday_name,
                        text_size=8,
                        anchor="lt",
                        red=True
                    )

    return main_cal_h


def make_calendar(year: int, month: int) -> None:
    # 次の月
    next_month = month + 1
    next_year = year
    if next_month > 12:
        next_month = 1
        next_year += 1

    # 高さ指定
    # 5週以下なら5週分、6週以上なら6週分の高さを確保
    header_h = 90

    sub_cal_h = header_h - 10
    sub_cal_w = 18*7

    draw = Draw(WIDTH, HEIGHT)

    # 年月表示
    draw.draw_text(
        x=80,
        y=75,
        text=str(year),
        text_size=20,
        anchor="rb"
    )

    draw.draw_text(
        x=120,
        y=75,
        text=str(month),
        text_size=50,
        anchor="mb"
    )

    draw.draw_text(
        x=160,
        y=75,
        text=calendar.month_abbr[month].upper(),
        text_size=20,
        anchor="lb"
    )

    # メインカレンダー
    main_cal_h = draw_main_calendar(
        draw=draw,
        year=year,
        month=month,
    )

    # サブカレンダー
    draw_sub_calendar(
        draw=draw,
        year=next_year,
        month=next_month,
        main_cal_h=main_cal_h
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
