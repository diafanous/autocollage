"""Launch Collage in a standalone desktop window."""

from __future__ import annotations

import logging
import os
import sys
import threading
import traceback
from pathlib import Path
from urllib.request import urlopen


def webview_storage_path() -> Path:
    """Keep WebView2's profile in a stable, per-user writable folder."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        local_app_data = str(Path.home() / "AppData" / "Local")
    path = Path(local_app_data) / "Collage" / "WebView2"
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_gui_smoke_test(url: str, webview) -> None:
    """Exercise the packaged native window, WebView2 backend, and bundled UI."""
    result: dict[str, str | None] = {"error": None, "title": None}
    window = webview.create_window(
        "Collage smoke test",
        url,
        width=840,
        height=620,
    )

    def on_loaded() -> None:
        try:
            title = window.evaluate_js("document.title")
            has_controls = window.evaluate_js(
                "['open', 'pick', 'go', 'unit'].every(id => document.getElementById(id))"
            )
            if str(title).strip().lower() != "collage" or not has_controls:
                raise RuntimeError("desktop smoke test loaded an unexpected page")
            result["title"] = str(title)
        except Exception as error:
            result["error"] = str(error)
        finally:
            window.destroy()

    def on_timeout() -> None:
        result["error"] = "desktop smoke test timed out waiting for the Collage page"
        write_smoke_error(result["error"])
        try:
            window.destroy()
        except Exception as error:
            write_smoke_error(f"{result['error']}\nCould not close the test window: {error}")

    window.events.loaded += on_loaded
    timeout = threading.Timer(45, on_timeout)
    timeout.daemon = True
    timeout.start()
    try:
        webview.start(storage_path=str(webview_storage_path()))
    finally:
        timeout.cancel()

    if result["error"]:
        raise RuntimeError(result["error"])
    if result["title"] is None:
        raise RuntimeError("desktop smoke test closed before the Collage page loaded")


def write_smoke_error(message: str | None = None) -> None:
    log_path = os.environ.get("COLLAGE_SMOKE_LOG")
    if not log_path:
        temp_dir = Path(os.environ.get("TEMP", Path.home() / "AppData" / "Local" / "Temp"))
        log_path = str(temp_dir / "Collage-smoke-error.log")
    try:
        Path(log_path).parent.mkdir(parents=True, exist_ok=True)
        detail = message if message is not None else traceback.format_exc()
        Path(log_path).write_text(detail, encoding="utf-8")
    except OSError:
        pass


def configure_smoke_logging(webview) -> None:
    log_path = os.environ.get("COLLAGE_WEBVIEW_LOG")
    if not log_path:
        return

    path = Path(log_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("", encoding="utf-8")
    logger = webview.logger
    for handler in tuple(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
    handler = logging.FileHandler(path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False


def main() -> int:
    server = None
    server_thread = None
    smoke_test = "--smoke-test" in sys.argv[1:]
    server_smoke_test = "--server-smoke-test" in sys.argv[1:]
    try:
        # Keep optional desktop imports inside the handled startup path so a
        # missing WebView2/runtime dependency cannot produce a frozen-app dialog.
        if smoke_test or server_smoke_test:
            os.environ["PYWEBVIEW_LOG"] = "DEBUG"
        import webview
        from server import Handler, Server
        if smoke_test or server_smoke_test:
            configure_smoke_logging(webview)

        # Bind to an OS-assigned loopback port so this app can run alongside the
        # browser version or another desktop instance without port conflicts.
        server = Server(("127.0.0.1", 0), Handler)
        port = server.server_address[1]
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()

        if smoke_test or server_smoke_test:
            with urlopen(f"http://127.0.0.1:{port}/", timeout=10) as response:
                page = response.read().decode("utf-8")
                if response.status != 200 or "<!doctype html>" not in page.lower():
                    raise RuntimeError("desktop smoke test could not load the bundled UI")
            with urlopen(f"http://127.0.0.1:{port}/version", timeout=10) as response:
                if response.status != 200 or not response.read():
                    raise RuntimeError("desktop smoke test could not read the server version")
            if smoke_test:
                run_gui_smoke_test(f"http://127.0.0.1:{port}", webview)
            return 0

        webview.create_window(
            "Collage",
            f"http://127.0.0.1:{port}",
            width=1280,
            height=900,
            min_size=(840, 620),
        )
        webview.start(storage_path=str(webview_storage_path()))
        return 0
    except Exception as error:
        if smoke_test or server_smoke_test:
            write_smoke_error()
            return 1

        message = f"Collage could not start.\n\n{error}"
        try:
            import ctypes

            ctypes.windll.user32.MessageBoxW(0, message, "Collage", 0x10)
        except Exception:
            pass
        return 1
    finally:
        if server:
            if server_thread and server_thread.is_alive():
                server.shutdown()
            server.server_close()
            if server_thread:
                server_thread.join(timeout=2)


if __name__ == "__main__":
    raise SystemExit(main())

