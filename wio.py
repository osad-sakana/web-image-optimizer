import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="wio",
        description="Web Image Optimizer - 画像ファイルのサイズ削減・リサイズ・圧縮・WebP変換ツール"
    )
    parser.add_argument(
        "path", help="対象ファイルまたはディレクトリのパス")
    parser.add_argument(
        "--size", type=int, default=100, help="目標ファイルサイズ（KB単位、デフォルト: 100）")
    parser.add_argument(
        "--width", type=int, default=1200, help="最大幅（px、デフォルト: 1200）")
    parser.add_argument(
        "--height", type=int, help="最大高さ（px）")
    parser.add_argument(
        "--quality", type=int, default=85, help="JPEG/WebP画質（1-100、デフォルト: 85）")
    parser.add_argument(
        "-r", "--recursive", action="store_true", help="ディレクトリを再帰的に処理")
    parser.add_argument(
        "--nobackup", action="store_true", help="バックアップを作成しない")
    parser.add_argument(
        "--parallel", action="store_true", help="並列処理を有効化")
    parser.add_argument(
        "--no-webp", action="store_true", help="WebP変換を無効化（デフォルトはWebP変換有効）")

    args = parser.parse_args()

    # デフォルトはバックアップ有効、--nobackup指定時のみ無効
    args.backup = not args.nobackup

    # デフォルトはWebP有効、--no-webp指定時のみ無効
    args.webp = not args.no_webp

    from wio_reduce import reduce_main
    reduce_main(args)


if __name__ == "__main__":
    main()
