from PIL import Image, ImageDraw, ImageFont
import calendar
import datetime
import jpholiday
import argparse
import os
from pathlib import Path
import read_font


class Draw:
    def __init__(self, w, h):
        self.font_j10 = read_font.read_font(10)
        self.img = Image.new("1", (w, h), 1)
        self.draw = ImageDraw.Draw(self.img)

    def draw_cell(self, x: int, y: int, w: int, h: int, text: str, reverse: bool = False):
        if reverse:
            self.draw.rectangle(
                (x, y, x + w - 1, y + h - 1),
                fill=0
            )
        bbox = self.draw.textbbox((0, 0), text, font=self.font_j10)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        tx = x + (w - text_w) // 2 - bbox[0]
        ty = y + (h - text_h) // 2 - bbox[1]

        self.draw.text(
            (tx, ty),
            text,
            font=self.font_j10,
            fill=1 if reverse else 0
        )

    def save(self, out: str):
        self.img.save(out)


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
        text=text
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
            reverse=reverse
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
                reverse=reverse
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
