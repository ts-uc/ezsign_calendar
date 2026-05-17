import calendar
import datetime
import jpholiday
import argparse
import os
import sxtwl
from japanera import EraDate

from skyfield.api import load
from skyfield import almanac
from draw import Draw
from qreki import Kyureki

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

JQ = [
    "冬至", "小寒", "大寒", "立春", "雨水", "啓蟄", "春分", "清明",
    "穀雨", "立夏", "小満", "芒種", "夏至", "小暑", "大暑", "立秋",
    "処暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
]

KANSHI = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]

JM = ["", "睦月", "如月", "弥生", "卯月", "皐月", "水無月", "文月", "葉月", "長月", "神無月", "霜月", "師走"]

def to_zenkaku(s: str) -> str:
    return s.translate(str.maketrans(
        "0123456789",
        "０１２３４５６７８９"
    ))


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
    era_name = EraDate.from_date(d).strftime("%-K")
    year_text = EraDate.from_date(d).strftime("%-Y")
    year_text = "元" if year_text == "1" else to_zenkaku(year_text)
    kanshi = KANSHI[(d.year - 4) % 60]

    draw.draw_text(x=80, y=75, text=f"{era_name}{year_text}年{kanshi}", text_size=8, anchor="rb")
    draw.draw_text(x=120, y=75, text=str(month), text_size=50, anchor="mb")
    draw.draw_text(x=160, y=65, text=calendar.month_abbr[month].upper(), text_size=20, anchor="lb")
    draw.draw_text(x=160, y=75, text=JM[month], text_size=8, anchor="lb")

# 初期化（1回だけ）
ts = load.timescale()
eph = load("de421.bsp")

def moon_phase_type(date: datetime):
    """
    指定日の主要月相を返す

    Returns:
        0: 朔
        1: 上弦
        2: 望
        3: 下弦
        None: その日に主要月相なし
    """

    t0 = ts.utc(date.year, date.month, date.day)
    t1 = ts.utc((date + datetime.timedelta(days=1)).year,
                (date + datetime.timedelta(days=1)).month,
                (date + datetime.timedelta(days=1)).day)

    f = almanac.moon_phases(eph)
    _, phases = almanac.find_discrete(t0, t1, f)

    return int(phases[0]) if len(phases) else None


def draw_weekday_cell(draw: Draw, cx: int, cy: int, cw: int, ch: int, text: str, right: bool, is_sunday: bool):
    draw.draw_cell_line(x=cx, y=cy, w=cw, h=ch, top=True, right=right)
    draw.draw_text(x=cx + 3, y=cy + 4, text=text, text_size=10, red=is_sunday, anchor="lt")


def draw_date_cell(draw: Draw, cx: int, cy: int, cw: int, ch: int, day: int, year: int, month: int, right: bool):
    # 罫線
    draw.draw_cell_line(x=cx, y=cy, w=cw, h=ch, top=True, right=right)

    # 日付表示
    draw.draw_text(x=cx + 3 + 15, y=cy + 4, text="" if day == 0 else str(day), text_size=20, red=False, anchor="mt")

    if day == 0:
        return

    # 祝日判定
    d = datetime.date(year, month, day)
    is_holiday = jpholiday.is_holiday(d)
    reverse = is_holiday

    if reverse:
        # 再描画赤文字で上書き
        draw.draw_text(x=cx + 3 + 15, y=cy + 4, text=str(day), text_size=20, red=True, anchor="mt")

    # 月相
    mp = moon_phase_type(datetime.datetime(year, month, day))
    if mp is not None:
        draw.draw_moon_phase(x=cx + cw - 2 - 12, y=cy + ch - 2 - 12, w=12, h=12, phase=mp)

    # 六曜
    k = Kyureki.from_ymd(year, month, day)
    draw.draw_text(x=cx + cw - 3, y=cy + 4, text=k.rokuyou, text_size=8, anchor="rt")

    # 二十四節気
    sd = sxtwl.fromSolar(year, month, day)
    if sd.hasJieQi():
        draw.draw_text(x=cx + cw - 3, y=cy + 4 + 10, text=JQ[sd.getJieQi()], text_size=8, anchor="rt")

    # 祝日名
    if is_holiday:
        holiday_name = jpholiday.is_holiday_name(d)
        holiday_name = "振替休日" if "振替休日" in holiday_name else holiday_name
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

            draw_date_cell(draw, cx, cy, cw, ch, day, year, month, right=(c != 6))

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
