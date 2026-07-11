# EZ Sign 用カレンダー

EZ Sign 用の大きなカレンダーと、`tepra_calendar` と同じテプラ用カレンダーを生成します。
テプラ版は縦 96 ドット、18 mm テープ向けの白黒画像です。通常版は祝日・二十四節気・雑節・月相を含みます。

## セットアップ

```bash
pip install -r requirements.txt
```

## 使い方

年の範囲を指定すると、各年の 1 月から 12 月までを一度に生成します。

```bash
# EZ Sign 版（既定）
python main.py 2025 2026

# テプラ版
python main.py 2025 2026 --layout tepra

# 両方を生成（出力先を分ける）
python main.py 2025 2026 --layout both --output ./output
```

必要な月だけをまとめて指定できます。重複した年月は一度だけ生成します。

```bash
python main.py --month 2025-01 2025-03 2026-12 --layout both
```

出力先は通常 `calendars/YYYY_MM.png` です。`both` の場合は、指定した出力先の `ezsign/` と `tepra/` に分けて保存します。

## ファイル構成

- `main.py` - EZ Sign 版の描画と一括生成 CLI
- `tepra.py` - テプラ版の描画（`tepra_calendar.py` 相当）
- `draw.py` - 画像描画ヘルパー
- `calendar_meta.py` - 祝日・暦情報
- `calendars/` - 生成画像の出力先
- `fonts/` - 使用フォント

## ライセンス

MIT License
