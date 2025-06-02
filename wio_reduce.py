import sys
from pathlib import Path
from typing import List
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
from PIL import Image
import shutil
import subprocess


def collect_image_files(path: str, recursive: bool) -> List[Path]:
    exts = {'.jpg', '.jpeg', '.png'}
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
    try:
        result = process_image(file, args)
        return (file, result, None)
    except Exception as e:
        with lock:
            error_list.append((file, type(e).__name__, str(e)))
        return (file, None, (type(e).__name__, str(e)))


def reduce_main(args):
    files = collect_image_files(args.path, args.recursive)
    if not files:
        print(f"[ERROR] No image files found in {args.path}")
        sys.exit(1)
    error_list = []
    lock = threading.Lock()
    results = []
    if args.parallel:
        with ThreadPoolExecutor() as executor:
            futures = {executor.submit(process_image_wrapper, f, args, error_list, lock): f for f in files}
            for fut in tqdm(as_completed(futures), total=len(files), desc="Processing"):
                file, result, error = fut.result()
                if result:
                    results.append((file, result))
    else:
        for f in tqdm(files, desc="Processing"):
            file, result, error = process_image_wrapper(f, args, error_list, lock)
            if result:
                results.append((file, result))
    # サマリー表示
    print(f"\nProcessed: {len(results)} files, Errors: {len(error_list)}")
    for file, err_type, err_msg in error_list:
        print(f"[ERROR] {file}: {err_type} - {err_msg}")


print_lock = threading.Lock()


def process_image(file, args):
    file = Path(file)
    ext = file.suffix.lower()
    # orig_size = file.stat().st_size
    orig_img = Image.open(file)
    orig_w, orig_h = orig_img.size
    # バックアップ
    if args.backup:
        bak_path = file.with_suffix(file.suffix + ".bak")
        if not bak_path.exists():
            shutil.copy2(file, bak_path)
    # リサイズ
    img = orig_img.copy()
    if args.width or args.height:
        max_w = args.width if args.width else orig_w
        max_h = args.height if args.height else orig_h
        img.thumbnail((max_w, max_h), Image.LANCZOS)
    # JPEG
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
        # 最終保存
        with open(file, 'wb') as f:
            f.write(out_bytes)
        new_size = file.stat().st_size / 1024
        msg = f"[OK] {file} → {new_size:.1f}KB (quality={used_quality}, resize={orig_w}x{orig_h}→{img.width}x{img.height})"
        with print_lock:
            print(msg)
        return {'size': new_size, 'quality': used_quality, 'resize': (orig_w, orig_h, img.width, img.height)}
    # PNG
    elif ext == '.png':
        tmp_path = file.with_suffix('.wio_tmp.png')
        img.save(tmp_path, format='PNG', optimize=True)
        # pngquantでさらに圧縮
        target_bytes = args.size * 1024
        # result_path = file
        try:
            subprocess.run([
                'pngquant', '--force', '--output', str(file), '--quality', '50-100', '--', str(tmp_path)
            ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception:
            # pngquant失敗時はPillow出力をそのまま使う
            shutil.move(tmp_path, file)
        else:
            if tmp_path.exists():
                tmp_path.unlink()
        new_size = file.stat().st_size / 1024
        msg = f"[OK] {file} → {new_size:.1f}KB (resize={orig_w}x{orig_h}→{img.width}x{img.height})"
        with print_lock:
            print(msg)
        return {'size': new_size, 'resize': (orig_w, orig_h, img.width, img.height)}
    else:
        raise ValueError("Unsupported file type")
