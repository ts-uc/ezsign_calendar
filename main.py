"""EZ Sign / テプラ用カレンダーの一括生成 CLI。"""

import argparse
from pathlib import Path

from ezsign import render as render_ezsign
from tepra import render as render_tepra

LAYOUTS = {
    "ezsign": render_ezsign,
    "tepra": render_tepra,
}


def parse_months(args: argparse.Namespace) -> list[tuple[int, int]]:
    """年月指定を検証し、重複を除いた年月一覧を返す。"""
    if args.month:
        values = [
            item
            for group in args.month
            for item in (group if isinstance(group, list) else [group])
        ]
        months = []
        for value in values:
            try:
                year_text, month_text = value.split("-", 1)
                year, month = int(year_text), int(month_text)
                if not 1 <= month <= 12:
                    raise ValueError
            except ValueError as exc:
                raise argparse.ArgumentTypeError(
                    f"年月は YYYY-MM で指定してください: {value}"
                ) from exc
            months.append((year, month))
        return list(dict.fromkeys(months))

    end = args.begin if args.end is None else args.end
    return [
        (year, month)
        for year in range(args.begin, end + 1)
        for month in range(1, 13)
    ]


def output_path(root: Path, layout: str, year: int, month: int, all_layouts: bool) -> Path:
    directory = root / layout if all_layouts else root
    return directory / f"{layout}_{year:04}_{month:02}.png"


def generate_calendars(args: argparse.Namespace) -> None:
    root = Path(args.output)
    # all は LAYOUTS に登録された全カレンダーを対象にする。
    # 新しいカレンダーを追加した場合も、ここを変更する必要はない。
    layouts = tuple(LAYOUTS) if args.layout == "all" else (args.layout,)

    for year, month in parse_months(args):
        for layout in layouts:
            path = output_path(root, layout, year, month, args.layout == "all")
            print(LAYOUTS[layout](year, month, path))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="EZ Sign / テプラ用カレンダーを生成します"
    )
    parser.add_argument(
        "begin", type=int, nargs="?",
        help="開始年（--month を使わない場合）",
    )
    parser.add_argument(
        "end", type=int, nargs="?",
        help="終了年（省略時は開始年）",
    )
    parser.add_argument(
        "--month", action="append", nargs="+",
        help="生成する年月（YYYY-MM）。複数指定可",
    )
    parser.add_argument(
        "--layout", choices=("ezsign", "tepra", "all"), default="all",
        help="レイアウト。省略時は全種類を生成",
    )
    parser.add_argument(
        "--output", type=Path,
        default=Path(__file__).parent / "calendars",
        help="出力ディレクトリ",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.month and (args.begin is not None or args.end is not None):
        parser.error("--month と開始年・終了年は同時に指定できません")
    if not args.month and args.begin is None:
        parser.error("開始年と終了年、または --month を指定してください")
    if args.end is not None and args.begin is None:
        parser.error("終了年を指定する場合は開始年も指定してください")

    generate_calendars(args)


if __name__ == "__main__":
    main()
