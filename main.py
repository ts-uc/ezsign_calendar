import calendar
import datetime
import jpholiday
import argparse
import os
from draw import Draw


def make_calendar(year: int, month: int) -> None:
    width = 400
    height = 300

    cal = calendar.Calendar(firstweekday=6)
    weeks = cal.monthdayscalendar(year, month)
    len_weeks = 5 if len(weeks) <= 5 else 6

    header_h = 90
    weekdays_h = 210 * 2 // (2 + len_weeks*3)
    date_h = 210 * 3 // (2 + len_weeks*3)

    main_cal_w = 46
    main_cal_origin_x = (width - main_cal_w * 7) // 2
    main_cal_origin_y = header_h

    # if len(weeks) <= 5:
    #     weekdays_h = 14
    #     date_h = 14

    draw = Draw(width, height)

    # 年月表示
    text = str(month)
    draw.draw_cell(
        x=0,
        y=0,
        w=width,
        h=header_h,
        text=text,
        text_size=72
    )

    # 曜日部分のグリッド
    weekdays = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

    for c, text in enumerate(weekdays):
        reverse = (c == 0)
        draw.draw_cell(
            x=main_cal_origin_x + c * main_cal_w,
            y=main_cal_origin_y,
            w=main_cal_w,
            h=weekdays_h,
            text=text,
            text_size=16,
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
                x=main_cal_origin_x + c * main_cal_w,
                y=main_cal_origin_y + weekdays_h + r * date_h,
                w=main_cal_w,
                h=date_h,
                text="" if day == 0 else str(day),
                text_size=24,
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
