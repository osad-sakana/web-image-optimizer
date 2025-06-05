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
- WebP変換対応（`--webp`）

## インストール

1. 依存パッケージのインストール

   ```sh
   poetry install --no-root
   ```

2. 必要に応じて `pngquant` をインストール（PNG圧縮強化用）

   - macOS: `brew install pngquant`
   - Ubuntu: `sudo apt install pngquant`

## 使い方

### 基本コマンド

```sh
poetry run wio reduce --path <ファイルまたはディレクトリ> --size <目標KB>
```

### 主なオプション

- `--path <パス>`: 対象ファイルまたはディレクトリ（必須）
- `--size <KB>`: 目標ファイルサイズ（KB単位, 必須）
- `--width <px>`: 最大幅
- `--height <px>`: 最大高さ
- `--quality <1-100>`: JPEG/WebP画質（デフォルト85）
- `-r, --recursive`: ディレクトリを再帰的に処理
- `--parallel`: 並列処理で高速化
- `--nobackup`: バックアップを作成しない（デフォルトは常に `.bak` を作成）
- `--webp`: 画像をWebP形式に変換して保存

### 例

#### 画像1枚を100KB以下、幅800pxにリサイズ

```sh
poetry run wio reduce --path path/to/image.jpg --size 100 --width 800
```

#### ディレクトリ内の全画像を200KB以下、最大幅1024px・最大高さ768px、品質70で再帰的に圧縮

```sh
poetry run wio reduce --path path/to/dir --size 200 --width 1024 --height 768 --quality 70 -r
```

#### バックアップを作成せずに並列処理

```sh
poetry run wio reduce --path path/to/dir --size 150 --nobackup --parallel -r
```

#### 画像をWebP形式で100KB以下に変換

```sh
poetry run wio reduce --path path/to/image.png --size 100 --webp
```

## バックアップ仕様

- デフォルトで、元画像は `<ファイル名>.<拡張子>.bak` というファイル名で同じディレクトリに保存されます。
- バックアップが不要な場合は `--nobackup` を指定してください。

## ヘルプ表示

```sh
poetry run wio
```

または

```sh
poetry run wio reduce --help
```

## ライセンス

MIT
