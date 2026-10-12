"""Launch Collage in a standalone desktop window."""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from urllib.request import urlopen

import webview

from server import Handler, Server


def webview_storage_path() -> Path:
    """Keep WebView2's profile in a stable, per-user writable folder."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if not local_app_data:
        local_app_data = str(Path.home() / "AppData" / "Local")
    path = Path(local_app_data) / "Collage" / "WebView2"
    path.mkdir(parents=True, exist_ok=True)
    return path


def run_gui_smoke_test(url: str) -> None:
    """Exercise the packaged native window, WebView2 backend, and bundled UI."""
    result: dict[str, str | None] = {"error": None, "title": None}
    window = webview.create_window(
        "Collage smoke test",
        url,
        width=840,
        height=620,
    )

    def on_loaded(loaded_window: webview.Window) -> None:
        try:
            title = loaded_window.evaluate_js("document.title")
            has_controls = loaded_window.evaluate_js(
                "['open', 'pick', 'go', 'unit'].every(id => document.getElementById(id))"
            )
            if str(title).strip().lower() != "collage" or not has_controls:
                raise RuntimeError("desktop smoke test loaded an unexpected page")
            result["title"] = str(title)
        except Exception as error:
            result["error"] = str(error)
        finally:
            loaded_window.destroy()

    def on_timeout() -> None:
        result["error"] = "desktop smoke test timed out waiting for the Collage page"
        window.destroy()

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


def main() -> None:
    # Bind to an OS-assigned loopback port so this app can run alongside the
    # browser version or another desktop instance without port conflicts.
    server = Server(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        if "--smoke-test" in sys.argv[1:] or "--server-smoke-test" in sys.argv[1:]:
            # Exercise the packaged server, native WebView2 window, and UI.
            # The release workflow runs this against the built EXE.
            with urlopen(f"http://127.0.0.1:{port}/", timeout=10) as response:
                page = response.read().decode("utf-8")
                if response.status != 200 or "<!doctype html>" not in page.lower():
                    raise RuntimeError("desktop smoke test could not load the bundled UI")
            with urlopen(f"http://127.0.0.1:{port}/version", timeout=10) as response:
                if response.status != 200 or not response.read():
                    raise RuntimeError("desktop smoke test could not read the server version")
            if "--smoke-test" in sys.argv[1:]:
                run_gui_smoke_test(f"http://127.0.0.1:{port}")
                print("Packaged desktop smoke test passed.")
            else:
                print("Packaged server smoke test passed.")
            return

        webview.create_window(
            "Collage",
            f"http://127.0.0.1:{port}",
            width=1280,
            height=900,
            min_size=(840, 620),
        )
        webview.start(storage_path=str(webview_storage_path()))
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2)


if __name__ == "__main__":
    main()

