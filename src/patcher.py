"""Offline, non-destructive Windows ISO patcher. No game files are bundled."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
MANIFEST = ROOT / 'patches' / 'manifest.json'


class PatchError(Exception):
    pass


class Cancelled(PatchError):
    pass


def check_cancel(cancel):
    if cancel is not None and cancel.is_set():
        raise Cancelled('작업을 취소했습니다. 원본 ISO는 변경되지 않았습니다.')


def sha256(path, cancel=None, progress=None):
    digest = hashlib.sha256()
    size = Path(path).stat().st_size
    total = 0
    with open(path, 'rb') as stream:
        while chunk := stream.read(4 * 1024 * 1024):
            check_cancel(cancel)
            digest.update(chunk)
            total += len(chunk)
            if progress:
                progress(total / max(1, size))
    check_cancel(cancel)
    return digest.hexdigest()


def load_manifest(root=ROOT):
    return json.loads((root / 'patches' / 'manifest.json').read_text(encoding='utf-8'))


def verify_payload(root=ROOT, manifest=None):
    manifest = manifest or load_manifest(root)
    for key in ('patch', 'engine'):
        entry = manifest[key]
        path = root / entry['file']
        if not path.is_file() or path.stat().st_size != entry['bytes'] or sha256(path) != entry['sha256']:
            raise PatchError('내장 패치 데이터 검증 실패: ' + key + '\n공식 배포 파일을 다시 받아주세요.')
    return manifest


def apply_patch(source, output, root=ROOT, cancel=None, notify=lambda label, value: None):
    manifest = verify_payload(root)
    source = Path(source).expanduser().resolve(strict=True)
    output = Path(output).expanduser().resolve()
    if not source.is_file():
        raise PatchError('원본 ISO 파일을 선택하세요.')
    if source == output or (output.exists() and os.path.samefile(source, output)):
        raise PatchError('원본과 출력 경로가 같습니다. 새 ISO 파일 이름을 지정하세요.')
    if output.exists():
        raise PatchError('출력 파일이 이미 있습니다. 다른 이름을 지정하세요. 기존 파일은 덮어쓰지 않습니다.')
    if output.suffix.lower() != '.iso':
        raise PatchError('출력 파일의 확장자는 .iso여야 합니다.')
    if not output.parent.is_dir():
        raise PatchError('출력 폴더가 없습니다.')
    expected = manifest['source']
    if source.stat().st_size != expected['bytes']:
        raise PatchError('지원하지 않는 원본 크기입니다. Japan (En,Ja) ISO와 README의 SHA-256을 확인하세요.')
    notify('원본 ISO의 SHA-256을 확인하고 있습니다.', 0)
    actual = sha256(source, cancel, lambda value: notify('원본 ISO 검증 중', value * 30))
    if actual != expected['sha256']:
        raise PatchError('원본 SHA-256이 일치하지 않습니다.\n기대값: ' + expected['sha256'] + '\n선택값: ' + actual)
    if shutil.disk_usage(output.parent).free < manifest['output']['bytes'] + 32 * 1024 * 1024:
        raise PatchError('출력 드라이브의 빈 공간이 부족합니다. 최소 450 MB를 확보하세요.')
    check_cancel(cancel)
    # Create a unique file exclusively; never delete a pre-existing .partial file.
    fd, name = tempfile.mkstemp(prefix=output.stem + '-', suffix='.partial', dir=output.parent)
    temporary = Path(name)
    process = None
    try:
        with os.fdopen(fd, 'wb') as destination, tempfile.TemporaryFile() as errors:
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
            environment = dict(os.environ)
            # Do not allow the engine's ambient option variable to change decoding.
            environment.pop('XDELTA', None)
            command = [str(root / manifest['engine']['file']), '-d', '-c', '-s', str(source),
                       str(root / manifest['patch']['file'])]
            process = subprocess.Popen(command, stdout=destination, stderr=errors,
                                       stdin=subprocess.DEVNULL, creationflags=flags, env=environment)
            while process.poll() is None:
                check_cancel(cancel)
                written = temporary.stat().st_size
                notify('한글 패치 적용 중', 30 + min(1, written / manifest['output']['bytes']) * 45)
                time.sleep(0.08)
            if process.returncode:
                errors.seek(0)
                detail = errors.read(4096).decode('utf-8', errors='replace')
                raise PatchError('패치 적용에 실패했습니다.\n' + detail)
        check_cancel(cancel)
        notify('생성된 ISO의 SHA-256을 확인하고 있습니다.', 75)
        actual = sha256(temporary, cancel, lambda value: notify('결과 ISO 검증 중', 75 + value * 24))
        if temporary.stat().st_size != manifest['output']['bytes'] or actual != manifest['output']['sha256']:
            raise PatchError('결과 ISO 검증에 실패했습니다. 완성 파일로 저장하지 않습니다.')
        check_cancel(cancel)
        # Windows rename is exclusive: a concurrently created destination also survives.
        if os.name == 'nt':
            os.rename(temporary, output)
        else:
            os.link(temporary, output)
            temporary.unlink()
        notify('완료! 원본 ISO는 그대로 보존했습니다.', 100)
        return {'version': manifest['version'], 'output': str(output), 'bytes': output.stat().st_size,
                'sha256': actual, 'source_sha256': expected['sha256'], 'verified': True}
    finally:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait(timeout=15)
        if temporary.exists():
            temporary.unlink()


def gui():
    import tkinter as tk
    from tkinter import filedialog, messagebox, ttk

    manifest = load_manifest()
    window = tk.Tk()
    window.title('Crazy Taxi 3 · 한글 패처 V1.0')
    window.geometry('760x520')
    window.minsize(700, 520)
    window.configure(bg='#1b1b1b')
    style = ttk.Style(window)
    style.theme_use('clam')
    style.configure('.', font=('맑은 고딕', 10))
    style.configure('TFrame', background='#1b1b1b')
    style.configure('TLabel', background='#1b1b1b', foreground='#f5f5f5')
    style.configure('Title.TLabel', font=('맑은 고딕', 23, 'bold'), foreground='#ffd32a')
    style.configure('Small.TLabel', font=('맑은 고딕', 9), foreground='#c9c9c9')
    style.configure('TButton', padding=(12, 8))
    style.configure('Horizontal.TProgressbar', background='#ffcc00', troughcolor='#353535')
    frame = ttk.Frame(window, padding=24)
    frame.pack(fill='both', expand=True)
    frame.columnconfigure(0, weight=1)
    ttk.Label(frame, text='CRAZY TAXI 3  /  한국어', style='Title.TLabel').grid(row=0, column=0, columnspan=2, sticky='w')
    ttk.Label(frame, text='V1.0 비공식 한글판 정식버전  ·  Korea Localized by GiKakNo').grid(row=1, column=0, columnspan=2, sticky='w', pady=(4, 18))
    ttk.Label(frame, text='1. Japan (En,Ja) 원본 ISO').grid(row=2, column=0, columnspan=2, sticky='w')
    source = tk.StringVar()
    output = tk.StringVar()
    source_entry = ttk.Entry(frame, textvariable=source)
    source_entry.grid(row=3, column=0, sticky='ew', pady=(6, 16), padx=(0, 8))

    def choose_source():
        path = filedialog.askopenfilename(parent=window, title='Japan (En,Ja) 원본 ISO', filetypes=[('ISO 이미지', '*.iso'), ('모든 파일', '*.*')])
        if path:
            source.set(path)
            if not output.get():
                output.set(str(Path(path).with_name('Crazy Taxi 3 (Japan) [Korean V1.0].iso')))

    pick_source = ttk.Button(frame, text='원본 선택', command=choose_source)
    pick_source.grid(row=3, column=1, pady=(6, 16))
    ttk.Label(frame, text='2. 한글 ISO를 저장할 새 경로').grid(row=4, column=0, columnspan=2, sticky='w')
    output_entry = ttk.Entry(frame, textvariable=output)
    output_entry.grid(row=5, column=0, sticky='ew', pady=(6, 16), padx=(0, 8))

    def choose_output():
        path = filedialog.asksaveasfilename(parent=window, title='새 ISO 저장 경로', initialfile='Crazy Taxi 3 (Japan) [Korean V1.0].iso', defaultextension='.iso', filetypes=[('ISO 이미지', '*.iso')])
        if path:
            output.set(path)

    pick_output = ttk.Button(frame, text='저장 경로', command=choose_output)
    pick_output.grid(row=5, column=1, pady=(6, 16))
    ttk.Label(frame, text='원본을 덮어쓰지 않습니다. 인터넷 연결·Python 설치가 필요 없습니다.\n가사 자막: 12개 오디오 / 260개 구간. 미확인 구간은 README를 확인하세요.', style='Small.TLabel').grid(row=6, column=0, columnspan=2, sticky='w')
    progress = tk.DoubleVar(value=0)
    ttk.Progressbar(frame, maximum=100, variable=progress).grid(row=7, column=0, columnspan=2, sticky='ew', pady=(18, 8))
    status = tk.StringVar(value='원본 선택 → 저장 경로 지정 → 패치 시작')
    ttk.Label(frame, textvariable=status, wraplength=650).grid(row=8, column=0, columnspan=2, sticky='w')
    events = queue.Queue()
    cancellation = threading.Event()
    running = False

    def worker(source_path, output_path):
        try:
            result = apply_patch(source_path, output_path, cancel=cancellation,
                                 notify=lambda label, value: events.put(('progress', (label, value))))
            events.put(('done', result))
        except Exception as error:
            events.put(('error', str(error)))

    def start():
        nonlocal running
        if not source.get().strip() or not output.get().strip():
            messagebox.showerror('파일 선택', '원본 ISO와 새 저장 경로를 지정하세요.', parent=window)
            return
        running = True
        cancellation.clear()
        for widget in (source_entry, output_entry, pick_source, pick_output, start_button):
            widget.configure(state='disabled')
        cancel_button.configure(state='normal')
        threading.Thread(target=worker, args=(source.get().strip(), output.get().strip()), daemon=True).start()

    def drain():
        nonlocal running
        try:
            while True:
                kind, value = events.get_nowait()
                if kind == 'progress':
                    status.set(value[0])
                    progress.set(value[1])
                else:
                    running = False
                    for widget in (source_entry, output_entry, pick_source, pick_output, start_button):
                        widget.configure(state='normal')
                    cancel_button.configure(state='disabled')
                    if kind == 'done':
                        status.set('완료! 결과 SHA-256 검증 통과')
                        messagebox.showinfo('패치 완료', '한글 ISO 생성 및 검증을 마쳤습니다.\n\n' + value['output'], parent=window)
                    else:
                        status.set('작업을 완료하지 못했습니다. 원본은 보존했습니다.')
                        messagebox.showerror('패치 안내', value, parent=window)
        except queue.Empty:
            pass
        window.after(80, drain)

    def close():
        if running:
            cancellation.set()
            status.set('취소 처리 중입니다. 임시 파일을 정리한 뒤 닫아주세요.')
        else:
            window.destroy()

    actions = ttk.Frame(frame)
    actions.grid(row=9, column=0, columnspan=2, sticky='e', pady=(18, 0))
    cancel_button = ttk.Button(actions, text='취소', command=cancellation.set, state='disabled')
    cancel_button.pack(side='left', padx=(0, 8))
    start_button = ttk.Button(actions, text='한글 패치 시작', command=start)
    start_button.pack(side='left')
    window.protocol('WM_DELETE_WINDOW', close)
    window.after(80, drain)
    window.mainloop()


def main():
    parser = argparse.ArgumentParser(description='Crazy Taxi 3 Japan Korean patch V1.0')
    parser.add_argument('--source', type=Path)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--report', type=Path, help='Write a JSON result (useful for windowed EXE).')
    parser.add_argument('--self-test', action='store_true', help='Validate embedded patch and engine hashes.')
    args = parser.parse_args()
    if not args.self_test and args.source is None and args.output is None:
        gui()
        return 0
    report_writable = False
    try:
        if args.report:
            report = args.report.expanduser().resolve()
            if report.exists():
                raise PatchError('보고서 파일이 이미 있습니다. 새 보고서 이름을 지정하세요.')
            if any(path is not None and report == path.expanduser().resolve()
                   for path in (args.source, args.output)):
                raise PatchError('보고서와 ISO의 경로는 달라야 합니다.')
            if not report.parent.is_dir():
                raise PatchError('보고서 저장 폴더가 없습니다.')
            report_writable = True
        if args.self_test:
            result = {'verified': True, 'manifest': verify_payload()}
        elif args.source is not None and args.output is not None:
            result = apply_patch(args.source, args.output)
        else:
            raise PatchError('--source와 --output을 함께 지정하세요.')
        code = 0
    except Exception as error:
        result = {'verified': False, 'error': str(error)}
        code = 1
    encoded = json.dumps(result, ensure_ascii=False, indent=2)
    if report_writable:
        # Also preserve a report/file created by another process after preflight.
        with report.open('x', encoding='utf-8') as stream:
            stream.write(encoded + '\n')
    if sys.stdout:
        print(encoded)
    return code


if __name__ == '__main__':
    raise SystemExit(main())
