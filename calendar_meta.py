import calendar
import datetime

import jpholiday
import sxtwl
from japanera import EraDate
from qreki import Kyureki
from skyfield import almanac
from skyfield.api import load

# 二十四節気名称
SEKKI = [
    "冬至", "小寒", "大寒", "立春", "雨水", "啓蟄", "春分", "清明",
    "穀雨", "立夏", "小満", "芒種", "夏至", "小暑", "大暑", "立秋",
    "処暑", "白露", "秋分", "寒露", "霜降", "立冬", "小雪", "大雪"
]

# 干支
ETO = [
    "甲子", "乙丑", "丙寅", "丁卯", "戊辰", "己巳", "庚午", "辛未", "壬申", "癸酉",
    "甲戌", "乙亥", "丙子", "丁丑", "戊寅", "己卯", "庚辰", "辛巳", "壬午", "癸未",
    "甲申", "乙酉", "丙戌", "丁亥", "戊子", "己丑", "庚寅", "辛卯", "壬辰", "癸巳",
    "甲午", "乙未", "丙申", "丁酉", "戊戌", "己亥", "庚子", "辛丑", "壬寅", "癸卯",
    "甲辰", "乙巳", "丙午", "丁未", "戊申", "己酉", "庚戌", "辛亥", "壬子", "癸丑",
    "甲寅", "乙卯", "丙辰", "丁巳", "戊午", "己未", "庚申", "辛酉", "壬戌", "癸亥",
]

# 伝統的月名
TRADITIONAL_MONTH = ["", "睦月", "如月", "弥生", "卯月", "皐月", "水無月",
                     "文月", "葉月", "長月", "神無月", "霜月", "師走"]

# Skyfield 初期化（1回だけ）
ts = load.timescale()
eph = load("de421.bsp")


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


def get_jp_era(date: datetime.date) -> str:
    era_name = EraDate.from_date(date).strftime("%-K")
    year_text = EraDate.from_date(date).strftime("%-Y")
    year_text = "元" if year_text == "1" else to_zenkaku(year_text)
    return era_name+year_text


def get_eto(date: datetime.date) -> str:
    return ETO[(date.year - 4) % 60]


def get_traditional_month(month: int) -> str:
    return TRADITIONAL_MONTH[month]


def get_moon_phase_type(date: datetime.date) -> int | None:
    t0 = ts.utc(date.year, date.month, date.day)
    t1 = ts.utc((date + datetime.timedelta(days=1)).year,
                (date + datetime.timedelta(days=1)).month,
                (date + datetime.timedelta(days=1)).day)
    f = almanac.moon_phases(eph)
    _, phases = almanac.find_discrete(t0, t1, f)
    return int(phases[0]) if len(phases) else None


JST = datetime.timezone(datetime.timedelta(hours=9))


def is_national_holiday(date: datetime.date) -> bool:
    return jpholiday.is_holiday(date)


def get_national_holiday(date: datetime.date) -> str | None:
    if jpholiday.is_holiday(date):
        name = jpholiday.is_holiday_name(date)
        return "振替休日" if "振替休日" in name else name
    return None
