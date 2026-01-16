import sys
import threading
import shutil
import subprocess
from pathlib import Path
from typing import List

from PIL import Image
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeElapsedColumn
from rich.table import Table
from rich.panel import Panel
from concurrent.futures import ThreadPoolExecutor, as_completed

console = Console()


def collect_image_files(path: str, recursive: bool) -> List[Path]:
    """指定パスからJPEG/PNG/WebP画像ファイルを収集する（再帰対応）"""
    exts = {'.jpg', '.jpeg', '.png', '.webp'}
    p = Path(path)
    files = []
    if p.is_file() and p.suffix.lower() in exts:
        files.append(p)
    elif p.is_dir():
        if recursive:
            for f in p.rglob('*'):
                if f.suffix.lower() in exts:
                    files.append(f)
        else:
            for f in p.glob('*'):
                if f.suffix.lower() in exts:
                    files.append(f)
    return files


def process_image_wrapper(file, args, error_list, lock):
    """各画像ファイルの処理をラップし、例外をキャッチしてエラーリストに追加"""
    try:
        result = process_image(file, args)
        return (file, result, None)
    except Exception as e:
        with lock:
            error_list.append((file, type(e).__name__, str(e)))
        return (file, None, (type(e).__name__, str(e)))


def reduce_main(args):
    """メイン処理：ファイル収集、並列/逐次処理、進捗表示、サマリー出力"""
    files = collect_image_files(args.path, args.recursive)
    if not files:
        console.print(f"[bold red]エラー:[/] {args.path} に画像ファイルが見つかりません")
        sys.exit(1)

    console.print(Panel.fit(
        f"[bold cyan]{len(files)}[/] 個の画像を処理します",
        title="🖼️  Web Image Optimizer",
        border_style="cyan"
    ))

    error_list = []
    lock = threading.Lock()
    results = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]処理中...", total=len(files))

        if args.parallel:
            with ThreadPoolExecutor() as executor:
                futures = {
                    executor.submit(process_image_wrapper, f, args, error_list, lock): f
                    for f in files
                }
                for fut in as_completed(futures):
                    file, result, error = fut.result()
                    if result:
                        results.append((file, result))
                    progress.advance(task)
        else:
            for f in files:
                file, result, error = process_image_wrapper(f, args, error_list, lock)
                if result:
                    results.append((file, result))
                progress.advance(task)

    # サマリーテーブル
    console.print()

    if results:
        table = Table(title="処理結果", show_header=True, header_style="bold magenta")
        table.add_column("ファイル", style="cyan", no_wrap=False)
        table.add_column("サイズ", justify="right", style="green")
        table.add_column("品質", justify="right")
        table.add_column("リサイズ", justify="center")

        total_size = 0
        for file, result in results:
            total_size += result['size']
            quality = str(result.get('quality', '-'))
            resize = result.get('resize', (0, 0, 0, 0))
            resize_str = f"{resize[0]}x{resize[1]} → {resize[2]}x{resize[3]}"
            output = result.get('output', str(file))
            table.add_row(
                str(Path(output).name),
                f"{result['size']:.1f} KB",
                quality,
                resize_str
            )

        console.print(table)
        console.print()

    # 結果サマリー
    success_count = len(results)
    error_count = len(error_list)

    if error_count == 0:
        console.print(Panel.fit(
            f"[bold green]✓[/] [green]{success_count}[/] 個のファイルを処理しました",
            border_style="green"
        ))
    else:
        console.print(Panel.fit(
            f"[bold green]✓[/] [green]{success_count}[/] 個成功  [bold red]✗[/] [red]{error_count}[/] 個失敗",
            border_style="yellow"
        ))

    # エラー詳細
    if error_list:
        console.print()
        console.print("[bold red]エラー詳細:[/]")
        for file, err_type, err_msg in error_list:
            console.print(f"  [red]•[/] {file}: {err_type} - {err_msg}")


print_lock = threading.Lock()


def process_image(file, args):
    """1ファイルの画像圧縮・リサイズ処理"""
    file = Path(file)
    ext = file.suffix.lower()

    # バックアップ（Image.open前に実施）
    if args.backup:
        bak_path = file.with_name(f"{file.name}.bak")
        try:
            if not bak_path.exists():
                shutil.copy2(file, bak_path)
            if not bak_path.exists():
                raise IOError(f"バックアップファイルの作成に失敗しました: {bak_path}")
        except Exception as e:
            raise

    orig_img = Image.open(file)
    orig_w, orig_h = orig_img.size

    # リサイズ処理
    img = orig_img.copy()
    if args.width or args.height:
        max_w = args.width if args.width else orig_w
        max_h = args.height if args.height else orig_h
        img.thumbnail((max_w, max_h), Image.LANCZOS)

    # WebP変換処理
    if getattr(args, 'webp', False):
        webp_path = file.with_suffix('.webp')
        quality = args.quality if hasattr(args, 'quality') else 85
        img.save(webp_path, format='WEBP', quality=quality, optimize=True)
        new_size = webp_path.stat().st_size / 1024
        return {
            'size': new_size,
            'quality': quality,
            'resize': (orig_w, orig_h, img.width, img.height),
            'output': str(webp_path)
        }

    # JPEG処理
    if ext in {'.jpg', '.jpeg'}:
        quality = args.quality
        min_quality = 10
        step = 5
        target_bytes = args.size * 1024
        out_bytes = None
        used_quality = quality
        from io import BytesIO

        while quality >= min_quality:
            buf = BytesIO()
            img.save(buf, format='JPEG', quality=quality, optimize=True)
            out_bytes = buf.getvalue()
            if len(out_bytes) <= target_bytes:
                used_quality = quality
                break
            quality -= step

        with open(file, 'wb') as f:
            f.write(out_bytes)
        new_size = file.stat().st_size / 1024
        return {
            'size': new_size,
            'quality': used_quality,
            'resize': (orig_w, orig_h, img.width, img.height)
        }

    # PNG処理
    elif ext == '.png':
        tmp_path = file.with_suffix('.wio_tmp.png')
        img.save(tmp_path, format='PNG', optimize=True)
        target_bytes = args.size * 1024
        try:
            subprocess.run([
                'pngquant', '--force', '--output', str(file),
                '--quality', '50-100', '--', str(tmp_path)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            shutil.move(tmp_path, file)
        else:
            if tmp_path.exists():
                tmp_path.unlink()
        new_size = file.stat().st_size / 1024
        return {
            'size': new_size,
            'resize': (orig_w, orig_h, img.width, img.height)
        }

    # WebP処理
    elif ext == '.webp':
        quality = args.quality
        min_quality = 10
        step = 5
        target_bytes = args.size * 1024
        out_bytes = None
        used_quality = quality
        from io import BytesIO

        while quality >= min_quality:
            buf = BytesIO()
            img.save(buf, format='WEBP', quality=quality, optimize=True)
            out_bytes = buf.getvalue()
            if len(out_bytes) <= target_bytes:
                used_quality = quality
                break
            quality -= step

        with open(file, 'wb') as f:
            f.write(out_bytes)
        new_size = file.stat().st_size / 1024
        return {
            'size': new_size,
            'quality': used_quality,
            'resize': (orig_w, orig_h, img.width, img.height)
        }
    else:
        raise ValueError("Unsupported file type")
