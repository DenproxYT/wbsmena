#!/usr/bin/env python3
"""
Десктоп-обёртка PVZ Automation на PyWebView.
Запускает Django-сервер в фоне и открывает приложение в нативном окне.

Запуск: дважды нажмите на run_desktop.bat (в этой же папке)
  или: python run_desktop.py

На Windows нужны:
  - WebView2 (обычно уже есть в Windows 10/11)
  - пакет cffi (pip install -r requirements.txt)
"""
import os
import sys
import subprocess
import time
import atexit

# Важно: переходим в папку backend (где лежит run_desktop.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
os.chdir(BASE_DIR)

PORT = 8765
URL = f"http://127.0.0.1:{PORT}/"

_process = None
_log_file = None


def wait_for_server(timeout=30):
    """Ожидание готовности сервера."""
    import urllib.request
    for i in range(int(timeout * 10)):
        try:
            with urllib.request.urlopen(URL, timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.1)
    return False


def kill_server():
    """Остановка Django-сервера при выходе."""
    global _process, _log_file
    if _process is not None and _process.poll() is None:
        _process.terminate()
        try:
            _process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            _process.kill()
        _process = None
    if _log_file is not None:
        try:
            _log_file.close()
        except Exception:
            pass


def main():
    global _process, _log_file

    # Лог Django в файл (для отладки белого экрана)
    log_path = os.path.join(BASE_DIR, "run_desktop.log")
    try:
        _log_file = open(log_path, "w", encoding="utf-8")
    except Exception:
        _log_file = None

    _out = _log_file if _log_file else subprocess.DEVNULL
    _process = subprocess.Popen(
        [sys.executable, "manage.py", "runserver", f"127.0.0.1:{PORT}", "--noreload", "--nothreading"],
        cwd=BASE_DIR,
        stdout=_out,
        stderr=subprocess.STDOUT if _log_file else subprocess.DEVNULL,
        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if sys.platform == "win32" else 0,
    )

    atexit.register(kill_server)

    if not wait_for_server():
        msg = f"Ошибка: сервер не запустился за 30 сек. Проверьте {log_path}"
        print(msg, file=sys.stderr)
        kill_server()
        sys.exit(1)

    # Небольшая пауза для полной инициализации сервера
    time.sleep(0.5)

    import webview

    # Встроенная страница загрузки — показывается сразу (без сети), затем переход на сервер
    loading_html = f'''<!DOCTYPE html><html><head><meta charset="utf-8"><meta http-equiv="refresh" content="2;url={URL}"></head>
<body style="margin:0;display:flex;flex-direction:column;align-items:center;justify-content:center;min-height:100vh;background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#4f46e5 100%);color:#fff;font-family:system-ui,sans-serif;">
<div style="width:56px;height:56px;border:4px solid rgba(255,255,255,0.3);border-top-color:#fff;border-radius:50%;animation:sp 0.8s linear infinite;"></div>
<div style="margin-top:1.5rem;font-weight:700;font-size:1.25rem;">Смена WB</div>
<div style="margin-top:0.5rem;opacity:0.9;">Загрузка...</div>
<style>@keyframes sp{{to{{transform:rotate(360deg)}}}}</style>
</body></html>'''

    icon_path = os.path.join(BASE_DIR, 'static', 'icon.ico')
    window = webview.create_window(
        title="Смена WB",
        html=loading_html,
        width=1280,
        height=800,
        min_size=(800, 600),
        resizable=True,
        background_color="#6366f1",
    )

    kwargs = {"debug": False}
    if "PYWEBVIEW_GUI" in os.environ:
        kwargs["gui"] = os.environ["PYWEBVIEW_GUI"]
    elif sys.platform == "win32":
        kwargs["gui"] = "edgechromium"
    icon_path = os.path.join(BASE_DIR, "static", "icon.ico")
    if os.path.exists(icon_path):
        kwargs["icon"] = icon_path
    webview.start(**kwargs)
    kill_server()


if __name__ == "__main__":
    main()
