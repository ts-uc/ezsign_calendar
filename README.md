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
# 登録されている全種類を生成（既定）
python main.py 2025 2026

# EZ Sign版だけを生成
python main.py 2025 2026 --layout ezsign

# テプラ版だけを生成
python main.py 2025 2026 --layout tepra

# 出力先を変更する場合
python main.py 2025 2026 --output ./calendars
```

必要な月だけをまとめて指定できます。重複した年月は一度だけ生成します。

```bash
python main.py --month 2025-01 2025-03 2026-12 --layout all
```

出力先は通常 `calendars/ezsign/YYYY_MM.png` と `calendars/tepra/YYYY_MM.png` です。レイアウトを指定した場合は、指定レイアウトの画像だけを `calendars/YYYY_MM.png` に保存します。レイアウトを省略するか `--layout all` を指定すると、`LAYOUTS` に登録された全種類を生成します。

## ファイル構成

- `main.py` - レイアウト選択と一括生成 CLI
- `ezsign.py` - EZ Sign 版の描画
- `tepra.py` - テプラ版の描画（`tepra_calendar.py` 相当）
- `draw.py` - 画像描画ヘルパー
- `calendar_meta.py` - 祝日・暦情報
- `calendars/` - 生成画像の出力先
- `fonts/` - 使用フォント

## ライセンス

MIT License
