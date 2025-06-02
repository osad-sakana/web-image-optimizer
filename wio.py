import argparse


def main():
    parser = argparse.ArgumentParser(
        prog="wio", description="Web Image Optimizer CLI Tool")
    subparsers = parser.add_subparsers(dest="command", required=False)

    reduce_parser = subparsers.add_parser(
        "reduce",
        help="Reduce image file size with resizing and compression."
    )
    reduce_parser.add_argument(
        "--path", required=True, help="Target file or directory path.")
    reduce_parser.add_argument(
        "--size", required=True, type=int, help="Target file size in KB.")
    reduce_parser.add_argument(
        "--width", type=int, help="Max width of output image (px).")
    reduce_parser.add_argument(
        "--height", type=int, help="Max height of output image (px).")
    reduce_parser.add_argument(
        "--quality", type=int, default=85, help="JPEG quality (1-100, default: 85).")
    reduce_parser.add_argument(
        "-r", "--recursive", action="store_true", help="Process directories recursively.")
    reduce_parser.add_argument(
        "--nobackup", action="store_true", help="Do not backup original files before processing.")
    reduce_parser.add_argument(
        "--parallel", action="store_true", help="Enable parallel processing.")

    args = parser.parse_args()

    # サブコマンド未指定や引数なしの場合はヘルプを表示
    if args.command is None:
        parser.print_help()
        exit(0)

    # デフォルトはバックアップ有効、--nobackup指定時のみ無効
    args.backup = not args.nobackup

    if args.command == "reduce":
        from wio_reduce import reduce_main
        reduce_main(args)


if __name__ == "__main__":
    main()
