import calendar
import datetime
import jpholiday
import argparse
import os
from draw import Draw


def make_calendar(year: int, month: int) -> None:
    cell_w = 20
    width = cell_w * 7
    height = 96

    header_h = 12
    weekdays_h = 12
    date_h = 12

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)

    if len(weeks) <= 5:
        weekdays_h = 14
        date_h = 14

    draw = Draw(width, height)

    # 年月表示
    text = f"{year:04}-{month:02}"
    draw.draw_cell(
        x=0,
        y=0,
        w=width,
        h=header_h,
        text=text,
        text_size=12
    )

    # 曜日部分のグリッド
    weekdays = ["SU", "MO", "TU", "WE", "TH", "FR", "SA"]

    for c, text in enumerate(weekdays):
        reverse = (c == 0)
        draw.draw_cell(
            x=c * cell_w,
            y=header_h,
            w=cell_w,
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

            draw.draw_cell(
                x=c * cell_w,
                y=r * date_h + header_h + weekdays_h,
                w=cell_w,
                h=date_h,
                text="" if day == 0 else str(day),
                text_size=12,
                red=reverse
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
