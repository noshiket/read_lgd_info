# read_lgd_info.py
LGDロゴファイル解析ツール

## 概要

LGD ファイルを解析し、標準のロゴ情報および独自拡張ヘッダから以下の情報を抽出します：
- ロゴ名: 透過性ロゴの名称
- サービスID (SID): Amatsukaze 特有の拡張データから抽出
- ポジション: 表示位置 (x, y)
- サイズ: 幅 (w) および 高さ (h)
- 可視化: ロゴデータの PNG 書き出し（オプション）

## インストール

### 1. リポジトリのクローン

```bash
git clone https://github.com/noshiket/read_lgd_info
cd read_lgd_info
```

### 2. 仮想環境の構築

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windowsの場合: .venv\Scripts\activate
```

### 3. 依存ライブラリのインストール

```bash
pip install -r requirements.txt
```

## ロゴ情報の表示

```bash
python3 read_lgd_info.py logo.lgd
```

出力例:
```
File Header: <logo data file ver0.1>
Logo count: 1

Logo File Information:
  Name: テレ東(2025-10-09)
  Service ID: 1072
  Position (x, y): (1312, 40)
  Size (w x h): 90 x 54

Command to create logo from TS:
  ./logo_scanner input.ts <serviceid> 1312 40 90 54 output.lgd
```

## ロゴをPNG画像として出力

-o オプションを指定することで、透過情報（Alpha）を保持した状態で PNG 保存します

#### PNG出力

```bash
.venv/bin/python3 read_lgd_info.py logo.lgd -o logo.png
```

出力例:
```
Read 9984 pixels

PNG saved to: logo.png
  - Size: 128 x 78 pixels
  - Format: RGBA (with alpha channel)
  - Alpha represents logo opacity
```
- Alpha値: dp_y, dp_cb, dp_cr の平均値から算出され、ロゴの不透明度を表現します。

## 技術仕様
このツールは以下のデータ構造に基づいて解析を行っています：
- Base部: 標準的な LOGO_HEADER および LOGO_PIXEL データ。
- Extended部: Amatsukaze 独自の LogoHeader（serviceId 等を含む）。

## ライセンス
MIT Licenseです。
LICENSEファイルに記載してます。
