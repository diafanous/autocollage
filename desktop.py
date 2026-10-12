"""Launch Collage in a standalone desktop window."""

from __future__ import annotations

import sys
import threading
from urllib.request import urlopen

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
        if "--smoke-test" in sys.argv[1:]:
            # Exercise the packaged server and its bundled UI without opening
            # a window. The release workflow runs this against the built EXE.
            with urlopen(f"http://127.0.0.1:{port}/", timeout=10) as response:
                page = response.read().decode("utf-8")
                if response.status != 200 or "<!doctype html>" not in page.lower():
                    raise RuntimeError("desktop smoke test could not load the bundled UI")
            with urlopen(f"http://127.0.0.1:{port}/version", timeout=10) as response:
                if response.status != 200 or not response.read():
                    raise RuntimeError("desktop smoke test could not read the server version")
            return

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
