"""Run once to answer the setup questions; run again to reopen your ad gallery."""
import argparse
import functools
import http.server
import json
import os
from pathlib import Path
import sys
import webbrowser

ROOT = Path(__file__).resolve().parent
STATE = ROOT / '.ad-engine' / 'active.json'


def activate_local_environment():
    local = ROOT / '.venv' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if local.exists() and Path(sys.prefix).resolve() != (ROOT / '.venv').resolve():
        os.execv(str(local), [str(local), str(Path(__file__).resolve()), *sys.argv[1:]])


def saved_project():
    if not STATE.exists():
        return None
    try:
        value = json.loads(STATE.read_text(encoding='utf-8'))['project']
        project = (ROOT / value).resolve()
        if project.is_dir() and (project / 'brand.json').is_file():
            return project
    except (OSError, ValueError, KeyError, TypeError):
        pass
    print('ไม่พบโปรเจกต์ที่บันทึกไว้ เริ่มตั้งค่าใหม่ได้เลย')
    return None


def remember(project):
    STATE.parent.mkdir(parents=True, exist_ok=True)
    # Only this app-owned pointer is replaced. Business project files are never overwritten.
    value = os.path.relpath(Path(project).resolve(), ROOT.resolve())
    temp = STATE.with_suffix('.tmp')
    temp.write_text(json.dumps({'project': value}, ensure_ascii=False), encoding='utf-8')
    temp.replace(STATE)


def serve(project, port, open_browser=True):
    import student
    from datetime import datetime
    out = ROOT / 'builds' / datetime.now().strftime('guided-%Y%m%d-%H%M%S-%f')
    student.build_project(project, out)
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(out))
    # Try adjacent ports if a previous preview is still open. Never stop another server.
    for candidate in range(port, min(port + 20, 65536)):
        try:
            server = http.server.ThreadingHTTPServer(('127.0.0.1', candidate), handler)
            break
        except OSError as exc:
            if exc.errno not in (48, 98, 10048):
                raise
    else:
        raise ValueError('No available port; use --port with another number')
    with server:
        url = f'http://localhost:{server.server_port}'
        print('\nเปิดคลังแอด: ' + url, flush=True)
        print('ไฟล์ที่คุณแก้ได้: ' + str(project), flush=True)
        print('Ctrl+C เพื่อหยุด แก้ไฟล์แล้วรัน python3 start.py ใหม่เพื่อดูการเปลี่ยนแปลง', flush=True)
        print('สร้างอีกแบรนด์: python3 start.py --new', flush=True)
        if open_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass


def main(argv=None):
    if sys.version_info < (3, 11):
        print('Please install Python 3.11 or newer.'); return 1
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--new', action='store_true', help='Set up another brand, preserving the previous one')
    parser.add_argument('--project', help='Reopen an existing editable project folder')
    parser.add_argument('--setup-only', action='store_true', help='Save the project without starting the server')
    parser.add_argument('--no-browser', action='store_true')
    parser.add_argument('--port', type=int, default=8767)
    args = parser.parse_args(argv)
    if args.new and args.project:
        parser.error('Choose either --new or --project')
    if not 1024 <= args.port <= 65535:
        parser.error('--port must be 1024–65535')
    try:
        import PIL  # dependency preflight before asking questions
    except ImportError:
        print('ติดตั้งก่อนด้วย python3 install.py (Windows: py install.py)'); return 1
    import onboarding
    import student
    try:
        project = Path(args.project).expanduser().resolve() if args.project else (None if args.new else saved_project())
        if project is None:
            answer = onboarding.interview()
            if answer is None:
                print('ยกเลิกแล้ว ยังไม่ได้บันทึกโปรเจกต์'); return 0
            project = onboarding.create_project(*answer, onboarding.new_project_path())
            print('\nสร้างภาพและแคปชั่นร่าง 3 ชิ้นแล้ว ไม่ได้ใช้ AI หรือ scrape', flush=True)
        student.load_site(project)
        student.prepare(project)
        remember(project)
        print('โปรเจกต์: ' + str(project), flush=True)
        print('บริบทและแผนสำหรับ AI: creative-brief.json (ไฟล์บริบทยังไม่ได้ถูกวิเคราะห์)', flush=True)
        print('รายชื่อ reference: watchlist.json — ยังไม่ได้เก็บแอด', flush=True)
        if not args.setup_only:
            serve(project, args.port, not args.no_browser)
        return 0
    except (EOFError, KeyboardInterrupt):
        print('\nหยุดการตั้งค่า ยังไม่เปลี่ยนโปรเจกต์เดิม'); return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print('เปิดโปรเจกต์ไม่สำเร็จ:', exc); return 1


if __name__ == '__main__':
    activate_local_environment()
    raise SystemExit(main())
