# Web Image Optimizer (wio)

画像ファイル（JPEG/PNG）のサイズ削減・リサイズ・圧縮・WebP変換を行うPython製CLIツールです。

## 特徴

- JPEG/PNG/WebP対応
- 目標ファイルサイズ指定
- 最大幅・高さ指定でリサイズ
- 画質調整（JPEG, WebP）
- ディレクトリ再帰処理
- 並列処理による高速化
- 進捗バー表示
- デフォルトで元画像を `.bak` でバックアップ
- PNGはpngquantによる追加圧縮もサポート
- デフォルトでWebP変換（`--no-webp`で無効化可能）

## インストール

### uvのインストール

```sh
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS (Homebrew)
brew install uv
```

### wioコマンドのインストール

```sh
uv tool install git+https://github.com/sabato/web-image-optimizer.git
```

これで `wio` コマンドがどこからでも使えるようになります。

### アンインストール

```sh
uv tool uninstall web-image-optimizer
```

### オプション: pngquantのインストール（PNG圧縮強化用）

- macOS: `brew install pngquant`
- Ubuntu: `sudo apt install pngquant`

## 使い方

### 基本コマンド

```sh
wio <ファイルまたはディレクトリ>
```

### 主なオプション

- `--size <KB>`: 目標ファイルサイズ（KB単位、デフォルト: 100）
- `--width <px>`: 最大幅（デフォルト: 1200）
- `--height <px>`: 最大高さ
- `--quality <1-100>`: JPEG/WebP画質（デフォルト: 85）
- `-r, --recursive`: ディレクトリを再帰的に処理
- `--parallel`: 並列処理で高速化
- `--nobackup`: バックアップを作成しない（デフォルトは `.bak` を作成）
- `--no-webp`: WebP変換を無効化（デフォルトはWebP変換有効）

### 例

#### 画像1枚を100KB以下、幅800pxにリサイズ

```sh
wio path/to/image.jpg --size 100 --width 800
```

#### ディレクトリ内の全画像を200KB以下、最大幅1024px・最大高さ768px、品質70で再帰的に圧縮

```sh
wio path/to/dir --size 200 --width 1024 --height 768 --quality 70 -r
```

#### バックアップを作成せずに並列処理

```sh
wio path/to/dir --size 150 --nobackup --parallel -r
```

#### WebP変換せずにJPEG/PNGのまま圧縮

```sh
wio path/to/image.png --size 100 --no-webp
```

## バックアップ仕様

- デフォルトで、元画像は `<ファイル名>.<拡張子>.bak` というファイル名で同じディレクトリに保存されます。
- バックアップが不要な場合は `--nobackup` を指定してください。

## ヘルプ表示

```sh
wio --help
```

## ライセンス

MIT
