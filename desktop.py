"""Launch Collage in a standalone desktop window."""

from __future__ import annotations

import threading

import webview

from server import Handler, Server


def main() -> None:
    # Bind to an OS-assigned loopback port so this app can run alongside the
    # browser version or another desktop instance without port conflicts.
    server = Server(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    try:
        webview.create_window(
            "Collage",
            f"http://127.0.0.1:{port}",
            width=1280,
            height=900,
            min_size=(840, 620),
        )
        webview.start()
    finally:
        server.shutdown()
        server.server_close()
        server_thread.join(timeout=2)


if __name__ == "__main__":
    main()
